# -*- coding: utf-8 -*-

import logging
import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from datetime import datetime as dt
from aiogram.utils.markdown import text, hbold
from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress

import states as st
import keyboards as kb

from config import LEN_TASKS, URL
from app import dp, bot

### 
from database.DB1C import Database_1C
from database import sqlDB
# from test_db import test_DB, users, users_chat_id, actions_var_list

logging.basicConfig(level=logging.INFO)


    
## Старт
async def command_start(message : types.Message, state: FSMContext):
    user: sqlDB.User = sqlDB.User.basic_auth(chat_id = message.from_user.id)
    if isinstance(user, sqlDB.User):
        keyboard = kb.StartMenu(mode='change')
    else:
        keyboard = kb.StartMenu(mode='auth')
        
        
    msg_text = text(hbold('Добро пожаловать!'),'\n','Выберите действие:',sep='')
    msg = await message.answer (msg_text, reply_markup=keyboard)
    await state.update_data(start_msgID=msg.message_id)
    await state.reset_state(with_data=False)
    
## Назад к старту
async def back_start(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data() 
    msg_text = text(hbold('Добро пожаловать!'),'\n','Выберите действие:',sep='')
    await bot.edit_message_text(text=msg_text, 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=kb.StartMenu(mode='change'))   

## Фильтры задач
async def full_list_move(call: types.CallbackQuery, state: FSMContext):
    user: sqlDB.User = sqlDB.User.basic_auth(chat_id = call.from_user.id)
    if isinstance(user, sqlDB.User):
        user_data = await state.get_data()
        await bot.edit_message_text(text=text(hbold('Доступные фильтры:')), 
                            chat_id = call.from_user.id,
                            message_id = user_data['start_msgID'],
                            reply_markup=kb.FiltersMenu()) 
    else:
        return await bot.answer_callback_quersy(call.id, text = 'Пользователь не найден в базе данных. Пожалуйста, пройдите авторизацию.', show_alert=True)        
 
## Назад к фильтрам 
async def back_to_filteres (call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await full_list_move (call, state)

## Список задач
async def full_list_taskd(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    
    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    print(user.chat_id, user.login)
    
    text_mode = {'FULL' : {'text' : text(hbold('Все задачи:')), 'params' : {'Executed':'no'}},
                 'FULL_ALL' : {'text' : text(hbold('Все задачи:')), 'params' : {'Executed':'yes'}},
                 'USER' : {'text' : text(hbold('Мои задачи:')), 'params' : {'Executed':'no', 'Executor': user.login}},
                 'USER_ALL' : {'text' : text(hbold('Мои задачи:')), 'params' : {'Executor': user.login, 'Executed':'yes'}},
                 'FREE' : {'text' : text(hbold('Свободные задачи:')), 'params' : {'Executed':'no', 'Accepted' : 'no'}},
                 'PAST' : {'text' : text(hbold('Просроченные задачи:')), 
                           'params' : {'Executed' : 'no', 
                                       'DateBegin': '20001231235959', 
                                       'DateExecuted'  : dt.now().strftime('%Y%m%d%H%M%S'), 
                                       }}}
    
    user_data = await state.get_data()
    if callback_data['ACTION'] in ['FULL','USER','FREE','PAST', 'FULL_ALL', 'USER_ALL']:
        page = 0
        mode = callback_data['ACTION']
        await state.update_data(pageID = page)
        await state.update_data(filter_mode=mode)
        
    elif callback_data['ACTION'] == 'PAGE':
        page = int(callback_data['PAGE'])  
        mode = user_data['filter_mode']
        await state.update_data(pageID = page)
    else:
        mode = user_data['filter_mode']
        page = user_data['pageID']    
     
    DB1C = Database_1C(URL, user.login_db, user.password)
    dataDB = DB1C.tasks(text_mode[mode]['params'])
    
        
  
    if isinstance(dataDB, dict):
        # await bot.delete_message(chat_id=call.from_user.id, message_id=user_data['start_msgID'])

        msg = await bot.edit_message_text(text=text_mode[mode]['text'], 
                            chat_id = call.from_user.id,
                            message_id = user_data['start_msgID'],
                            reply_markup=kb.TasksMenu(data = dataDB, page=page))
        # await state.update_data(start_msgID=msg.message_id)
    else: 
        return await bot.answer_callback_query(call.id, text = 'По данному фильтру нет задач.', show_alert=True)

## Описание задачи  
async def send_task_info(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    
    user_data = await state.get_data()
    taskID = callback_data['TASK_ID']
    await state.update_data(taskID=taskID)

    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    DB1C = Database_1C(URL, user.login_db, user.password)
    dataDB = DB1C.tasks(params={'id' : taskID})[taskID]
     
    date_task = dt.strptime(dataDB['Дата'], '%d.%m.%Y %H:%M:%S').strftime('%d/%m/%Y') # %d.%m.%Y %H:%M:%S     

    taskNAME = text(hbold(dataDB['Номер']), ' от ', date_task, '\n',
                        dataDB['Наименование'], sep='')
    await state.update_data(taskNAME=taskNAME)
    
    task_message = text(hbold(dataDB['Номер']), ' от ', date_task, '\n',
                        dataDB['Наименование'], '\n','\n',
                        hbold('Клиент: '), dataDB['CRM_Партнер'], '\n','\n',
                        hbold('Описание: '),'\n',
                        dataDB['Описание'], '\n','\n',
                        hbold('Исполнение: '), dataDB['Исполнитель'], '\n',
                        dataDB['РезультатВыполнения'],
                        # hbold('Комментарии: '),'\n',
                        # dataDB['Комментарий'],
                        sep='')

    await bot.delete_message(chat_id=call.from_user.id, message_id=user_data['start_msgID'])

    msg = await bot.send_message(text=task_message, 
                        chat_id = call.from_user.id,
                        # message_id = user_data['start_msgID'],
                        reply_markup=kb.TaskActionMenu(accepted=dataDB['ПринятаКИсполнению'], done=dataDB['Выполнена']))
    await state.update_data(start_msgID=msg.message_id)

    

## Принять задачу
async def accept_task(call: types.CallbackQuery, state: FSMContext, callback_data: dict, ):

    user_data = await state.get_data()
    
    if callback_data['ACTION'] == 'ACCEPT':
        msg_text = 'Задача принята'
        keyboard = kb.TaskActionMenu(accepted='Да')
        accept='yes'
             
    elif callback_data['ACTION'] == 'DECLINE':
        msg_text = 'Задача отменена'
        keyboard = kb.TaskActionMenu(accepted='Нет')
        accept='no'
    print(user_data['taskID'])
    
    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    DB1C = Database_1C(URL, user.login_db, user.password)
    # DB1C.SetAccept(taskID=user_data['taskID'], accept=accept)
    DB1C.SetExecutor(taskID=user_data['taskID'], user=user.login)
    
    await bot.answer_callback_query(call.id, text = msg_text)
    await bot.edit_message_reply_markup(chat_id = call.from_user.id,
                                     message_id = call.message.message_id,
                                     reply_markup=keyboard)

### ввести комментарий и сохранить
async def comment(call: types.CallbackQuery, state: FSMContext):
    msg = await call.message.answer('Введите коментарий:', reply_markup=kb.cancel_kb)
    await state.update_data(comment_id = msg.message_id)
    await st.CommentStates.add_comment.set()

async def save_comment(message: types.Message, state: FSMContext): # нельзя оставить коммент выполненной задаче
    user_data = await state.get_data()  
    
    user: sqlDB.User = sqlDB.User.basic_auth(message.from_user.id)
    DB1C = Database_1C(URL, user.login_db, user.password)
    req = DB1C.setcomment(user_data['taskID'], message.text, user.login)
    
    if req != None:
        msg = await message.answer(req)
        await asyncio.sleep(3)
        await bot.delete_message(chat_id=message.from_user.id, message_id=msg.message_id)
        await bot.delete_message(chat_id=message.from_user.id, message_id=user_data['comment_id'])
        await message.delete()
        await state.reset_state(with_data=False)
        return
    
    msg = await message.answer('Комментарий сохранен.')
       
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg.message_id)
    await bot.delete_message(chat_id=message.from_user.id, message_id=user_data['comment_id'])
    await message.delete()
    
    taskID = user_data['taskID']
    dataDB = DB1C.tasks(params={'id' : taskID})[taskID]    
        
    date_task = dt.strptime(dataDB['Дата'], '%d.%m.%Y %H:%M:%S').strftime('%d/%m/%Y') # %d.%m.%Y %H:%M:%S     

    task_message = text(hbold(dataDB['Номер']), ' от ', date_task, '\n',
                        dataDB['Наименование'], '\n','\n',
                        hbold('Клиент: '), dataDB['CRM_Партнер'], '\n','\n',
                        hbold('Описание: '),'\n',
                        dataDB['Описание'], '\n','\n',
                        hbold('Исполнение: '), dataDB['Исполнитель'], '\n',
                        dataDB['РезультатВыполнения'],
                        # hbold('Комментарии: '),'\n',
                        # dataDB['Комментарий'],
                        sep='')
    with suppress(MessageNotModified):
        await bot.edit_message_text(text=task_message, 
                            chat_id = message.from_user.id,
                            message_id = user_data['start_msgID'],
                            reply_markup=kb.TaskActionMenu(accepted=dataDB['ПринятаКИсполнению'], done=dataDB['Выполнена']))   
    
    await state.reset_state(with_data=False)


### добавить фото/видео
async def uploadFile(call: types.CallbackQuery, state: FSMContext):
    msg = await call.message.answer('Добавьте фото или видео:', reply_markup=kb.cancel_kb)
    await state.update_data(photo_msgID = msg.message_id)
    await st.UploadFileState.add_file.set()

# @dp.message_handler(content_types=["photo"], state=st.UploadFileState.add_file)
# @dp.message_handler(state=st.UploadFileState.add_file)
@dp.message_handler(content_types=["text"], state=st.UploadFileState.add_file)
async def saveFile(message: types.Message,  state: FSMContext):
    user_data = await state.get_data()
    print(message.content_type)
    print(message)
    
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_name = message.photo[-1].values
        print(file_name)
        
    elif message.content_type == 'video':
        file_id = message.video.file_id
        file_name = message.video.file_name
        print(file_name)
        print(message.video.values)
    
    # TODO: отправление файла и кодировка в байтах
    # data = {"id": user_data['taskID'], "file": file_id, "name": file_name, 'extension': file_extension}
         
    await message.delete() 
    await bot.delete_message(chat_id=message.from_user.id, message_id=user_data['photo_msgID'])
    await state.reset_state(with_data=False)



## пригласить пользователя
async def add_user(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
    
    user_data = await state.get_data()
    
    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    DB1C = Database_1C(URL, user.login_db, user.password)       

    user_request = sqlDB.UserRequest.new_request(taskID=user_data['taskID'],
                                                     taskNAME = user_data['taskNAME'],
                                                     from_userID = user,
                                                     # to_userID = "None",
                                                     action = callback_data['ACTION'],
                                                     # decision = 'DECLINED',
                                                     )    
    user_request.save()
    print('User from', user_request.from_userID)    
       
    users_list = DB1C.users()
    msg = await call.message.answer('Выберите пользователя:', reply_markup=kb.UsersMenu(users_list))
    await state.update_data(choose_user_msgID = msg.message_id)
    await state.update_data(user_requestID = user_request.id)

async def choose_user(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
    
    user_data = await state.get_data()
    user_request = sqlDB.UserRequest.basic_auth(user_data['user_requestID'])
    user_request.to_userID = sqlDB.User.basic_auth(callback_data['CHAT_ID'])
    user_request.save()
    print('User to', user_request.to_userID)
    await bot.edit_message_text(text='Подтвердите выбор' , # TODO: добавить название юзера
                                chat_id = call.from_user.id, 
                                message_id=user_data['choose_user_msgID'],
                                reply_markup=kb.add_user_kb)
    

async def send_notification(call: types.CallbackQuery,  state: FSMContext):
      
    user_data = await state.get_data()
    user_request = sqlDB.UserRequest.basic_auth(user_data['user_requestID'])    
    
    msg = await bot.send_message(chat_id=user_request.to_userID, 
                                     text=user_request.get_text(),
                                     reply_markup=kb.UsersNotification(user_request.id))
    
    await state.update_data(ask_msgID = msg.message_id)  
    await bot.delete_message(chat_id=call.from_user.id, message_id = call.message.message_id)

async def tasksend_reply(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):

    await bot.delete_message(chat_id=call.from_user.id, message_id = call.message.message_id)
    user_data = await state.get_data()

    user_request = sqlDB.UserRequest.basic_auth(callback_data['REPLY'])
    user_request.decision = callback_data['ACTION']
    user_request.save()
    
    user: sqlDB.User = sqlDB.User.basic_auth(user_request.from_userID)    
    DB1C = Database_1C(URL, user.login_db, user.password)

    if (user_request.decision == 'ACCEPT')&(user_request.action == 'INVITE'):
        req = DB1C.AddUsers(user_data['taskID'], [user.login])         

    elif (user_request.decision == 'ACCEPT')&(user_request.action == 'TRANSFER'):
        req = DB1C.SetRedirect(user_data['taskID'], user.login)      
    else:
        req = None
        
    if req != None:
        await bot.answer_callback_query(call.id, text=req, show_alert=True)
        return  
        
    keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Cкрыть уведомление', callback_data='cancel_b')) 
    await bot.send_message(chat_id=user_request.from_userID, text=user_request.det_text_reply(), reply_markup=keyboard)


###  вывести дополнительные варианты
async def show_options(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    mode = callback_data['ACTION']
    print(mode)
    
    if mode == 'VARS':
        user_data = await state.get_data()
        user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id) 
        DB1C = Database_1C(URL, user.login_db, user.password)
        variants = DB1C.GetVariants(user_data['taskID'])
        print(variants)
        if isinstance(variants, list):
            
            keyboard = kb.VarsMenu(variants)
            # TODO: отправлять клавиатуру с вариантами
        else:
            await bot.answer_callback_query(call.id, text=variants, show_alert=True)
            return            


    elif mode == 'MOREVARS':
        keyboard = kb.TaskActionMoreMenu()
    await bot.edit_message_reply_markup(chat_id = call.from_user.id,
                                      message_id = call.message.message_id,
                                      reply_markup=keyboard)    
        

# async def state_var(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
#     chosen_var = callback_data['VAR']
#     user_data = await state.get_data()  
#     msg_txt = 'Подтвердите присвоение задаче {0} статуста "{1}"'.format(user_data['taskID'], chosen_var)
#     await call.message.answer(msg_txt, reply_markup=kb.option_kb)

# async def state_var_accept(call: types.CallbackQuery,  state: FSMContext):
    # TODO: нет метода для присвоения варианта задачи
#     await bot.answer_callback_query(call.id, text='Вариант сохранен', show_alert=True)
#     await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

      

async def del_message(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await state.reset_state(with_data=False) 
    
async def back_vars(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    taskID = user_data['taskID']

    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    DB1C = Database_1C(URL, user.login_db, user.password)
    dataDB = DB1C.tasks(params={'id' : taskID})[taskID]
   
    await bot.edit_message_reply_markup(
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=kb.TaskActionMenu(accepted=dataDB['ПринятаКИсполнению'], done=dataDB['Выполнена']))

async def echo_send(message : types.Message):
    msg = await message.answer ('Нет такой команды')
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg.message_id)
    await message.delete()

    
def reg_handlers_client(dp: Dispatcher):

    dp.register_message_handler(command_start, commands=['start'])    
    
    ### Фильтры    
    dp.register_callback_query_handler(back_start,        kb.FiltersMenu.CallbackData.FILTER_CB.filter(ACTION=["BACK"]))
    dp.register_callback_query_handler(full_list_move,    kb.StartMenu.CallbackData.START_CB.filter(ACTION=["SHOWTASKS"]))
    dp.register_callback_query_handler(back_to_filteres,  kb.TasksMenu.CallbackData.BACK_CB.filter(ACTION=["BACK"]))

    ### Список задач
    dp.register_callback_query_handler(full_list_taskd, kb.FiltersMenu.CallbackData.FILTER_CB.filter(ACTION=['FULL','USER','FREE','PAST', 'FULL_ALL', 'USER_ALL']))  
    dp.register_callback_query_handler(full_list_taskd, kb.TasksMenu.CallbackData.PAGES_CB.filter(ACTION=["PAGE"]))  
    dp.register_callback_query_handler(full_list_taskd, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=["BACK"]))  
    
    ### Информация о задаче    
    dp.register_callback_query_handler(send_task_info, kb.TasksMenu.CallbackData.TASKS_CB.filter(ACTION=["TASK"]))
    
    ### Принять задачу
    dp.register_callback_query_handler(accept_task, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=["ACCEPT", "DECLINE"]))

    ### Комментарий
    dp.register_callback_query_handler(comment, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=['COMMENT']), state="*")
    dp.register_message_handler(save_comment, state=st.CommentStates.add_comment)

    ### Показать доп.варианты
    dp.register_callback_query_handler(show_options, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=['VARS', 'MOREVARS']))

    ### Выбрать вариант
    # dp.register_callback_query_handler(state_var, Text(startswith="varb_")) 
    # dp.register_callback_query_handler(state_var_accept, Text(startswith="accept_b"))
  
    
    ### Добавить пользователя
    dp.register_callback_query_handler(add_user,          kb.TaskActionMoreMenu.CallbackData.MOREVAR_CB.filter(ACTION=['INVITE', 'TRANSFER']))
    dp.register_callback_query_handler(choose_user,       kb.UsersMenu.CallbackData.USER_CB.filter(ACTION=['USERS']))
    dp.register_callback_query_handler(send_notification, Text(startswith="users_invite"))
    dp.register_callback_query_handler(tasksend_reply,    kb.UsersNotification.CallbackData.USER_NOT.filter(ACTION=['ACCEPT', 'DECLINE']))


    ### Добавить файл
    dp.register_callback_query_handler(uploadFile, kb.TaskActionMoreMenu.CallbackData.MOREVAR_CB.filter(ACTION=['FILE']), state="*")
    # dp.register_callback_query_handler(saveFile, state=st.UploadFileState.add_file)
 
    dp.register_callback_query_handler(del_message,  Text(contains=('cancel_b'), ignore_case=True), state="*")
    dp.register_callback_query_handler(back_vars, kb.TaskActionMoreMenu.CallbackData.MOREVAR_CB.filter(ACTION=['BACK']))
    dp.register_callback_query_handler(back_vars, kb.VarsMenu.CallbackData.VARS.filter(VAR=['BACK']))
    dp.register_message_handler(echo_send)

