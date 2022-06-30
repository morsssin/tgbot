# -*- coding: utf-8 -*-

import logging
import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

# from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,
#                                       MessageToDeleteNotFound)
import states as st
import keyboards as kb

from config import URL, LOGIN, PASS
from app import dp, bot

### 
from database.DB1C import Database_1C
from database.sqlite_db import database as db
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
    
    if await db.get_user_data(message.from_user.id, 'login') == message:
        await bot.edit_message_text(text='Пользователь найден в базе данных.',  chat_id = message.chat.id,message_id = user_data['auth_msgID'])
        await state.reset_state(with_data=False)
        await asyncio.sleep(1)
        await bot.delete_message(chat_id = message.chat.id,message_id = user_data['auth_msgID'])
        
    else:
        await state.update_data(login=message.text)  
        await bot.edit_message_text(text='Введите пароль',  chat_id = message.chat.id,message_id = user_data['auth_msgID'])
        await st.AuthStates.next()
        await asyncio.sleep(1)
    
    await message.delete()

    

### проверка пароля
async def auth_pass(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    login_db = user_data['login']
    password  = message.text
    
    await message.delete()

    if login_db in users:
        login_db = LOGIN
        password = PASS
 
    if Database_1C(URL, login_db, password).ping():
        
        user_data = {'chatID'   : message.from_user.id,
                     'login'    : user_data['login'],
                     'password' : password,
                     'login_db' : login_db}
   
        await db.add_user_data(data=user_data)
        await bot.edit_message_text(text='Вход выполнен.',  chat_id = message.chat.id,message_id = user_data['auth_msgID'])
        await asyncio.sleep(1)
        await bot.delete_message(chat_id = message.chat.id,message_id = user_data['auth_msgID'])

    else:
        txt = "Неверный логин или пароль. Повторите ввод или обратитесь к администратору."
        await bot.edit_message_text(text=txt,  chat_id = message.chat.id,message_id = user_data['auth_msgID'])
        await asyncio.sleep(1)
        return
    
    await state.reset_state(with_data=False)
        
    
def reg_handlers_auth(dp : Dispatcher):

    ### авторизация    
    dp.register_callback_query_handler(auth_login,  Text(contains=('auth'), ignore_case=True), state="*")
    dp.register_message_handler(login_entered, state=st.AuthStates.auth_login_st)
    dp.register_message_handler(auth_pass, state=st.AuthStates.login_entered_st)
    