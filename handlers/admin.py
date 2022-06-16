from  emoji import emojize
import asyncio
from aiogram import types, Dispatcher
from create_bot import dp, bot, URL, PASS, LOGIN
import keyboards as kb
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import text, bold, italic, code, pre, escape_md
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,
                                      MessageToDeleteNotFound)

from urllib import request
from requests.auth import HTTPBasicAuth
import requests
import pandas as pd
import datetime as dt

users = ['admin', 'admin1', 'client']    
users_pass = {'admin':'pass', 'admin1': 'password', 'client':'password'}
users_chat_id = {'admin':'', 'admin1': '', 'client':''}

class AuthStates(StatesGroup):
    auth_login_st = State()
    login_entered_st = State()
    auth_pass_st = State()

###  ДЕРЕВО СОСТОЯНИЙ ###

### ввод логина
async def auth_login(call: types.CallbackQuery,  state: FSMContext):
    msg = await call.message.answer('Для входа в систему введите логин')
    await AuthStates.auth_login_st.set()    
    await state.update_data(auth_msgID = msg.message_id)
    
### проверка логина и ввод пароля
async def login_entered(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text.lower() not in users:
        text_ = "Пользователь не найден в базе данных\. Пожалуйста, проверьте правильность ввода или обратитесь к администратору\."
        await bot.edit_message_text(text=text_,  chat_id = message.chat.id,message_id = user_data['auth_msgID'])   
        return
    await state.update_data(entered_login=message.text.lower())
    # await AuthStates.next()
    await state.reset_state(with_data=False)
    text_ = "Пользователь найден в базе данных\. ID чата:{}\.".format(message.chat.id)
    await bot.edit_message_text(text=text_,  chat_id = message.chat.id,message_id = user_data['auth_msgID'])
    users_chat_id[message.text.lower()] = message.chat.id
    await asyncio.sleep(2)
    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=user_data['auth_msgID'])


### проверка пароля
async def auth_pass(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text.lower() != users_pass[user_data['entered_login']]:
        await message.answer("Неверный пароль\. Повторите ввод или обратитесь к администратору\.")
        await message.delete()
        return
    # await message.answer("Вход выполнен.")
    await message.delete()
    
    await bot.send_message(message.from_user.id, "Вход выполнен. ID чата:{}. Можно переходить к списку задач.".format(message.from_user.chat_id),  reply_markup=kb.auth_kb_yes)
    await state.reset_state(with_data=False)
    # await AuthStates.next()
    
    
    
def reg_handlers_client(dp : Dispatcher):


    ### авторизация    
    dp.register_callback_query_handler(auth_login, Text(startswith="auth"), state="*")
    # dp.register_message_handler(auth_login, Text(equals="авторизация", ignore_case=True), state="*")
    dp.register_message_handler(login_entered, state=AuthStates.auth_login_st)
    # dp.register_message_handler(auth_pass, state=AuthStates.login_entered_st)