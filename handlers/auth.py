# -*- coding: utf-8 -*-

import logging
import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


import states as st
import keyboards as kb

from config import URL, LOGIN, PASS
from app import dp, bot
from handlers import client

### 
from database.DB1C import Database_1C
from database import sqlDB
from test_db import users

logging.basicConfig(level=logging.INFO)


### ввод логина
async def auth_login(call: types.CallbackQuery,  state: FSMContext):
    msg = await call.message.answer('Для входа в систему введите логин', reply_markup=kb.cancel_kb)
    await st.AuthStates.auth_login_st.set()    
    await state.update_data(auth_msgID = msg.message_id)
    
### проверка логина и ввод пароля
async def login_entered(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user: sqlDB.User = sqlDB.User.basic_auth(chat_id = message.from_user.id)
    print(user)
    
    if isinstance(user, sqlDB.User):
        await bot.edit_message_text(text='Пользователь найден в базе данных.',  chat_id = message.chat.id,message_id = user_data['auth_msgID'])
        await state.reset_state(with_data=False)
        await asyncio.sleep(1)
        await bot.delete_message(chat_id = message.chat.id,message_id = user_data['auth_msgID'])
        
    else:
        await state.update_data(login=message.text)  
        await bot.edit_message_text(text='Введите пароль',  chat_id = message.chat.id,message_id = user_data['auth_msgID'], reply_markup=kb.cancel_kb)
        await st.AuthStates.next()
    
    await message.delete()

    

### проверка пароля
async def auth_pass(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    login_db = user_data['login']
    password  = message.text
    
    await message.delete()

    if login_db in users: #TODO удалить в продакшене
        new_user = sqlDB.User(chat_id=message.from_user.id, login = user_data['login'])
        new_user.save()
        login_db = new_user.login_db
        password = new_user.password

 
    if Database_1C(URL, login_db, password).ping():
        new_user = sqlDB.User.create(chat_id=message.from_user.id, 
                                    login = user_data['login'],
                                    password = password,
                                    login_db=login_db)
        new_user.save()

        await bot.edit_message_text(text='Вход выполнен.',  chat_id = message.chat.id, message_id = user_data['auth_msgID'])
        await asyncio.sleep(2)
        await bot.delete_message(chat_id = message.chat.id,message_id = user_data['auth_msgID'])
        await bot.edit_message_reply_markup(chat_id = message.from_user.id,
                                            message_id = user_data['start_msgID'],
                                            reply_markup=kb.StartMenu(mode='change'))


    else:
        txt = "Неверный логин или пароль. Повторите ввод или обратитесь к администратору."
        await bot.edit_message_text(text=txt,  chat_id = message.chat.id,message_id = user_data['auth_msgID'])
        await asyncio.sleep(3)
        await bot.delete_message(chat_id = message.chat.id,message_id = user_data['auth_msgID'])

    
    await state.reset_state(with_data=False)
 

async def user_change(call: types.CallbackQuery, state: FSMContext):   
    
    user: sqlDB.User = sqlDB.User.basic_auth(chat_id = call.from_user.id)
    user.delete_instance()
    
    user_data = await state.get_data()
    await bot.answer_callback_query(call.id, text='Выход выполнен', show_alert=True)
    await bot.edit_message_reply_markup(chat_id = call.from_user.id,
                                            message_id = user_data['start_msgID'],
                                            reply_markup=kb.StartMenu())       
    
def reg_handlers_auth(dp : Dispatcher):

    ### авторизация    
    dp.register_callback_query_handler(auth_login,  Text(contains=('auth'), ignore_case=True), state="*")
    dp.register_message_handler(login_entered, state=st.AuthStates.auth_login_st)
    dp.register_message_handler(auth_pass, state=st.AuthStates.login_entered_st)
    dp.register_callback_query_handler(user_change,  Text(contains=('uchange'), ignore_case=True), state="*")
    