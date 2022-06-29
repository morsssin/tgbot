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



### принять задачу
async def accept_task(call: types.CallbackQuery, state: FSMContext):
    
    ## to do: отправка принятия задачи в БД

    await bot.answer_callback_query(call.id, text='Задача принята')
    await bot.edit_message_reply_markup(chat_id = call.from_user.id,
                                     message_id = call.message.message_id,
                                     reply_markup=kb.task_actions_kb_accepted)

async def decline_task(call: types.CallbackQuery, state: FSMContext):

    ## to do: отправка ОТМЕНЫ задачи в БД
    await bot.answer_callback_query(call.id, text='Задача отменена')
    await bot.edit_message_reply_markup(chat_id = call.from_user.id,
                                     message_id = call.message.message_id,
                                     reply_markup=kb.task_actions_kb)
    
   
### ввести комментарий и сохранить
async def comment(call: types.CallbackQuery, state: FSMContext):
    msg = await call.message.answer('Введите коментарий:', reply_markup=kb.cancel_kb)
    await state.update_data(comment_id = msg.message_id)
    await st.CommentStates.add_comment.set()

async def save_comment(message: types.Message, state: FSMContext):
    user_data = await state.get_data()  
    
    # len_comm = len(test_DB[user_data['taskID']]['COMMENTS'])
    # test_DB[user_data['taskID']]['COMMENTS']['User {0}'.format(len_comm + 1)] = message.text
    msg = await message.answer('Комментарий сохранен')
       
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg.message_id)
    await bot.delete_message(chat_id=message.from_user.id, message_id=user_data['comment_id'])
    await message.delete()
    
    taskID = user_data['taskID']
    
    req = requests.get(URL + '/ERP/hs/tg_bot/tasks', auth=HTTPBasicAuth(LOGIN, PASS))
    dataDB = req.json()
    date_task = dt.datetime.strptime(dataDB[taskID]['Дата'], '%d.%m.%Y %H:%M:%S').strftime('%d/%m/%Y')
  
    
  
    
    # comments_txt = ''
    # for idx, (key, val) in enumerate(test_DB[taskID]['COMMENTS'].items()):
    #     txt = text(bold(key), ': ', escape_md(val), '\n', sep='')
    #     comments_txt = text(comments_txt, txt, sep='')      

    if dataDB[taskID]['Наименование'][:2]==' (':
        task_descr = dataDB[taskID]['Наименование'][2:-1]
    else:
        task_descr = dataDB[taskID]['Наименование']
    

    task_message = text(bold(escape_md(dataDB[taskID]['Номер'])), ' от ', escape_md(date_task), '\n',
                        escape_md(task_descr), '\n',
                        '\n',
                        bold('Клиент: '), escape_md(dataDB[taskID]['CRM_Партнер']), '\n',
                        '\n',
                        bold('Описание: '),'\n',
                        escape_md(dataDB[taskID]['Описание']), '\n',
                        '\n',
                        bold('Исполнение: '), escape_md(dataDB[taskID]['Исполнитель']), '\n',
                        escape_md(dataDB[taskID]['РезультатВыполнения']),
                        sep='')
            
    
    # task_message = text(task_message.replace('.', '\.'), '\n',
    #                     '\n',
    #                     bold('Комментарии:'),'\n',
    #                     comments_txt, sep='')
    # print(comments_txt)
    # print(task_message)
       
    if dataDB[taskID]['ПринятаКИсполнению'] == 'Да':
        keyboard = kb.task_actions_kb_accepted
        
    elif dataDB[taskID]['ПринятаКИсполнению'] == 'Нет':
        keyboard = kb.task_actions_kb
    
    await bot.edit_message_text(text=task_message, 
                        chat_id = message.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=keyboard)    

    await state.reset_state(with_data=False)


### добавить фото/видео



async def uploadPhoto(call: types.CallbackQuery, state: FSMContext):
    msg = await call.message.answer('Добавьте фото или видео:', reply_markup=kb.cancel_kb)
    await state.update_data(photo_msgID = msg.message_id)
    await st.UploadPhotoState.add_photo.set()



@dp.message_handler(content_types=["photo"], state=st.UploadPhotoState.add_photo)
async def savePhoto(message: types.Message,  state: FSMContext):
    file_id = message.photo[-1].file_id
    user_data = await state.get_data()

    await state.update_data(photoID = file_id)
    msg = await bot.send_photo(message.chat.id, file_id,  caption='Фото загружено')
    await state.reset_state(with_data=False)
    
    await asyncio.sleep(3)
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg.message_id)
    await bot.delete_message(chat_id=message.from_user.id, message_id=user_data['photo_msgID'])
    await message.delete()



@dp.message_handler(content_types=["video"], state=st.UploadPhotoState.add_photo)
async def saveVideo(message: types.Message,  state: FSMContext):
    print(message.video)
    print(message.video.file_id)
    user_data = await state.get_data()


    file_id = message.video.file_id
    
    await state.update_data(videoID = file_id)
    msg = await bot.send_video(message.chat.id, file_id, caption='Видео загружено')
    await state.reset_state(with_data=False)
    
    await asyncio.sleep(3)
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg.message_id)
    await bot.delete_message(chat_id=message.from_user.id, message_id=user_data['photo_msgID'])
    await message.delete()


