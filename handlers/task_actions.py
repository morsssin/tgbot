# -*- coding: utf-8 -*-

import re
import logging
import asyncio
import requests
import datetime as dt

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


from aiogram.utils.markdown import text, hbold

# from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,
#                                       MessageToDeleteNotFound)
import states as st
import keyboards as kb

from config import LEN_TASKS, URL, LOGIN, PASS, DEBUG_MODE
from app import dp, bot


### 
from database.db_1c import db_1c
# from database.sqlite_db import database as db
from test_db import test_DB, full_list




logging.basicConfig(level=logging.INFO)




### выполненные работы


async def add_work_done (call: types.CallbackQuery(),  state: FSMContext):
    await call.message.answer('Выберите вариант для поиска', reply_markup=kb.add_work_done_kb)
    await st.ToolsStates.find_work_done.set()

async def search_handler(query: types.InlineQuery, state: FSMContext):  
    
    if query.query.split(':')[0] == 'tasks':
        result_list = search_in_list(tdb.works_list, query.query.split(':')[1])

        
    elif query.query.split(':')[0] == 'tools':
        result_list = search_in_list(tdb.tools_list, query.query.split(':')[1])

    articles = [types.InlineQueryResultArticle(id=idx,
                                               title=item,
                                               input_message_content=types.InputTextMessageContent(message_text="%s" % item),
                                               reply_markup = kb.accept_work_done_kb
    ) for idx, item in enumerate(result_list)]
    await query.answer(articles, cache_time=60, is_personal=True)
        
      
async def save_work_done(call: types.CallbackQuery,  state: FSMContext):
    if call.data.split('_')[1] == 'accepted':
        await bot.answer_callback_query(call.id, text='Вариант добавлен', show_alert=True)
                  
    elif call.data.split('_')[1] == 'declined':   
        await bot.answer_callback_query(call.id, text='Вариант отклонен', show_alert=True)
        
        


###  вывести дополнительные варианты
async def show_options(call: types.CallbackQuery, state: FSMContext):
    mode = call.data.split("_")[1]
    
    if mode == 'vars':
        task_actions_var_kb = types.InlineKeyboardMarkup(row_width=2)

        for i, var in enumerate(tdb.actions_var_list):
            task_actions_var_kb.insert(types.InlineKeyboardButton(var, callback_data='varb_%s' % i))
        back_var__button = types.InlineKeyboardButton('◀️ Назад', callback_data='backvar')
        task_actions_var_kb.insert(back_var__button)
    elif mode == 'morevars':
        task_actions_var_kb = kb.more_options_kb 
    await bot.edit_message_reply_markup(chat_id = call.from_user.id,
                                     message_id = call.message.message_id,
                                     reply_markup=task_actions_var_kb)    
        

async def state_var(call: types.CallbackQuery,  state: FSMContext):
    mode = call.data.split("_")[1]
    txt = tdb.actions_var_list[int(mode)].replace('.', '\.')
    user_data = await state.get_data()

    msg_txt = 'Подтвердите присвоение задаче {0} статуста "{1}"'.format(user_data['taskID'], txt)
    await call.message.answer(msg_txt, reply_markup=kb.option_kb)

async def state_var_accept(call: types.CallbackQuery,  state: FSMContext):
    await bot.answer_callback_query(call.id, text='Вариант сохранен', show_alert=True)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)


    
def reg_handlers_client(dp : Dispatcher):


    ### список задач
    

    # ### комментарий
    # dp.register_callback_query_handler(comment, Text(startswith="comment"), state="*")
    # dp.register_message_handler(save_comment, state=st.CommentStates.add_comment)
    # dp.register_callback_query_handler(del_comment,  Text(startswith="cancel_b"), state=st.UploadPhotoState.add_photo)


    ### добавить пользователя
    dp.register_callback_query_handler(add_user, Text(startswith="adduser_"))
    dp.register_callback_query_handler(choose_user, Text(startswith="user_"))
    dp.register_callback_query_handler(send_notification, Text(startswith="users_invite"))
    dp.register_callback_query_handler(tasksend_reply, Text(startswith="tasksend_"))


     ### добавить фото/видео
    dp.register_callback_query_handler(del_comment,  Text(startswith="cancel_b"), state=st.CommentStates.add_comment)


    ### выполненные работы
    dp.register_callback_query_handler(add_work_done, Text(startswith="todowork"), state="*")
    dp.register_inline_handler(search_handler, state=st.ToolsStates.find_work_done)
    dp.register_callback_query_handler(save_work_done, Text(startswith="work_"), state=st.ToolsStates.find_work_done)


    ### свернуть задачу
    dp.register_callback_query_handler(hide_message,Text(startswith="hide_message"))
    dp.register_callback_query_handler(hide_message,Text(startswith="hide_message"), state=st.ToolsStates.find_work_done) 

    ### выбрать вариант
    dp.register_callback_query_handler(state_var, Text(startswith="varb_")) 
    dp.register_callback_query_handler(state_var_accept, Text(startswith="accept_b"))
    
 
    dp.register_callback_query_handler(show_options, Text(startswith="show_"))
    dp.register_callback_query_handler(back_vars, Text(startswith="backvar"))

    