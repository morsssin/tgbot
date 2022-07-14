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

from config import LEN_TASKS, URL, DEBUG_MODE
from app import dp, bot

### 
from database.DB1C import Database_1C
from database import sqlDB
# from test_db import test_DB, users, users_chat_id, actions_var_list

logging.basicConfig(level=logging.INFO)

# db.get_user_data(call.from_user.id, 'login')
# db.get_user_data(call.from_user.id, 'login_db')
# db.get_user_data(call.from_user.id, 'password')
  

def get_key(dict_, value):
    for k, v in dict_.items():
        if v == value:
            return k
    
### команда для старта
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
    

## выбор всех задач
async def back_start(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data() 
    msg_text = text(hbold('Добро пожаловать!'),'\n','Выберите действие:',sep='')
    await bot.edit_message_text(text=msg_text, 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=kb.StartMenu(mode='change'))   


## выбор всех задач
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
 
    

    
async def back_to_filteres (call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await full_list_move (call, state)


async def full_list_taskd(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    
    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    print(user.chat_id, user.login)
    
    text_mode = {'FULL' : {'text' : text(hbold('Все задачи:')), 'params' : {'Executed':'no'}},
                 'FULL_ALL' : {'text' : text(hbold('Все задачи:')), 'params' : {'Executed':'yes'}},
                 'USER' : {'text' : text(hbold('Мои задачи:')), 'params' : {'Executed':'no', 'Executor': user.login}},
                 'USER_ALL' : {'text' : text(hbold('Мои задачи:')), 'params' : {'Executor': user.login, 'Executed':'yes'}},
                 'FREE' : {'text' : text(hbold('Свободные задачи:')), 'params' : {'Executed':'no', 'Accepted' : 'no'}},
                 'PAST' : {'text' : text(hbold('Просроченные задачи:')), 
                           'params' : {'DateBegin': '20001231235959', 
                                       'DateExecuted'  : dt.now().strftime('%Y%m%d%H%M%S'), 
                                       'Executed' : 'no'}}}
    
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
     
    if isinstance(user, sqlDB.User):
        DB1C = Database_1C(URL, user.login_db, user.password)
        dataDB = DB1C.tasks(text_mode[mode]['params'])
    else:
        return await bot.answer_callback_query(call.id, text = 'Пользователь не найден в базе данных. Пожалуйста, пройдите авторизацию.', show_alert=True)        
    
    if isinstance(dataDB, dict):
        await bot.edit_message_text(text=text_mode[mode]['text'], 
                            chat_id = call.from_user.id,
                            message_id = user_data['start_msgID'],
                            reply_markup=kb.TasksMenu(data = dataDB, page=page))
    else: 
        return await bot.answer_callback_query(call.id, text = 'По данному фильтру нет задач.', show_alert=True)



### выбор описания задачи  
# @dp.callback_query_handler(kb.TasksMenu.CallbackData.TASKS_CB.filter(ACTION=["TASK"]))
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


    await bot.edit_message_text(text=task_message, 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=kb.TaskActionMenu(accepted=dataDB['ПринятаКИсполнению'], done=dataDB['Выполнена']))



### принять задачу
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
        
    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    DB1C = Database_1C(URL, user.login_db, user.password)
    DB1C.setaccept(taskID=user_data['taskID'], accept=accept)
    
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
    print(user_data['taskID'], message.text, user.login)
    req = DB1C.setcomment(user_data['taskID'], message.text, user.login)
    
    if req != None:
        msg = await message.answer('Комментарий не может быть загружен. Ошибка {0}. Обратитесь к администратору.'.format(req))
        await asyncio.sleep(1)
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

async def del_message(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await state.reset_state(with_data=False) 


### добавить фото/видео
async def uploadFile(call: types.CallbackQuery, state: FSMContext):
    msg = await call.message.answer('Добавьте фото или видео:', reply_markup=kb.cancel_kb)
    await state.update_data(photo_msgID = msg.message_id)
    await st.UploadFileState.add_file.set()


@dp.message_handler(content_types=["photo", "video"], state=st.UploadFileState.add_file)
async def saveFile(message: types.Message,  state: FSMContext):
    user_data = await state.get_data()
    print(message.content_type)
    
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


# @dp.message_handler(content_types=["photo", "video"], state=st.UploadFileState.add_file)


## пригласить пользователя
@dp.callback_query_handler(kb.TaskActionMoreMenu.CallbackData.MOREVAR_CB.filter(ACTION=['INVITE', 'TRANSFER']))
async def add_user(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
    
    user_data = await state.get_data()
    
    user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
    DB1C = Database_1C(URL, user.login_db, user.password)       

    user_request = sqlDB.UserRequest(taskID=user_data['taskID'],
                                     taskNAME = user_data['taskNAME'],
                                     from_userID = user,
                                     to_userID = None,
                                     action = callback_data['ACTION'],
                                     decision = 'DECLINED')    
    print(user_request)
    print(user_request.id)
    
       
    users_list = DB1C.users()
    print(users_list)

    msg = await call.message.answer('Выберите пользователя:', reply_markup=kb.UsersMenu(users_list))
    await state.update_data(choose_user_msgID = msg.message_id)
    await state.update_data(user_requestID = user_request.id)

@dp.callback_query_handler(kb.UsersMenu.CallbackData.USER_CB.filter(ACTION=['USERS']))
async def choose_user(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
    
    user_data = await state.get_data()
    user_request = sqlDB.UserRequest.basic_auth(user_data['user_requestID'])
    user_request.to_userID = sqlDB.User.login_auth(callback_data['LOGIN'])
    print(user_request.to_userID)

    await bot.edit_message_text(text='Подтвердите выбор' ,
                                chat_id = call.from_user.id, 
                                message_id=user_data['choose_user_msgID'],
                                reply_markup=kb.add_user_kb)
    

@dp.callback_query_handler(Text(startswith="users_invite"))
async def send_notification(call: types.CallbackQuery,  state: FSMContext):
      
    user_data = await state.get_data()
    user_request = sqlDB.UserRequest.basic_auth(user_data['user_requestID'])
    
    msg = await bot.send_message(chat_id=user_request.to_userID.chat_id, 
                                     text=user_request.get_text(),
                                     reply_markup=kb.UsersNotification(user_request.id))
    
    await state.update_data(ask_msgID = msg.message_id)  
    await bot.delete_message(chat_id=call.from_user.id, message_id = call.message.message_id)


@dp.callback_query_handler(kb.UsersNotification.CallbackData.USER_NOT.filter(ACTION=['ACCEPT']))
async def tasksend_reply(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
    
    await bot.delete_message(chat_id=call.from_user.id, message_id = call.message.message_id)
    user_request = sqlDB.UserRequest.basic_auth(callback_data['REPLY'])
    user_request.decision = 'ACCEPTED'
    
    keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Cкрыть уведомление', 'cancel_b')) 
    await bot.send_message(chat_id=user_request.from_userID.chat_id, text=user_request.det_text_reply(), reply_markup=keyboard)




# ###  вывести дополнительные варианты
# async def show_options(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
#     mode = callback_data['ACTION']
    
#     if mode == 'vars':
#         task_actions_var_kb = types.InlineKeyboardMarkup(row_width=2)

#         for i, var in enumerate(actions_var_list):
#             task_actions_var_kb.insert(types.InlineKeyboardButton(var, callback_data='varb_%s' % i))
#         back_var__button = types.InlineKeyboardButton('◀️ Назад', callback_data='backvar')
#         task_actions_var_kb.insert(back_var__button)
#     elif mode == 'morevars':
#         task_actions_var_kb = kb.TaskActionMoreMenu()
#     await bot.edit_message_reply_markup(chat_id = call.from_user.id,
#                                      message_id = call.message.message_id,
#                                      reply_markup=task_actions_var_kb)    
        

# async def state_var(call: types.CallbackQuery,  state: FSMContext):
#     mode = call.data.split("_")[1]
#     txt = actions_var_list[int(mode)].replace('.', '\.')
#     user_data = await state.get_data()

#     msg_txt = 'Подтвердите присвоение задаче {0} статуста "{1}"'.format(user_data['taskID'], txt)
#     await call.message.answer(msg_txt, reply_markup=kb.option_kb)

# async def state_var_accept(call: types.CallbackQuery,  state: FSMContext):
#     await bot.answer_callback_query(call.id, text='Вариант сохранен', show_alert=True)
#     await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

      

    
# async def back_vars(call: types.CallbackQuery, state: FSMContext):
#     user_data = await state.get_data()
#     taskID = user_data['taskID']


#     if DEBUG_MODE:
#         dataDB = test_DB[taskID]       
#     else:
#         user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
#         DB1C = Database_1C(URL, user.login_db, user.password)
#         dataDB = DB1C.tasks(params={'id' : taskID})[taskID]
#         print(dataDB)
     

#     await bot.edit_message_reply_markup(
#                         chat_id = call.from_user.id,
#                         message_id = user_data['start_msgID'],
#                         reply_markup=kb.TaskActionMenu(accepted=dataDB['ПринятаКИсполнению'], done=dataDB['Выполнена']))



    
# ## пригласить пользователя
# async def add_user(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
    
#     action = callback_data['ACTION']
    
#     user: sqlDB.User = sqlDB.User.basic_auth(call.from_user.id)
#     user_request: sqlDB.UserRequest = sqlDB.UserRequest()
#     user_request.from_user
    
    
#     DB1C = Database_1C(URL, user.login_db, user.password)
#     users_list = DB1C.users()
    
#     users_list = users_list + users # TODO только для теста
    
    
#     # user_data = await state.update_data(user_action = action)
    
#     user_list = users
#     else:
#         None # TODO: добавить подгрузку списка из 1с
       
#     msg = await call.message.answer('Выберите пользователя:', reply_markup=kb.UsersMenu(user_list=user_list, action=action))
#     await state.update_data(choose_user_msgID = msg.message_id)

# # TODO: добавить исключение для тех кого нет еще в боте и обновлять бд при каждом вызове переадресации

# async def choose_user(call: types.CallbackQuery,  state: FSMContext, callback_data: dict):
    
#     await state.update_data(user_login = callback_data['LOGIN'])
#     await state.update_data(from_chatID = get_chatID(callback_data['LOGIN']))
    
#     user  = callback_data['LOGIN']
    
    
#     await state.update_data(from_chatID = call.from_user.id)
#     await state.update_data(to_chatID = call.data.split("_")[1])
#     await state.update_data(mode_chatID = call.data.split("_")[2])
    
#     user_data = await state.get_data()
#     await bot.edit_message_text(text='Подтвердите выбор' ,
#                                 chat_id = call.from_user.id, 
#                                 message_id=user_data['choose_user_msgID'],
#                                 reply_markup=kb.add_user_kb)
    

# async def send_notification(call: types.CallbackQuery,  state: FSMContext):
#     user_data = await state.get_data()
#     taskID = user_data['taskID']
#     to_chatID = user_data['to_chatID']
#     from_chatID = user_data['from_chatID']
#     mode_chatID = user_data['mode_chatID']
    
#     taskNAME = user_data['taskNAME']
    
#     if mode_chatID == 'invite':
#         text_ = '{0} приглашает вас присоединиться к задаче "{1}"'.format(get_key(tdb.users_chat_id, user_data['from_chatID']),taskNAME)
#     elif mode_chatID == 'shift':
#         text_ = '{0} предлагает вам принять задачу "{1}"'.format(get_key(tdb.users_chat_id, user_data['from_chatID']),taskNAME)
  
#     reply_kb = types.InlineKeyboardMarkup()
#     callback_data_accept = 'tasksend_accept_{0}_{1}_{2}_{3}'.format(taskID, from_chatID, to_chatID, mode_chatID)
#     callback_data_decline = 'tasksend_decline_{0}_{1}_{2}_{3}'.format(taskID, from_chatID, to_chatID, mode_chatID)
    
#     accept_task_button = types.InlineKeyboardButton('✅ Принять', callback_data = callback_data_accept)
#     decline_task_button = types.InlineKeyboardButton('❌ Отклонить', callback_data = callback_data_decline)
#     reply_kb.row(accept_task_button, decline_task_button)
    
#     msg = await bot.send_message(chat_id=user_data['to_chatID'], 
#                                      text=escape_md(text_),
#                                      reply_markup=reply_kb)
#     await state.update_data(ask_msgID = msg.message_id)
#     await bot.delete_message(chat_id=call.from_user.id, message_id = call.message.message_id)


# async def tasksend_reply(call: types.CallbackQuery,  state: FSMContext):
    
#     await bot.delete_message(chat_id=call.from_user.id, message_id = call.message.message_id)
    
#     mode = call.data.split('_')[1]
#     taskID = int(call.data.split('_')[2])
#     from_chatID = call.data.split('_')[3]
#     to_chatID = float(call.data.split('_')[4])
#     mode_chatID = call.data.split('_')[5]



#     req = requests.get(URL + '/ERP/hs/tg_bot/tasks', auth=HTTPBasicAuth(LOGIN, PASS))
#     dataDB = req.json()
#     date_task = dt.datetime.strptime(dataDB[taskID]['Дата'], '%d.%m.%Y %H:%M:%S').strftime('%d/%m/%Y')
    
#     if dataDB[taskID]['Наименование'][:2]==' (':
#         task_descr = dataDB[taskID]['Наименование'][2:-1]
#     else:
#         task_descr = dataDB[taskID]['Наименование']

#     taskNAME =  text(bold(escape_md(dataDB[taskID]['Номер'])), 'от', escape_md(date_task), ' ',
#                         escape_md(task_descr))

#     hide_button = types.InlineKeyboardButton('Cкрыть уведомление', callback_data='hide_message')
#     keyboard = types.InlineKeyboardMarkup().add(hide_button)

#     if (mode == 'accept')&(mode_chatID == 'invite'):
#         text_ = '{0} принял задачу "{1}". Выполняется добавление пользователя.'.format(get_key(tdb.users_chat_id, to_chatID),taskNAME) 
#         await bot.send_message(chat_id=from_chatID, text=escape_md(text_), reply_markup=keyboard)
 
#     elif (mode == 'accept')&(mode_chatID == 'shift'):
#         text_ = '{0} принял задачу "{1}". Выполняется переадресация задачи.'.format(get_key(tdb.users_chat_id, to_chatID),taskNAME) 
#         await bot.send_message(chat_id=from_chatID, text=escape_md(text_), reply_markup=keyboard)
                   
#     elif mode == 'decline':
#         text_ = '{0} отклонил задачу "{1}"'.format(get_key(tdb.users_chat_id, to_chatID),taskNAME) 
#         await bot.send_message(chat_id=from_chatID, text=escape_md(text_), reply_markup=keyboard)
 


async def echo_send(message : types.Message):
    msg = await message.answer ('Нет такой команды')
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg.message_id)
    await message.delete()



    
def reg_handlers_client(dp : Dispatcher):
    
    
    dp.register_message_handler(command_start, commands=['start'])
    
    dp.register_callback_query_handler(back_start,        kb.FiltersMenu.CallbackData.FILTER_CB.filter(ACTION=["BACK"]))
    dp.register_callback_query_handler(full_list_move,    kb.StartMenu.CallbackData.START_CB.filter(ACTION=["SHOWTASKS"]))
    dp.register_callback_query_handler(back_to_filteres,  kb.TasksMenu.CallbackData.BACK_CB.filter(ACTION=["BACK"]))


    dp.register_callback_query_handler(full_list_taskd, kb.FiltersMenu.CallbackData.FILTER_CB.filter(ACTION=['FULL','USER','FREE','PAST', 'FULL_ALL', 'USER_ALL']))  
    dp.register_callback_query_handler(full_list_taskd, kb.TasksMenu.CallbackData.PAGES_CB.filter(ACTION=["PAGE"]))  
    dp.register_callback_query_handler(full_list_taskd, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=["BACK"]))  
    dp.register_callback_query_handler(send_task_info, kb.TasksMenu.CallbackData.TASKS_CB.filter(ACTION=["TASK"]))
    
    dp.register_callback_query_handler(accept_task, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=["ACCEPT", "DECLINE"]))


    # ### комментарий
    dp.register_callback_query_handler(comment, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=['COMMENT']), state="*")
    dp.register_message_handler(save_comment, state=st.CommentStates.add_comment)
    dp.register_callback_query_handler(del_message,  Text(contains=('cancel_b'), ignore_case=True), state="*")

    # # ### добавить пользователя
    # dp.register_callback_query_handler(add_user, kb.TaskActionMoreMenu.CallbackData.MOREVAR_CB.filter(ACTION=['INVITE', 'TRANSFER']))
    # dp.register_callback_query_handler(choose_user, Text(startswith="user_"))
    # dp.register_callback_query_handler(send_notification, Text(startswith="users_invite"))
    # dp.register_callback_query_handler(tasksend_reply, Text(startswith="tasksend_"))


    # # добавить файл
    # dp.register_callback_query_handler(uploadFile, kb.TaskActionMoreMenu.CallbackData.MOREVAR_CB.filter(ACTION=['FILE']), state="*")
 


    # dp.register_callback_query_handler(show_options, kb.TaskActionMenu.CallbackData.ACTION_CB.filter(ACTION=['vars', 'morevars']))
    # dp.register_callback_query_handler(back_vars, kb.TaskActionMoreMenu.CallbackData.MOREVAR_CB.filter(ACTION=['BACK']))

    
    dp.register_message_handler(echo_send)

