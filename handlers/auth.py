# -*- coding: utf-8 -*-

import logging
import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from cryptography.fernet import Fernet


import states as st
import keyboards as kb

from load_bot import bot, dp

### 
from database.DB1C import Database_1C
from database import sqlDB

# logging.basicConfig(level=logging.INFO)


### ввод логина
async def auth_login(call: types.CallbackQuery,  state: FSMContext):
    logging.info(f"{call.from_user.id} - auth login")
    msg = await call.message.answer('Для входа в систему введите логин', reply_markup=kb.cancel_kb)
    await st.AuthStates.auth_login_st.set()    
    await state.update_data(auth_msgID = msg.message_id)
    
### проверка логина и ввод пароля
async def login_entered(message: types.Message, state: FSMContext):
    logging.info(f"{message.from_user.id} -login entered - {message.text}")

    user_data = await state.get_data()
    user: sqlDB.User = sqlDB.User.basic_auth(chat_id = message.from_user.id)
    
    if isinstance(user, sqlDB.User):
        logging.info(f"{message.from_user.id} - auth successful - {user}")
        
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
    logging.info(f"{message.from_user.id} - auth password")

    
    user_data = await state.get_data()
    await message.delete()
    
    login_db = user_data['login']
    password  = message.text
        
    if Database_1C(login_db, password, auth=True).ping() == None:
        from config import DATABASE_SQL
        
        cipher = Fernet(DATABASE_SQL.key) 
        password = cipher.encrypt(password.encode('utf-8')).decode('utf-8')
        
        names_1C = sqlDB.Users1C.select().dicts()
        
        for row in names_1C:
            name = 'NA'
            name_fio = row['login'].split(' ')
            
            if len(name_fio) == 3:
                name_fio = name_fio[0] + name_fio[1][:1] + name_fio[2][:1]
            else:
                name_fio = row['login']
            
            print(name_fio)
            if login_db.lower() == name_fio.lower():
                name = row['login']
                break
                
        

        new_user = sqlDB.User.create(chat_id=message.from_user.id, 
                                    login_db=login_db.lower(),
                                    password = password,
                                    name_1C =name )
        new_user.save()
        logging.info(f"{message.from_user.id} - auth successful")

        await bot.edit_message_text(text='Вход выполнен.',  chat_id = message.chat.id, message_id = user_data['auth_msgID'])
        await asyncio.sleep(2)
        await bot.delete_message(chat_id = message.chat.id,message_id = user_data['auth_msgID'])
        await bot.edit_message_reply_markup(chat_id = message.from_user.id,
                                            message_id = user_data['start_msgID'],
                                            reply_markup=kb.StartMenu(mode='change'))
    else:
        logging.warning(f"{message.from_user.id} - auth invalid data")
        txt = "Неверный логин или пароль. Повторите ввод или обратитесь к администратору."
        await bot.edit_message_text(text=txt,  chat_id = message.chat.id,message_id = user_data['auth_msgID'])
        await asyncio.sleep(3)
        await bot.delete_message(chat_id = message.chat.id,message_id = user_data['auth_msgID'])
 
    await state.reset_state(with_data=False)
 

async def user_change(call: types.CallbackQuery, state: FSMContext):   
    logging.info(f"{call.from_user.id} - user change")
    
    user: sqlDB.User = sqlDB.User.basic_auth(chat_id = call.from_user.id)
    user.delete_instance()
    
    user_data = await state.get_data()
    await bot.answer_callback_query(call.id, text='Выход выполнен', show_alert=True, cache_time=10000)
    await bot.edit_message_reply_markup(chat_id = call.from_user.id,
                                            message_id = user_data['start_msgID'],
                                            reply_markup=kb.StartMenu())       
    
def reg_handlers_auth(dp : Dispatcher):

    ### авторизация    
    dp.register_callback_query_handler(auth_login,  Text(contains=('auth'), ignore_case=True), state="*")
    dp.register_message_handler(login_entered, state=st.AuthStates.auth_login_st)
    dp.register_message_handler(auth_pass, state=st.AuthStates.login_entered_st)
    dp.register_callback_query_handler(user_change,  Text(contains=('uchange'), ignore_case=True), state="*")
    