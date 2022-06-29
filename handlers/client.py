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
from database.sqlite_db import database as db
from test_db import test_DB, full_list




logging.basicConfig(level=logging.INFO)




# functions_dict = {'level1' : await command_start, 
#                   'level2' : await full_list_move, 
#                   'level3' : await }





    
### команда для старта
async def command_start(message : types.Message, state: FSMContext):
    msg_text = text(hbold('Добро пожаловать!'),'\n','Выберите действие:',sep='')
    msg = await message.answer (msg_text, reply_markup=kb.StartMenu())
    await state.update_data(start_msgID=msg.message_id)
    

## выбор всех задач
async def back_start(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    user_data = await state.get_data() 
    msg_text = text(hbold('Добро пожаловать!'),'\n','Выберите действие:',sep='')
    await bot.edit_message_text(text=msg_text, 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=kb.StartMenu())   


## выбор всех задач
async def full_list_move(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await bot.edit_message_text(text=text(hbold('Доступные фильтры:')), 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=kb.FiltersMenu()) 
    
async def back_to_filteres (call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await full_list_move (call, state)
    
    
    # user_data = await state.get_data()
    # await bot.edit_message_text(text=text(bold('Доступные фильтры:')), 
    #                     chat_id = call.from_user.id,
    #                     message_id = user_data['start_msgID'],
    #                     reply_markup=kb.FiltersMenu())) 


async def full_list_taskd(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    from datetime import datetime as dt

    text_mode = {'FULL' : {'text' : text(hbold('Все задачи:')), 'params' : {}},
                 'USER' : {'text' : text(hbold('Мои задачи:')), 'params' : {}},
                 'FREE' : {'text' : text(hbold('Свободные задачи:')), 'params' : {'Accepted' : 'no'}},
                 'PAST' : {'text' : text(hbold('Просроченные задачи:')), 
                           'params' : {'DateBegin': '00010000000000', 
                                       'DateEnd'  : dt.now().strftime('%Y%m%d%H%M%S'), 
                                       'Executed' : 'no'}}}
   
    user_data = await state.get_data()
    
    if (callback_data['ACTION'] == 'BACK')|(callback_data['ACTION'] == 'PAGE'):
        mode = user_data['filter_mode']
    
    else:
        mode = callback_data['ACTION'] 
        await state.update_data(filter_mode=mode)
    
    page = int(callback_data['PAGE'])    
    msg_text = text_mode[mode]['text']
    
    if DEBUG_MODE:
        dataDB = test_DB      
    else:
        dataDB = db_1c.tasks(text_mode[mode]['params'])
   
    await bot.edit_message_text(text=msg_text, 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=kb.TasksMenu(data = dataDB, page=page))       



### выбор описания задачи  
# @dp.callback_query_handler(kb.TasksMenu.CallbackData.TASKS_CB.filter(ACTION=["TASK"]))
async def send_task_info(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    from datetime import datetime as dt
    
    taskID = callback_data['TASK_ID']
    await state.update_data(taskID=taskID)
    
    
    if DEBUG_MODE:
        dataDB = test_DB[taskID]       
    else:
        dataDB = db_1c.tasks(params={'id' : taskID})[taskID] 


        
    date_task = dt.strptime(dataDB[taskID]['Дата'], '%Y%m%d%H%M%S').strftime('%d/%m/%Y') # %d.%m.%Y %H:%M:%S

    if dataDB[taskID]['Наименование'][:2]==' (':
        task_descr = dataDB[taskID]['Наименование'][2:-1]
    else:
        task_descr = dataDB[taskID]['Наименование']
    
    
    task_message = text(hbold(dataDB[taskID]['Номер']), ' от ', date_task, '\n',
                        task_descr, '\n',
                        '\n',
                        hbold('Клиент: '), (dataDB[taskID]['CRM_Партнер']), '\n',
                        '\n',
                        hbold('Описание: '),'\n',
                        (dataDB[taskID]['Описание']), '\n',
                        '\n',
                        hbold('Исполнение: '), (dataDB[taskID]['Исполнитель']), '\n',
                        (dataDB[taskID]['РезультатВыполнения']),
                        sep='')

    user_data = await state.get_data()
    await bot.edit_message_text(text=task_message, 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=kb.TaskActionMenu(accepted=dataDB[taskID]['ПринятаКИсполнению']))    


    
async def back_vars(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    taskID = user_data['taskID']
    
    if DEBUG_MODE:
        dataDB = test_DB[taskID]       
    else:
        dataDB = db_1c.tasks(params={'id' : taskID})           
    await bot.edit_message_reply_markup(chat_id = call.from_user.id,
                                  message_id = call.message.message_id,
                                  reply_markup=kb.TaskActionMenu(accepted=dataDB[taskID]['ПринятаКИсполнению']))

    


async def echo_send(message : types.Message):
    msg = await message.answer ('Нет такой команды')
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg.message_id)
    await message.delete()



    
def reg_handlers_client(dp : Dispatcher):
    
    
    dp.register_message_handler(command_start, commands=['start'])
    
    dp.register_callback_query_handler(back_start,        kb.FiltersMenu.CallbackData.FILTER_CB.filter(ACTION=["BACK"]))
    dp.register_callback_query_handler(full_list_move,    kb.StartMenu.CallbackData.START_CB.filter(ACTION=["SHOWTASKS"]))
    dp.register_callback_query_handler(back_to_filteres,  kb.TasksMenu.CallbackData.TASKS_CB.filter(ACTION=["BACK"]))


    dp.register_callback_query_handler(full_list_taskd, kb.FiltersMenu.CallbackData.FILTER_CB.filter(ACTION=['FULL','USER','FREE','PAST']))  
    dp.register_callback_query_handler(full_list_taskd, kb.TasksMenu.CallbackData.TASKS_CB.filter(ACTION=["PAGE"]))  
    dp.register_callback_query_handler(send_task_info, kb.TasksMenu.CallbackData.TASKS_CB.filter(ACTION=["TASK"]))

    # dp.register_callback_query_handler(accept_task, Text(startswith="accept_task"))
    # dp.register_callback_query_handler(decline_task, Text(startswith="decline_task"))
    

    # ### комментарий
    # dp.register_callback_query_handler(comment, Text(startswith="comment"), state="*")
    # dp.register_message_handler(save_comment, state=st.CommentStates.add_comment)
    # dp.register_callback_query_handler(del_comment,  Text(startswith="cancel_b"), state=st.UploadPhotoState.add_photo)

 
    # dp.register_callback_query_handler(show_options, Text(startswith="show_"))
    dp.register_callback_query_handler(back_vars, Text(startswith="backvar"))

    
    dp.register_message_handler(echo_send)

