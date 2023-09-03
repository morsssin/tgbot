# -*- coding: utf-8 -*-

import logging
import asyncio
import base64
import datetime
from peewee import *

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from datetime import datetime as dt
from aiogram.utils.markdown import text, hbold
from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress

import states as st
import keyboards as kb

from config import BOT_SETTINGS
from load_bot import bot, dp

from database.DB1C import Database_1C
from database import sqlDB




data_DB_dict = {'number': 'Номер',
                'date_1c': 'Дата',
                'task_name': 'Наименование',
                'completed': 'Выполнена',
                'author': 'Автор',
                'group_of_executors': 'ГруппаИсполнителейЗадач',
                'execution_date': 'ДатаИсполнения',
                'start_date': 'ДатаНачала',
                'date_of_acceptance_and_execution': 'ДатаПринятияКИсполнению',
                'description': 'Описание',
                'subject': 'Предмет',
                'accepted_to_implementation': 'ПринятаКИсполнению',
                'execution_result': 'РезультатВыполнения',
                'status_business_process': 'СостояниеБизнесПроцесса',
                'period_of_execution': 'СрокИсполнения',
                'crm_execution_option': 'CRM_ВариантВыполнения',
                'crm_iteration': 'CRM_Итерация',
                'crm_contact_person': 'CRM_КонтактноеЛицо',
                'crm_partner': 'CRM_Партнер',
                'crm_forwarded': 'CRM_Переадресована',
                'crm_route_point': 'CRM_ТочкаМаршрута',
                'executor': 'Исполнитель',
                'group_executors': 'РольИсполнителя',
                'performance': 'Представление',
                'taskID': 'id',
                'comment': 'Комментарий',
                'additional_executors': 'ДополнительныеИсполнители',
}


def getTaskDescription(dataDB: dict):
        
    date_task = dt.strptime(dataDB['Дата'], '%d.%m.%Y %H:%M:%S').strftime('%d/%m/%Y') # %d.%m.%Y %H:%M:%S     

    taskNAME = text(hbold(dataDB['Номер']), ' от ', date_task, '\n',
                        dataDB['Наименование'], sep='')
    
    if (dataDB['ДополнительныеИсполнители'] != [])&(dataDB['ДополнительныеИсполнители'] != ""):
        add_executors = ', '.join(dataDB['ДополнительныеИсполнители'])
    else:
        add_executors = 'Нет'
        
    description = 'Нет' if dataDB['Описание'] == "" else dataDB['Описание']
    executors = 'Нет' if dataDB['РольИсполнителя'] == "" else dataDB['РольИсполнителя']
    executor = 'Нет' if dataDB['Исполнитель'] == "" else dataDB['Исполнитель']
    result = 'Нет' if dataDB['РезультатВыполнения'] == "" else dataDB['РезультатВыполнения']
    terms = 'Нет' if dataDB['СрокИсполнения'] == "" else dataDB['СрокИсполнения']
        
    
    task_message = text(hbold(dataDB['Номер']), ' от ', date_task, '\n',
                        dataDB['Наименование'], '\n','\n',
                        hbold('Клиент: '), dataDB['CRM_Партнер'], '\n','\n',
                        hbold('Описание: '),'\n',
                        description, '\n','\n',
                        # hbold('Принята задача: '), dataDB['ПринятаКИсполнению'], '\n\n',
                        hbold('Группа исполнителей: '), executors, '\n',
                        hbold('Исполнитель: '), executor, '\n',
                        hbold('Дополнительные исполнители: '), add_executors, '\n',
                        hbold('Срок исполнения: '), terms,'\n', '\n',
                        hbold('Результат выполнения: '), '\n',
                        result,
                        # hbold('Комментарии: '),'\n',
                        # dataDB['Комментарий'],
                        sep='')
    return task_message, taskNAME

async def send_alert(message: types.Message, text: str, time: int):
    msg = await bot.send_message(chat_id=message.from_user.id, text=text)
    await asyncio.sleep(time)
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg.message_id)

def get_media_group(files):
    import magic
    import mimetypes
    import re
    import io
    
    media = types.MediaGroup()
    media_docs = types.MediaGroup()
    docs = False
    
    for file in files:
    
        file = re.sub(r"^data\:.+base64\,(.+)$", r"\1", file)
    
        decoded = base64.b64decode(file)
        mime_type = magic.from_buffer(decoded, mime=True)
        file_ext = mimetypes.guess_extension(mime_type)
        
        bytesio = io.BytesIO(decoded)
        bytesio.seek(0)
        

        if file_ext in ['.jpg']:
            media.attach_photo(types.InputMediaPhoto(types.InputFile(bytesio)))            
        elif file_ext in ['.mp4']:
            media.attach_video(types.InputMediaVideo(types.InputFile(bytesio)))
        else:
            docs = True
            media_docs.attach_document(types.InputMediaDocument(types.InputFile(bytesio)))
            
    if docs:
        return [media, media_docs]
    else:
        return [media]
    

