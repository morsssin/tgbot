import re
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
########### FOR TEST ONLY ################
# test_DB = {}

# for i in range(1, 16):
#     test_DB['id0%s' % i] = {'1C_ID':'№ 000%s от 25.04.2022' % i,
#                             'NAME':'Название задачи %s' % i,
#                             'CLIENT':'Клиент:',
#                             'CLIENT_NAME':'Иванов Иван ИП %s' % i,
#                             'DESC':'Описание %s' % i,
#                             'EXEC':'Исполнение:',
#                             'EXEC_NAME':'Дирекция %s' % i,
#                             'RESULT':'07.05.2022 12.25 Принята к исполнению',
#                             'COMMENTS':{'User 1':'Здесь был комментарий 1',
#                                         'User 2':'Здесь был комментарий 2',
#                                         'User 3':'Здесь был комментарий 3',},
#                             'OWNER':'Иванов %s' % i, 
#                             'STATE':'declined'}


users = ['admin', 'admin1', 'client']    
users_pass = {'admin':'pass', 'admin1': 'password', 'client':'password'}
users_chat_id = {'admin':'', 'admin1': '', 'client':''}

actions_var_list = ['Проблема решена', 'Проблема не решена', 'Требуется выезд тех.специалиста', 'Не в нашей юрисдикции']

len_tasks = 30

tools_list = []
works_list = []
for i in range(1, 100):
    tools_list.append('Оборудование №%s' % i)
    works_list.append('Работа №%s' % i)
    


########### FOR TEST ONLY ################
def search_in_list (list_: list, val: str):
    list_res = []
    for item in list_:
        if val.lower() in item.lower():
            list_res.append(item)
    return list_res


def get_key(dict_, value):
    for k, v in dict_.items():
        if v == value:
            return k



class CommentStates(StatesGroup):
    add_comment = State()
    save_comment2 = State()


    
### команда для старта
async def command_start(message : types.Message, state: FSMContext):
    hello_msg = text(bold('Добро пожаловать!'),'\n','Выберите действие:',sep='')   
    msg = await message.answer (hello_msg,reply_markup=kb.auth_kb_no)
    await state.update_data(start_msgID=msg.message_id)




## выбор всех задач
async def full_list_move(call: types.CallbackQuery, state: FSMContext):

    user_data = await state.get_data()
    text_ = text(bold('Доступные фильтры:'))
    await bot.edit_message_text(text=text_, 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=kb.task_list_kb) 
    