## пригласить пользователя
async def add_user(call: types.CallbackQuery,  state: FSMContext):
    
    mode = call.data.split('_')[1]
    keyboard = types.InlineKeyboardMarkup()    
    for user in tdb.users:
        keyboard.add(types.InlineKeyboardButton(user, callback_data='user_{0}_{1}'.format(tdb.users_chat_id[user], mode)))
    
    msg = await call.message.answer('Выберите пользователя:', reply_markup=keyboard)
    await state.update_data(choose_user_msgID = msg.message_id)


async def choose_user(call: types.CallbackQuery,  state: FSMContext):
    
    await state.update_data(from_chatID = call.from_user.id)
    await state.update_data(to_chatID = call.data.split("_")[1])
    await state.update_data(mode_chatID = call.data.split("_")[2])
    
    user_data = await state.get_data()
    await bot.edit_message_text(text='Подтвердите выбор' ,
                                chat_id = call.from_user.id, 
                                message_id=user_data['choose_user_msgID'],
                                reply_markup=kb.add_user_kb)
    

async def send_notification(call: types.CallbackQuery,  state: FSMContext):
    user_data = await state.get_data()
    taskID = user_data['taskID']
    to_chatID = user_data['to_chatID']
    from_chatID = user_data['from_chatID']
    mode_chatID = user_data['mode_chatID']
    
    taskNAME = user_data['taskNAME']
    
    if mode_chatID == 'invite':
        text_ = '{0} приглашает вас присоединиться к задаче "{1}"'.format(get_key(tdb.users_chat_id, user_data['from_chatID']),taskNAME)
    elif mode_chatID == 'shift':
        text_ = '{0} предлагает вам принять задачу "{1}"'.format(get_key(tdb.users_chat_id, user_data['from_chatID']),taskNAME)
  
    reply_kb = types.InlineKeyboardMarkup()
    callback_data_accept = 'tasksend_accept_{0}_{1}_{2}_{3}'.format(taskID, from_chatID, to_chatID, mode_chatID)
    callback_data_decline = 'tasksend_decline_{0}_{1}_{2}_{3}'.format(taskID, from_chatID, to_chatID, mode_chatID)
    
    accept_task_button = types.InlineKeyboardButton('✅ Принять', callback_data = callback_data_accept)
    decline_task_button = types.InlineKeyboardButton('❌ Отклонить', callback_data = callback_data_decline)
    reply_kb.row(accept_task_button, decline_task_button)
    
    msg = await bot.send_message(chat_id=user_data['to_chatID'], 
                                     text=escape_md(text_),
                                     reply_markup=reply_kb)
    await state.update_data(ask_msgID = msg.message_id)
    await bot.delete_message(chat_id=call.from_user.id, message_id = call.message.message_id)


async def tasksend_reply(call: types.CallbackQuery,  state: FSMContext):
    
    await bot.delete_message(chat_id=call.from_user.id, message_id = call.message.message_id)
    
    mode = call.data.split('_')[1]
    taskID = int(call.data.split('_')[2])
    from_chatID = call.data.split('_')[3]
    to_chatID = float(call.data.split('_')[4])
    mode_chatID = call.data.split('_')[5]



    req = requests.get(URL + '/ERP/hs/tg_bot/tasks', auth=HTTPBasicAuth(LOGIN, PASS))
    dataDB = req.json()
    date_task = dt.datetime.strptime(dataDB[taskID]['Дата'], '%d.%m.%Y %H:%M:%S').strftime('%d/%m/%Y')
    
    if dataDB[taskID]['Наименование'][:2]==' (':
        task_descr = dataDB[taskID]['Наименование'][2:-1]
    else:
        task_descr = dataDB[taskID]['Наименование']

    taskNAME =  text(bold(escape_md(dataDB[taskID]['Номер'])), 'от', escape_md(date_task), ' ',
                        escape_md(task_descr))

    hide_button = types.InlineKeyboardButton('Cкрыть уведомление', callback_data='hide_message')
    keyboard = types.InlineKeyboardMarkup().add(hide_button)

    if (mode == 'accept')&(mode_chatID == 'invite'):
        text_ = '{0} принял задачу "{1}". Выполняется добавление пользователя.'.format(get_key(tdb.users_chat_id, to_chatID),taskNAME) 
        await bot.send_message(chat_id=from_chatID, text=escape_md(text_), reply_markup=keyboard)
 
    elif (mode == 'accept')&(mode_chatID == 'shift'):
        text_ = '{0} принял задачу "{1}". Выполняется переадресация задачи.'.format(get_key(tdb.users_chat_id, to_chatID),taskNAME) 
        await bot.send_message(chat_id=from_chatID, text=escape_md(text_), reply_markup=keyboard)
                   
    elif mode == 'decline':
        text_ = '{0} отклонил задачу "{1}"'.format(get_key(tdb.users_chat_id, to_chatID),taskNAME) 
        await bot.send_message(chat_id=from_chatID, text=escape_md(text_), reply_markup=keyboard)





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
    dp.register_callback_query_handler(accept_task, Text(startswith="accept_task"))
    dp.register_callback_query_handler(decline_task, Text(startswith="decline_task"))
    

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
    dp.register_callback_query_handler(uploadPhoto, Text(startswith="add_photo"), state="*")
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

    