## Старт
async def command_start(message : types.Message, state: FSMContext):
    logging.info(f"{message.from_user.id} - start")
    
    await state.reset_state(with_data=False)
    user: sqlDB.User = sqlDB.User.basic_auth(chat_id = message.from_user.id)
    
    if isinstance(user, sqlDB.User):
        keyboard = kb.StartMenu(mode='change')
    else:
        keyboard = kb.StartMenu(mode='auth')
        
        
    msg_text = text(hbold('Добро пожаловать!'),'\n','Выберите действие:',sep='')
    msg = await message.answer (msg_text, reply_markup=keyboard)
    await state.update_data(start_msgID=msg.message_id)
    

    
## Назад к старту
async def back_start(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=False)
    
    user_data = await state.get_data() 
    msg_text = text(hbold('Добро пожаловать!'),'\n','Выберите действие:',sep='')
    with suppress(MessageNotModified):
        await bot.edit_message_text(text=msg_text, 
                            chat_id = call.from_user.id,
                            message_id = user_data['start_msgID'],
                            reply_markup=kb.StartMenu(mode='change'))   

## Фильтры задач
async def full_list_move(call: types.CallbackQuery, state: FSMContext):
    
    await state.reset_state(with_data=False)
    user: sqlDB.User = sqlDB.User.basic_auth(chat_id = call.from_user.id)
    
    if isinstance(user, sqlDB.User):
        logging.info(f"{call.from_user.id} {user.login_db} - show filters")
        user_data = await state.get_data()
        with suppress(MessageNotModified):
            await bot.edit_message_text(text=text(hbold('Доступные фильтры:')), 
                                chat_id = call.from_user.id,
                                message_id = user_data['start_msgID'],
                                reply_markup=kb.FiltersMenu()) 
    else:
        logging.warning(f"{call.from_user.id} - show filters - USER NOT FOUND")
        return await bot.answer_callback_query(call.id, text = 'Пользователь не найден в базе данных. Пожалуйста, пройдите авторизацию.', show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)        
 