async def back_start(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text_ = text(bold('Добро пожаловать!'),'\n','Выберите действие:',sep='')   
    await bot.edit_message_text(text=text_, 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=kb.auth_kb_no)   



async def full_list_taskd(call: types.CallbackQuery, state: FSMContext):
    mode = call.data.split("_")[0]
    page = int(call.data.split("_")[3])
    user_data = await state.get_data()
    
    print(URL)
    print(LOGIN)
    print(PASS)
    
    
    req = requests.get(URL + '/ERP/hs/tg_bot/tasks', headers = {'Accept': 'application/json'}, auth=HTTPBasicAuth(LOGIN, PASS))
    print(req)
    dataDB = req.json()
    
    data_df = pd.json_normalize(dataDB)
    data_df = data_df.replace('01.01.0001 0:00:00', None)
    data_df['ДатаИсполнения'] = pd.to_datetime(data_df['ДатаИсполнения'], dayfirst=True)
    # data_df['Дата'] = pd.to_datetime(data_df['Дата'],  dayfirst=True)

    
    if mode != 'back':
        await state.update_data(filter_mode=mode)
    elif mode == 'back':
        mode = user_data['filter_mode']

    if mode == 'all':
        list_needed = data_df.index.to_list()
        text_ = text(bold('Все задачи:')) 
        
    elif mode == 'user':
        list_needed = data_df.loc[data_df['Исполнитель']=='ED'].index.to_list()
        text_ = text(bold('Мои задачи:'))
        
    elif mode == 'free':
        list_needed = data_df.loc[data_df['Исполнитель']==''].index.to_list()
        text_ = text(bold('Свободные задачи:'))
        
    elif mode == 'past':
        list_needed = data_df.loc[(data_df['ДатаИсполнения'] > dt.datetime.now())&(data_df['Выполнена']=='Нет')].index.to_list()
        text_ = text(bold('Просроченные задачи:'))

    
    num_pages = round((len(list_needed)/len_tasks) + 0.5)

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=7)
    back_button = types.InlineKeyboardButton('◀️ Назад', callback_data='back_to_filteres')


    if num_pages > 1:
        start = len_tasks*(page-1)
        end = len_tasks*page
        
        print(start, end)
    
        for i in list_needed[start:end]:
            date_task = dt.datetime.strptime(dataDB[i]['Дата'], '%d.%m.%Y %H:%M:%S').strftime('%d/%m/%Y')
            button_label = str(date_task) + ' ' + dataDB[i]['Наименование']
            keyboard.add(types.InlineKeyboardButton(button_label, callback_data='id_%s'% i))

            
        keyboard.add(types.InlineKeyboardButton('Стр. 1', callback_data='{0}_tasks_page_1'.format(mode))) 
        for num_page in range(2, num_pages+1):
            keyboard.insert(types.InlineKeyboardButton('Стр. %s' % num_page, callback_data='{0}_tasks_page_{1}'.format(mode, num_page)))
    
    elif num_pages == 1:
        for i in list_needed:
            date_task = dt.datetime.strptime(dataDB[i]['Дата'], '%d.%m.%Y %H:%M:%S').strftime('%d/%m/%Y')
            button_label = str(date_task) + ' ' + dataDB[i]['Наименование']
            keyboard.add(types.InlineKeyboardButton(button_label, callback_data='id_%s'% i))

    keyboard.add(back_button)
    user_data = await state.get_data()
    
    await bot.edit_message_text(text=text_, 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=keyboard)       


async def back_to_filteres (call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    txt =  text(bold('Доступные фильтры:'))
    await bot.edit_message_text(text=txt, 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=kb.task_list_kb) 



 ### выбор описания задачи  
async def send_task_info(call: types.CallbackQuery, state: FSMContext):
    taskID = int(call.data.split("_")[1])
    await state.update_data(taskID=taskID)

    req = requests.get(URL + '/ERP/hs/tg_bot/tasks', auth=HTTPBasicAuth(LOGIN, PASS))
    print(req)
    dataDB = req.json()
    print(taskID)
    date_task = dt.datetime.strptime(dataDB[taskID]['Дата'], '%d.%m.%Y %H:%M:%S').strftime('%d/%m/%Y')

    
    # comments_txt = ''
    # for idx, (key, val) in enumerate(test_DB[taskID]['COMMENTS'].items()):
    #     txt = text(bold(key), ': ', re.escape(val), '\n', sep='')
    #     comments_txt = text(comments_txt, txt, sep='')      
    #     # comments_txt = comments_txt + key + ': ' + val + '\n'
    
    if dataDB[taskID]['Наименование'][:2]==' (':
        task_descr = dataDB[taskID]['Наименование'][2:-1]
    else:
        task_descr = dataDB[taskID]['Наименование']
    
    taskNAME =  text(bold(escape_md(dataDB[taskID]['Номер'])), 'от', escape_md(date_task), ' ',
                        escape_md(task_descr))
    await state.update_data(taskNAME=taskNAME)
    
    task_message = text(bold(dataDB[taskID]['Номер']), ' от ', escape_md(date_task), '\n',
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
    

    
    # task_message = text(task_message, '\n',
    #                     '\n',
    #                     bold('Комментарии:'),'\n',
    #                     comments_txt, sep='')
                        
    if dataDB[taskID]['ПринятаКИсполнению'] == 'Да':
        keyboard = kb.task_actions_kb_accepted
        
    elif dataDB[taskID]['ПринятаКИсполнению'] == 'Нет':
        keyboard = kb.task_actions_kb
    
    user_data = await state.get_data()
    await bot.edit_message_text(text=task_message, 
                        chat_id = call.from_user.id,
                        message_id = user_data['start_msgID'],
                        reply_markup=keyboard)    


    




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
    await CommentStates.add_comment.set()

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

async def del_comment(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await state.reset_state(with_data=False) 


### свернуть задачу
async def hide_message(call: types.CallbackQuery,  state: FSMContext):
    await state.update_data(last_mess_task_id=None)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)












## пригласить пользователя
async def add_user(call: types.CallbackQuery,  state: FSMContext):
    
    mode = call.data.split('_')[1]
    keyboard = types.InlineKeyboardMarkup()    
    for user in users:
        keyboard.add(types.InlineKeyboardButton(user, callback_data='user_{0}_{1}'.format(users_chat_id[user], mode)))
    
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
        text_ = '{0} приглашает вас присоединиться к задаче "{1}"'.format(get_key(users_chat_id, user_data['from_chatID']),taskNAME)
    elif mode_chatID == 'shift':
        text_ = '{0} предлагает вам принять задачу "{1}"'.format(get_key(users_chat_id, user_data['from_chatID']),taskNAME)
  
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
        text_ = '{0} принял задачу "{1}". Выполняется добавление пользователя.'.format(get_key(users_chat_id, to_chatID),taskNAME) 
        await bot.send_message(chat_id=from_chatID, text=escape_md(text_), reply_markup=keyboard)
 
    elif (mode == 'accept')&(mode_chatID == 'shift'):
        text_ = '{0} принял задачу "{1}". Выполняется переадресация задачи.'.format(get_key(users_chat_id, to_chatID),taskNAME) 
        await bot.send_message(chat_id=from_chatID, text=escape_md(text_), reply_markup=keyboard)
                   
    elif mode == 'decline':
        text_ = '{0} отклонил задачу "{1}"'.format(get_key(users_chat_id, to_chatID),taskNAME) 
        await bot.send_message(chat_id=from_chatID, text=escape_md(text_), reply_markup=keyboard)





### выполненные работы
class ToolsStates(StatesGroup):
    find_work_done = State()
    save_work_done = State()

async def add_work_done (call: types.CallbackQuery(),  state: FSMContext):
    await call.message.answer('Выберите вариант для поиска', reply_markup=kb.add_work_done_kb)
    await ToolsStates.find_work_done.set()

async def search_handler(query: types.InlineQuery, state: FSMContext):  
    
    if query.query.split(':')[0] == 'tasks':
        result_list = search_in_list(works_list, query.query.split(':')[1])

        
    elif query.query.split(':')[0] == 'tools':
        result_list = search_in_list(tools_list, query.query.split(':')[1])

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
        
        

### добавить фото/видео
class UploadPhotoState(StatesGroup):
    add_photo = State()
    save_photo = State()


async def uploadPhoto(call: types.CallbackQuery, state: FSMContext):
    msg = await call.message.answer('Добавьте фото или видео:', reply_markup=kb.cancel_kb)
    await state.update_data(photo_msgID = msg.message_id)
    await UploadPhotoState.add_photo.set()



@dp.message_handler(content_types=["photo"], state=UploadPhotoState.add_photo)
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



@dp.message_handler(content_types=["video"], state=UploadPhotoState.add_photo)
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




 

###  вывести дополнительные варианты
async def show_options(call: types.CallbackQuery, state: FSMContext):
    mode = call.data.split("_")[1]
    
    if mode == 'vars':
        task_actions_var_kb = types.InlineKeyboardMarkup(row_width=2)

        for i, var in enumerate(actions_var_list):
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
    txt = actions_var_list[int(mode)].replace('.', '\.')
    user_data = await state.get_data()

    msg_txt = 'Подтвердите присвоение задаче {0} статуста "{1}"'.format(user_data['taskID'], txt)
    await call.message.answer(msg_txt, reply_markup=kb.option_kb)

async def state_var_accept(call: types.CallbackQuery,  state: FSMContext):
    await bot.answer_callback_query(call.id, text='Вариант сохранен', show_alert=True)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        

    
async def back_vars(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    taskID = user_data['taskID']

    req = requests.get(URL + '/ERP/hs/tg_bot/tasks', auth=HTTPBasicAuth(LOGIN, PASS))
    print(req)
    dataDB = req.json()
    
    if dataDB[taskID]['ПринятаКИсполнению'] == 'Да':
        keyboard = kb.task_actions_kb_accepted
        
    elif dataDB[taskID]['ПринятаКИсполнению'] == 'Нет':
        keyboard = kb.task_actions_kb
    

    await bot.edit_message_reply_markup(chat_id = call.from_user.id,
                                  message_id = call.message.message_id,
                                  reply_markup=keyboard)

    
  
async def echo_send(message : types.Message):
    msg = await message.answer ('Нет такой команды')
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg.message_id)
    await message.delete()

    
def reg_handlers_client(dp : Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])


    ### список задач
    dp.register_callback_query_handler(full_list_move, Text(startswith="go_to_tasks"))
    dp.register_callback_query_handler(back_start, Text(startswith="back_start"))
    dp.register_callback_query_handler(back_to_filteres,  Text(startswith="back_to_filteres"))

    dp.register_callback_query_handler(full_list_taskd, Text(contains ="_tasks", ignore_case=True))  
    dp.register_callback_query_handler(send_task_info, Text(startswith="id_"))

    dp.register_callback_query_handler(accept_task, Text(startswith="accept_task"))
    dp.register_callback_query_handler(decline_task, Text(startswith="decline_task"))
    

    # ### комментарий
    # dp.register_callback_query_handler(comment, Text(startswith="comment"), state="*")
    # dp.register_message_handler(save_comment, state=CommentStates.add_comment)
    # dp.register_callback_query_handler(del_comment,  Text(startswith="cancel_b"), state=UploadPhotoState.add_photo)


    ### добавить пользователя
    dp.register_callback_query_handler(add_user, Text(startswith="adduser_"))
    dp.register_callback_query_handler(choose_user, Text(startswith="user_"))
    dp.register_callback_query_handler(send_notification, Text(startswith="users_invite"))
    dp.register_callback_query_handler(tasksend_reply, Text(startswith="tasksend_"))


     ### добавить фото/видео
    dp.register_callback_query_handler(uploadPhoto, Text(startswith="add_photo"), state="*")
    dp.register_callback_query_handler(del_comment,  Text(startswith="cancel_b"), state=CommentStates.add_comment)


    ### выполненные работы
    dp.register_callback_query_handler(add_work_done, Text(startswith="todowork"), state="*")
    dp.register_inline_handler(search_handler, state=ToolsStates.find_work_done)
    dp.register_callback_query_handler(save_work_done, Text(startswith="work_"), state=ToolsStates.find_work_done)


    ### свернуть задачу
    dp.register_callback_query_handler(hide_message,Text(startswith="hide_message"))
    dp.register_callback_query_handler(hide_message,Text(startswith="hide_message"), state=ToolsStates.find_work_done) 

    ### выбрать вариант
    dp.register_callback_query_handler(state_var, Text(startswith="varb_")) 
    dp.register_callback_query_handler(state_var_accept, Text(startswith="accept_b"))
    
 
    dp.register_callback_query_handler(show_options, Text(startswith="show_"))
    dp.register_callback_query_handler(back_vars, Text(startswith="backvar"))

    
    dp.register_message_handler(echo_send)