## Назад к фильтрам 
async def back_to_filteres (call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.reset_state(with_data=False)
    await del_message(call, state)
    await del_files(call, state)
    await full_list_move (call, state)

## Список задач
async def full_list_tasks(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.reset_state(with_data=False)
    await del_message(call, state)
    await del_files(call, state)
    
    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    logging.info(f"{call.from_user.id} {user.login_db} - show full list")
    
    text_mode = {'FULL' : {'text' : text(hbold('Входящие задачи:')), 'params' : {'Executed':'no', 
                                                                                 'Accepted': 'no'
                                                                                 }},
                 'USER' : {'text' : text(hbold('Текущие задачи:')), 'params' : {'Executed':'no', 'Executor': user.name_1C, 'Accepted': 'yes'}},
                 'USER_ALL' : {'text' : text(hbold('Выполненные задачи:')), 'params' : {'Executor': user.name_1C, 'Executed':'yes'}},
                 'FREE' : {'text' : text(hbold('Свободные задачи:')), 'params' : {'Executed':'no', 
                                                                                  'Accepted' : 'no'
                                                                                  }},
                 'PAST' : {'text' : text(hbold('Просроченные задачи:')), 
                           'params' : {'Executed' : 'no', 
                                       'DateBegin': '20001231235959', 
                                       'DateExecuted'  : dt.now().strftime('%Y%m%d%H%M%S'), 
                                       'Executor': user.name_1C,
                                       'Accepted': 'yes',
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
     
    DB1C = Database_1C(user.login_db, user.password)
    dataDB = DB1C.tasks(text_mode[mode]['params'])
    if not isinstance(dataDB, dict):
        return await bot.answer_callback_query(call.id, text=dataDB, show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)

    roles = DB1C.GetRoles(user.name_1C.lower())
    
    user_data = await state.get_data()
    
    full_cond = (callback_data['ACTION'] == 'FULL')|((user_data['filter_mode']=='FULL')&((callback_data['ACTION'] == 'BACK')|(callback_data['ACTION'] == 'PAGE')))
    free_cond = (callback_data['ACTION'] == 'FREE')|((user_data['filter_mode']=='FREE')&((callback_data['ACTION'] == 'BACK')|(callback_data['ACTION'] == 'PAGE')))
    
    if full_cond:
        if isinstance(roles, list):
            dataDB = {key:value for i, (key, value) in enumerate(dataDB.items()) if ((dataDB[key]['РольИсполнителя'] in roles)|(dataDB[key]['Исполнитель'].lower() == user.name_1C.lower()))}
        else:
            dataDB = {key:value for i, (key, value) in enumerate(dataDB.items()) if (dataDB[key]['Исполнитель'].lower() == user.name_1C.lower())}
        
    elif free_cond:
        if isinstance(roles, list):
            dataDB = {key:value for i, (key, value) in enumerate(dataDB.items()) if (((dataDB[key]['РольИсполнителя'] not in roles))&(dataDB[key]['Исполнитель'].lower() != user.name_1C.lower()))}
        else:
            dataDB = {key:value for i, (key, value) in enumerate(dataDB.items()) if (dataDB[key]['Исполнитель'].lower() != user.name_1C.lower())}
   

    if isinstance(dataDB, dict):
        logging.info(f"{call.from_user.id} {user.login_db} - num of tasks:{len(dataDB)}")
        with suppress(MessageNotModified):
            await bot.edit_message_text(text=text_mode[mode]['text'], 
                                chat_id = call.from_user.id,
                                message_id = user_data['start_msgID'],
                                reply_markup=kb.TasksMenu(data = dataDB, page=page, per_page = BOT_SETTINGS.LEN_TASKS, user=user))
    else: 
        return await bot.answer_callback_query(call.id, text = dataDB, show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)

## Описание задачи  
async def send_task_info(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.reset_state(with_data=False)
    await del_message(call, state)
    await del_files(call, state)
    
    user_data = await state.get_data()
    try:
        taskID = callback_data['TASK_ID']
    except:
        taskID = user_data['taskID']

    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    DB1C = Database_1C(user.login_db, user.password)
    dataDB = DB1C.tasks(params={'id' : taskID})[taskID]
    
    logging.info(f"{call.from_user.id} {user.login_db} - send task info - taskID:{taskID}")
        
    if isinstance(dataDB, dict):
        task_message, taskNAME = getTaskDescription(dataDB)

        is_executor = (dataDB['Исполнитель'].lower() == user.name_1C.lower())

        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=user_data['start_msgID'])
            msg = await bot.send_message(text=task_message, 
                                chat_id = call.from_user.id,
                                reply_markup=kb.TaskActionMenu(accepted=dataDB['ПринятаКИсполнению'], done=dataDB['Выполнена'], is_executor=is_executor))
            await state.update_data(start_msgID=msg.message_id)

          
        except Exception as ex:
            logging.info(f'{ex}')
            with suppress(MessageNotModified):
                msg = await bot.edit_message_text(text=task_message, 
                                    chat_id = call.from_user.id,
                                    message_id = user_data['start_msgID'],
                                    reply_markup=kb.TaskActionMenu(accepted=dataDB['ПринятаКИсполнению'], done=dataDB['Выполнена'], is_executor=is_executor))
         
        await state.update_data(taskID=taskID)
        await state.update_data(taskNAME=taskNAME)
        await state.update_data(task_message=task_message)
    
        files = DB1C.GetFiles(taskID)
        if isinstance(files, list) and len(files)>0:
            logging.info(f"{call.from_user.id} {user.login_db} - send files:{len(files)}")
            msg_id = []
            
            for media in get_media_group(files):
                msg = await bot.send_media_group(chat_id = call.from_user.id, media=media)
                for i in msg:
                    msg_id.append(i.message_id)
            await state.update_data(file_msgID = msg_id)

    else: 
        return await bot.answer_callback_query(call.id, text = dataDB, show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)
    



## Принять задачу
async def accept_task(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.reset_state(with_data=False)  
    await del_message(call, state)
    user_data = await state.get_data()
    
    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    logging.info(f"{call.from_user.id} {user.login_db} - accept task - taskID:{user_data['taskID']}")
    
    
    DB1C = Database_1C(user.login_db, user.password)
    dataDB = DB1C.tasks(params={'id' : user_data['taskID']})[user_data['taskID']] 
    is_executor = (dataDB['Исполнитель'].lower() == user.name_1C.lower())
    
    
    if callback_data['ACTION'] == 'ACCEPT':
        msg_text = 'Задача принята'
        keyboard = kb.TaskActionMenu(accepted='Да', is_executor=True)
        accept='yes'
             
    elif callback_data['ACTION'] == 'DECLINE':
        msg_text = 'Задача отменена'
        keyboard = kb.TaskActionMenu(accepted='Нет', is_executor=is_executor)
        accept='no'
        
    if not isinstance(dataDB, dict):
        return await bot.answer_callback_query(call.id, text = dataDB, show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)
    
    if (dataDB['Исполнитель'].lower() == user.name_1C.lower())|(dataDB['Исполнитель'].lower() == ""):
        req = DB1C.SetAccept(taskID=user_data['taskID'], accept=accept)
        # req = None
        if req != None:
            await bot.answer_callback_query(call.id, text=req, show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)
            return
        
        if (dataDB['Исполнитель'].lower() == "")&(accept=='yes'):
            print(user_data['taskID'], user.name_1C)
            req = DB1C.SetExecutor(taskID=user_data['taskID'], user=user.name_1C)
            if req != None:
                await bot.answer_callback_query(call.id, text=req, show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)
                return  
              
    else:
        logging.info(f"{call.from_user.id} {user.login_db} - task already has executor - taskID:{user_data['taskID']}")
        await bot.answer_callback_query(call.id, text='У задачи уже назначен исполнитель!', show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)
        return          
    
    dataDB = DB1C.tasks(params={'id' : user_data['taskID']})[user_data['taskID']]    
    task_message, _ = getTaskDescription(dataDB)
    
    await bot.answer_callback_query(call.id, text = msg_text, cache_time=BOT_SETTINGS.CACHE_TIME)

    
    with suppress(MessageNotModified):
        await bot.edit_message_text(text=task_message,
                                    chat_id = call.from_user.id,
                                    message_id = call.message.message_id,
                                    reply_markup=keyboard)


### ввести комментарий и сохранить
async def comment(call: types.CallbackQuery, state: FSMContext):
    logging.info(f"{call.from_user.id} - comment ")
    await state.reset_state(with_data=False)
    
    await del_message(call, state)
    msg = await call.message.answer('Введите коментарий:', reply_markup=kb.cancel_kb)
    await state.update_data(add_msgID = msg.message_id)
    await st.CommentStates.add_comment.set()

async def save_comment(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    taskID = user_data['taskID']
    user: sqlDB.User = sqlDB.User.basic_auth(message.from_user.id)
    
    logging.info(f"{message.from_user.id} {user.login_db} - save comment - comment:{message.text} - taskID:{taskID}")
    
    DB1C = Database_1C(user.login_db, user.password)
    req = DB1C.SetComment(user_data['taskID'], message.text, user.name_1C)
    
    await message.delete()
   
    if req != None:
        await send_alert(message, text=req, time=3)
        await bot.delete_message(chat_id=message.from_user.id, message_id=user_data['add_msgID'])
        await state.reset_state(with_data=False)
        return
    
    logging.info(f"{message.from_user.id} {user.login_db} - comment saved")
    await send_alert(message, text='Комментарий сохранен.', time=2)
    await bot.delete_message(chat_id=message.from_user.id, message_id=user_data['add_msgID'])
     
    dataDB = DB1C.tasks(params={'id' : taskID})[taskID]  
    
    if isinstance(dataDB, dict):
        is_executor = (dataDB['Исполнитель'].lower() == user.name_1C.lower())
    else:
        await send_alert(message, text=dataDB, time=3)
        await state.reset_state(with_data=False)
        return
        
    task_message, _ = getTaskDescription(dataDB)

    with suppress(MessageNotModified):
        await bot.edit_message_text(text=task_message, 
                            chat_id = message.from_user.id,
                            message_id = user_data['start_msgID'],
                            reply_markup=kb.TaskActionMenu(accepted=dataDB['ПринятаКИсполнению'], done=dataDB['Выполнена'], is_executor=is_executor))   
    
    await state.reset_state(with_data=False)


### добавить фото/видео
async def uploadFile(call: types.CallbackQuery, state: FSMContext):
    logging.info(f"{call.from_user.id} - upload File")
    
    await state.reset_state(with_data=False)
    await del_message(call, state)
    msg = await call.message.answer('Добавьте фото или видео:', reply_markup=kb.cancel_kb) 
    await state.update_data(add_msgID = msg.message_id)
    await st.UploadFileState.add_file.set()

@dp.message_handler(content_types=['photo', 'video', 'document'], state=st.UploadFileState.add_file)
async def saveFile(message: types.Message,  state: FSMContext):
    import base64
    
    user: sqlDB.User = sqlDB.User.basic_auth(message.from_user.id)
    DB1C = Database_1C(user.login_db, user.password)
    user_data = await state.get_data()
    
    ftype = message.content_type
    taskID = user_data['taskID']
    date = message.date  
    description = message.caption
    
    logging.info(f"{message.from_user.id} {user.login_db} - save File - taskID:{taskID}")
    await message.delete() 
        
    if ftype == 'photo':
        
        tgID = message.photo[-1].file_id
        size = message.photo[-1].file_size
        name = 'photo_{0}.jpg'.format(tgID[16:26])
                
    elif ftype == 'video':
        tgID = message.video.file_id
        size = message.video.file_size
        name = message.video.file_name        
             
    elif ftype == 'document':
        tgID = message.document.file_id
        size = message.document.file_size
        name = message.document.file_name
        
    extension = name.split('.')[-1]

    new_file = sqlDB.File.create(tgID = tgID, 
                                 taskID = taskID,
                                  ftype = ftype,
                                  name = name,
                                  extension = extension,
                                  description = description, 
                                  size = size, 
                                  date = date)
    new_file.save() 
    
    new_file = (await bot.download_file_by_id(tgID)).getvalue()
    file64 = base64.b64encode(new_file).decode()
    
    req  = DB1C.SetFile(taskID, file64, name, extension)
    
    if req != None:
        await send_alert(message, text=req, time=3)
        await bot.delete_message(chat_id=message.from_user.id, message_id=user_data['add_msgID'])
        await state.reset_state(with_data=False)
        return
    
    logging.info(f"{message.from_user.id} {user.login_db} - file saved - taskID:{taskID}")
    await send_alert(message, text='Файл сохранен.', time=3)
    await del_files(message, state)
    
    files = DB1C.GetFiles(taskID)
    if isinstance(files, list) and len(files)>0:
        logging.info(f"{message.from_user.id} {user.login_db} - send files:{len(files)}")
        msg_id = []
        
        for media in get_media_group(files):
            msg = await bot.send_media_group(chat_id = message.from_user.id, media=media)
            for i in msg:
                msg_id.append(i.message_id)
        await state.update_data(file_msgID = msg_id)    
    
    await bot.delete_message(chat_id = message.from_user.id, message_id = user_data['add_msgID'])    
    await state.reset_state(with_data=False)


## пригласить пользователя
async def add_user(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
    await state.reset_state(with_data=False)
    await del_message(call, state)
    
    user_data = await state.get_data()
    user = sqlDB.User.basic_auth(call.from_user.id)
    DB1C = Database_1C(user.login_db, user.password)
    
    logging.info(f"{call.from_user.id} {user.login_db} - add user - taskID:{user_data['taskID']}")

    user_request = sqlDB.UserRequest.new_request(taskID=user_data['taskID'],
                                                     taskNAME = user_data['task_message'],
                                                     from_userID = user.chat_id,
                                                     from_userName = user.name_1C,
                                                     action = callback_data['ACTION'],
                                                     )    
    user_request.save()
       
    users_list = DB1C.users()
    with suppress(MessageNotModified):
        await bot.edit_message_text(text='Выберите пользователя:', 
                            chat_id = call.from_user.id,
                            message_id = user_data['start_msgID'],
                            reply_markup=kb.UsersMenu(users_list)) 
    
    # msg = await call.message.answer('Выберите пользователя:', reply_markup=kb.UsersMenu(users_list))   
    # await state.update_data(add_msgID = msg.message_id)
    await state.update_data(user_requestID = user_request.id)


async def choose_user(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
    
    user_data = await state.get_data()
    user = sqlDB.User.basic_auth(call.from_user.id)
    DB1C = Database_1C(user.login_db, user.password)
    
    
    if callback_data['ACTION'] == 'BACK':
        taskID = user_data['taskID']
        dataDB = DB1C.tasks(params={'id' : taskID})[taskID]
        task_message, _ = getTaskDescription(dataDB)
                 
        with suppress(MessageNotModified):
            await bot.edit_message_text(text=task_message, 
                                chat_id = call.from_user.id,
                                message_id = user_data['start_msgID'],
                                reply_markup=kb.TaskActionMoreMenu())
        return  
    
    
    if callback_data['ACTION'] == 'USERS':   
        user_request = sqlDB.UserRequest.basic_auth(user_data['user_requestID']) 
        user_to = sqlDB.Users1C.get_or_none(id=callback_data['USER']).login
        
        logging.info(f"{call.from_user.id} {user.login_db} - choose user - user to:{user_to} -  taskID:{user_data['taskID']}")
     
        user_request.to_userID = sqlDB.User.name_auth(name=user_to)
        user_request.to_userName = user_to
        user_request.save()
        with suppress(MessageNotModified):
            await bot.edit_message_text(text=f'Подтвердите выбор: {user_request.to_userName}' , 
                                        chat_id = call.from_user.id,
                                        message_id=user_data['start_msgID'],
                                        reply_markup=kb.AddUserKB())
    

async def invite_user (call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
      
    user_data = await state.get_data()
    user_request = sqlDB.UserRequest.basic_auth(user_data['user_requestID'])
    
    user: sqlDB.User = sqlDB.User.basic_auth(user_request.from_userID)    
    DB1C = Database_1C(user.login_db, user.password)
    
    if callback_data['ACTION'] == 'BACK':

        users_list = DB1C.users()
        with suppress(MessageNotModified):
            await bot.edit_message_text(text='Выберите пользователя:', 
                                chat_id = call.from_user.id,
                                message_id = user_data['start_msgID'],
                                reply_markup=kb.UsersMenu(users_list))
        
        
    if callback_data['ACTION'] == 'ACCEPT':
        if user_request.action == 'INVITE':
            logging.info(f"{call.from_user.id} {user.login_db} - invite user:{user_request.to_userName} - taskID:{user_data['taskID']}")
            req = DB1C.AddUsers(user_request.taskID, [user_request.to_userName]) 
            txt = 'Пользователь приглашен'  
            messsage_to = f'{user_request.from_userName} пригласил(а) Вас в задачу {user_request.taskNAME}'
    
        elif user_request.action == 'TRANSFER':
            logging.info(f"{call.from_user.id} {user.login_db} - transfer to user:{user_request.to_userName} - taskID:{user_data['taskID']}")
            req = DB1C.SetRedirect(user_request.taskID, user_request.to_userName)      
            txt = 'Задача передана'
            messsage_to = f'{user_request.from_userName} передал(а) Вам задачу {user_request.taskNAME}'
            
        if req != None:
            await bot.answer_callback_query(call.id, text=req, show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)
            await bot.delete_message(chat_id=call.from_user.id, message_id = call.message.message_id)
            return  
    
        
        if user_request.to_userID:
            new_not = sqlDB.Notifications.new_notification(taskID=user_request.taskID, messageID=0, userID = user_request.to_userID, text = messsage_to)
            new_not.save()
            keyboard = kb.NotificationKB(taskID=user_request.taskID, notificationID=new_not.id)
            
            msg = await bot.send_message(chat_id=user_request.to_userID, text=messsage_to, reply_markup=keyboard)
            new_not.messageID = msg.message_id
            new_not.save()
    
        await bot.answer_callback_query(call.id, text=txt, show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)
        dataDB = DB1C.tasks(params={'id' : user_data['taskID']})[user_data['taskID']]
        task_message, _ = getTaskDescription(dataDB)
                 
        with suppress(MessageNotModified):
            await bot.edit_message_text(text=task_message, 
                                chat_id = call.from_user.id,
                                message_id = user_data['start_msgID'],
                                reply_markup=kb.TaskActionMoreMenu())
            


###  вывести дополнительные варианты
async def show_options(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.reset_state(with_data=False)
    await del_message(call, state)
    mode = callback_data['ACTION']
    
    user_data = await state.get_data()
    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id) 
    logging.info(f"{call.from_user.id} {user.login_db} - show options - taskID:{user_data['taskID']}")

    
    if (mode == 'VARS')|(mode == 'BACK'):
        DB1C = Database_1C(user.login_db, user.password)
        variants = DB1C.GetVariants(user_data['taskID'])
        
        if isinstance(variants, list):
            logging.info(f"{call.from_user.id} {user.login_db} - num options:{len(variants)} - taskID:{user_data['taskID']}")
            keyboard = kb.VarsMenu(variants)
            variants_new = {}
            for i in variants:
                variants_new[i['ЗначениеВарианта']] = i['ПредставлениеВарианта']
           
            await state.update_data(complete_MODE = 'MORE')
            await state.update_data(task_variants = variants_new)

            
        elif variants.find('0') != -1:
            logging.info(f"{call.from_user.id} {user.login_db} - no options available - taskID:{user_data['taskID']}")

            await state.update_data(complete_MODE = 'DONE')
            with suppress(MessageNotModified):
                await bot.edit_message_text(text='Подтвердите выполнение задачи', 
                                    chat_id = call.from_user.id,
                                    message_id = user_data['start_msgID'],
                                    reply_markup=kb.option_kb) 
            
            
            # msg = await call.message.answer('Подтвердите выполнение задачи', reply_markup=kb.option_kb)
            # await state.update_data(add_msgID = msg.message_id)
            return
            
        else:
            await bot.answer_callback_query(call.id, text=variants, show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)
            return
        

    elif mode == 'MOREVARS':
        keyboard = kb.TaskActionMoreMenu()
    await bot.edit_message_reply_markup(chat_id = call.from_user.id,
                                      message_id = call.message.message_id,
                                      reply_markup=keyboard)    
 
       

async def confirm_option(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
    user = sqlDB.User.basic_auth(call.from_user.id)
    user_data = await state.get_data()
    
    logging.info(f"{call.from_user.id} {user.login_db} - confirm option - taskID:{user_data['taskID']}")
    
    variants = user_data['task_variants']
    chosen_var = callback_data['VAR']
    chones_var_name = variants[chosen_var]
    
    await state.update_data(chosen_variant = [chosen_var, chones_var_name]) 
    msg_txt = 'Подтвердите выбор варианта: "{0}"'.format(chones_var_name)

    with suppress(MessageNotModified):
        await bot.edit_message_text(text=msg_txt, 
                            chat_id = call.from_user.id,
                            message_id = user_data['start_msgID'],
                            reply_markup=kb.option_kb) 
    
    # msg = await call.message.answer(msg_txt, reply_markup=kb.option_kb)
    # await state.update_data(add_msgID = msg.message_id)

async def option_accepted(call: types.CallbackQuery,  state: FSMContext): 
    user = sqlDB.User.basic_auth(call.from_user.id) 
    DB1C = Database_1C(user.login_db, user.password) 
    user_data = await state.get_data() 
    
    logging.info(f"{call.from_user.id} {user.login_db} - option_accepted - taskID:{user_data['taskID']}")
    
    if user_data['complete_MODE'] == 'DONE':
        req = DB1C.SetExecute(user_data['taskID'])
        
    elif user_data['complete_MODE'] == 'MORE':
        chosen_variant = user_data['chosen_variant'] 
        req = DB1C.SetVariant(user_data['taskID'], chosen_variant) 
    
    if req != None:
        await bot.answer_callback_query(call.id, text=req, show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)
        return
       
    await bot.answer_callback_query(call.id, text='Выполнено', show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)
    
    # await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await del_files(call, state)
    await full_list_move(call, state)


async def option_declined(call: types.CallbackQuery,  state: FSMContext): 
    user = sqlDB.User.basic_auth(call.from_user.id) 
    DB1C = Database_1C(user.login_db, user.password) 
    user_data = await state.get_data() 
    taskID = user_data['taskID']
    
    logging.info(f"{call.from_user.id} {user.login_db} - option_declined - taskID:{user_data['taskID']}")
    
    dataDB = DB1C.tasks(params={'id' : taskID})[taskID]
    task_message, _ = getTaskDescription(dataDB)

    
    if user_data['complete_MODE'] == 'DONE':
        if isinstance(dataDB, dict):
            is_executor = (dataDB['Исполнитель'].lower() == user.name_1C.lower())
        
        
        with suppress(MessageNotModified):
            await bot.edit_message_text(text=task_message, 
                                chat_id = call.from_user.id,
                                message_id = user_data['start_msgID'],
                                reply_markup=kb.TaskActionMenu(accepted=dataDB['ПринятаКИсполнению'], done=dataDB['Выполнена'], is_executor=is_executor))
        return
        
        
    elif user_data['complete_MODE'] == 'MORE':
        variants = DB1C.GetVariants(taskID)
 
        if isinstance(variants, list):
            logging.info(f"{call.from_user.id} {user.login_db} - num options:{len(variants)} - taskID:{user_data['taskID']}")
            keyboard = kb.VarsMenu(variants)
            variants_new = {}
            for i in variants:
                variants_new[i['ЗначениеВарианта']] = i['ПредставлениеВарианта']
           
            await state.update_data(complete_MODE = 'MORE')
            await state.update_data(task_variants = variants_new)
            
            with suppress(MessageNotModified):
                await bot.edit_message_text(text=task_message, 
                                    chat_id = call.from_user.id,
                                    message_id = user_data['start_msgID'],
                                    reply_markup=keyboard) 
            return

      
async def del_files(call: types.CallbackQuery, state: FSMContext):
    logging.info("delete files")
    user_data = await state.get_data()  
    try:      
        msg_id = user_data['file_msgID']
        for msg in msg_id:
            await bot.delete_message(chat_id=call.from_user.id, message_id=msg)
        await state.reset_state(with_data=False) 
    except Exception as ex:
        pass
        # logging.info(ex)


async def del_message(call: types.CallbackQuery, state: FSMContext):
    logging.info("delete message")
    user_data = await state.get_data()      
    try:
        msg_id = user_data['add_msgID']
        await bot.delete_message(chat_id=call.from_user.id, message_id=msg_id)
        await state.reset_state(with_data=False)
    except Exception as ex:
        pass
        # logging.info(ex)
          

async def del_callback(call: types.CallbackQuery, state: FSMContext):
    logging.info("delete callback")
    if len(call.data.split(':')) > 2:
        print(call.data)
        notification = sqlDB.Notifications.basic_auth(call.data.split(':')[2])
        notification.result = 'HIDDEN'
        notification.save()
    try:
        await call.message.delete()
    except Exception as ex:
        logging.info(ex)
                

    
async def back_vars(call: types.CallbackQuery, state: FSMContext):
    logging.info("back_vars")
    await state.reset_state(with_data=False)
    await del_message(call, state)
    
    user_data = await state.get_data()
    taskID = user_data['taskID']

    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    DB1C = Database_1C(user.login_db, user.password)
    dataDB = DB1C.tasks(params={'id' : taskID})[taskID]
    
    if isinstance(dataDB, dict):
        is_executor = (dataDB['Исполнитель'].lower() == user.name_1C.lower())
    else: 
        return await bot.answer_callback_query(call.id, text = dataDB, show_alert=True, cache_time=BOT_SETTINGS.CACHE_TIME)
    
    task_message, _ = getTaskDescription(dataDB)
    with suppress(MessageNotModified):
        await bot.edit_message_text(text = task_message,
                            chat_id = call.from_user.id,
                            message_id = user_data['start_msgID'],
                            reply_markup=kb.TaskActionMenu(accepted=dataDB['ПринятаКИсполнению'], done=dataDB['Выполнена'], is_executor=is_executor))

async def echo_send(message : types.Message):
    msg = await message.answer ('Нет такой команды')
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg.message_id)
    await message.delete()


async def show_task_notification(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    logging.info("show_task_notification")
    
    taskID = callback_data['TASK_ID']
    
    notification = sqlDB.Notifications.basic_auth(callback_data['NOT_ID'])
    notification.result = 'READ'
    notification.save()
    
    await state.update_data(filter_mode='FULL')
    await state.update_data(pageID=0)
    await state.update_data(taskID=taskID)
    # await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.delete()
     
    await send_task_info(call, state, callback_data)


async def test_command(message : types.Message):
    from notifier import notify_user
    
    value = {'Наименование':'Тестовая задача', 
             'РольИсполнителя': 'Тестовая группа', 
             'Исполнитель': 'БотТест',
             'taskID':'1cf37b5e-e876-11ec-a7a8-d89d67149b66'}
    user = sqlDB.User.name_auth(value['Исполнитель'])
    await notify_user(user=user, msg_type='group', data=value)


    
def reg_handlers_client(dp: Dispatcher):

    dp.register_message_handler(command_start, commands=['start'],  state="*")    
    dp.register_message_handler(test_command, commands=['test'],  state="*")    

    
    ### Фильтры    
    dp.register_callback_query_handler(back_start,        kb.FiltersMenu.CallbackData.FILTER_CB.filter(ACTION=["BACK"]))
    dp.register_callback_query_handler(full_list_move,    kb.StartMenu.CallbackData.START_CB.filter(ACTION=["SHOWTASKS"]))
    dp.register_callback_query_handler(back_to_filteres,  kb.TasksMenu.CallbackData.BACK_CB.filter(ACTION=["BACK"]))

    ### Список задач
    dp.register_callback_query_handler(full_list_tasks, kb.FiltersMenu.CallbackData.FILTER_CB.filter(ACTION=['FULL','USER','FREE','PAST', 'FULL_ALL', 'USER_ALL']))  
    dp.register_callback_query_handler(full_list_tasks, kb.TasksMenu.CallbackData.PAGES_CB.filter(ACTION=["PAGE"]))  
    dp.register_callback_query_handler(full_list_tasks, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=["BACK"]), state="*")  
    
    ### Информация о задаче    
    dp.register_callback_query_handler(send_task_info, kb.TasksMenu.CallbackData.TASKS_CB.filter(ACTION=["TASK"]),  state="*")
    dp.register_callback_query_handler(send_task_info, kb.CompleteMenu.CallbackData.COMPLETE_CB.filter(ACTION=['BACK']),  state="*")
    
    ### Принять задачу
    dp.register_callback_query_handler(accept_task, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=["ACCEPT", "DECLINE"]),  state="*")

    ### Комментарий
    dp.register_callback_query_handler(comment, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=['COMMENT']), state="*")
    dp.register_message_handler(save_comment, state=st.CommentStates.add_comment)

    ### Показать доп.варианты
    dp.register_callback_query_handler(show_options, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=['VARS', 'MOREVARS']), state="*")

    ### Выбрать вариант
    # dp.register_callback_query_handler(complete_task, kb.CompleteMenu.CallbackData.COMPLETE_CB.filter(ACTION=['DONE', 'MORE'])) 
    dp.register_callback_query_handler(confirm_option, kb.VarsMenu.CallbackData.VARS.filter(ACTION=['CHOOSE'])) 
    dp.register_callback_query_handler(option_accepted, Text(contains=('accept_b'), ignore_case=True))
    dp.register_callback_query_handler(option_declined, Text(contains=('back_task'), ignore_case=True))
  
    
    ### Добавить пользователя
    dp.register_callback_query_handler(add_user,          kb.TaskActionMoreMenu.CallbackData.MOREVAR_CB.filter(ACTION=['INVITE', 'TRANSFER']), state="*")
    dp.register_callback_query_handler(choose_user,       kb.UsersMenu.CallbackData.USER_CB.filter())
    dp.register_callback_query_handler(invite_user,       kb.AddUserKB.CallbackData.ADDUSER_CB.filter())
    # dp.register_callback_query_handler(tasksend_reply,    kb.UsersNotification.CallbackData.USER_NOT.filter(ACTION=['ACCEPT', 'DECLINE']))


    ### Добавить файл
    dp.register_callback_query_handler(uploadFile, kb.TaskActionMoreMenu.CallbackData.MOREVAR_CB.filter(ACTION=['FILE']), state="*")
    dp.register_callback_query_handler(del_message,  Text(contains=('cancel_b'), ignore_case=True), state="*") 
    dp.register_callback_query_handler(del_callback,  Text(contains=('cancel_call_b'), ignore_case=True), state="*")
    dp.register_callback_query_handler(back_vars, kb.TaskActionMoreMenu.CallbackData.MOREVAR_CB.filter(ACTION=['BACK']), state="*")   
    dp.register_callback_query_handler(back_vars, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=['BACK']), state="*")
    dp.register_callback_query_handler(back_vars, kb.VarsMenu.CallbackData.VARS.filter(ACTION=['BACK']), state="*")

    dp.register_callback_query_handler(show_task_notification, kb.NotificationKB.CallbackData.NOTIFY_CB.filter(), state="*")
    dp.register_message_handler(echo_send)


