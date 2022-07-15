# -*- coding: utf-8 -*-
import typing

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from database import sqlDB


### Стартовая клавиатура
class StartMenu (InlineKeyboardMarkup):
    def __init__(self, mode : str = 'auth'):
        super().__init__(row_width=2)
        self.auth  = InlineKeyboardButton('🔑 Авторизация', 
                     callback_data=self.CallbackData.START_CB.new(LEVEL=1, ACTION="AUTH"))
        self.tasks = InlineKeyboardButton('📓 Задачи', 
                     callback_data=self.CallbackData.START_CB.new(LEVEL=1, ACTION="SHOWTASKS"))
        self.change = InlineKeyboardButton('🔑 Сменить пользователя', 
                     callback_data=self.CallbackData.START_CB.new(LEVEL=1, ACTION="UCHANGE"))
        
        if mode =='change':
            self.add(self.change, self.tasks)
        else:
            self.add(self.auth, self.tasks)
        
    class CallbackData:
        START_CB = CallbackData("START", "LEVEL", "ACTION")


### Фильтры
class FiltersMenu(InlineKeyboardMarkup):
    def __init__(self):
        super().__init__(row_width=2)
        self.full  = InlineKeyboardButton('📓 Все задачи', 
                     callback_data=self.CallbackData.FILTER_CB.new(LEVEL=2, ACTION="FULL"))
        self.user  = InlineKeyboardButton('👤 Мои задачи', 
                     callback_data=self.CallbackData.FILTER_CB.new(LEVEL=2, ACTION="USER"))
        self.free  = InlineKeyboardButton('📗 Свободные', 
                     callback_data=self.CallbackData.FILTER_CB.new(LEVEL=2, ACTION="FREE"))
        self.past  = InlineKeyboardButton('📕 Просроченные', 
                     callback_data=self.CallbackData.FILTER_CB.new(LEVEL=2, ACTION="PAST"))
        self.full1  = InlineKeyboardButton('📓 Выполненные', 
                     callback_data=self.CallbackData.FILTER_CB.new(LEVEL=2, ACTION="FULL_ALL"))
        self.user1  = InlineKeyboardButton('👤 Мои выполненные', 
                     callback_data=self.CallbackData.FILTER_CB.new(LEVEL=2, ACTION="USER_ALL"))        
        
        self.back  = InlineKeyboardButton('◀️ Назад', 
                     callback_data=self.CallbackData.FILTER_CB.new(LEVEL=2, ACTION="BACK"))
        
        self.add(self.full, self.user, self.free, self.past, self.full1, self.user1, self.back)

    
    class CallbackData:
        FILTER_CB = CallbackData("FILTER", "LEVEL", "ACTION")


### Список задач
class TasksMenu(InlineKeyboardMarkup):
    def __init__(self, data: typing.Dict, per_page: int = 35, page: int = 0):
        from datetime import datetime as dt
        from aiogram.utils.markdown import text
        
        super().__init__(resize_keyboard=True, row_width=7)
        
        tasks = list(data.items())
        num_pages = round((len(data)/per_page) + 0.5)
        print(per_page*page, per_page*page + per_page)
        
        for task in tasks[per_page*page : per_page*page + per_page]:
            date_task = dt.strptime(task[1]['Дата'], '%d.%m.%Y %H:%M:%S').strftime('%d/%m/%Y')
            button_label = text(str(date_task), task[1]['Наименование'], sep=' ')
            
            self.add(InlineKeyboardButton(button_label, 
                     callback_data=self.CallbackData.TASKS_CB.new(LEVEL=3, TASK_ID=task[0], PAGE=page, ACTION='TASK')))
        
        print(num_pages)
        if (num_pages > 1)&(num_pages < 11):
            self.add(InlineKeyboardButton('С.1', callback_data=self.CallbackData.PAGES_CB.new(LEVEL=3, PAGE=0, ACTION='PAGE')))        
            for page in range(1, num_pages):
                self.insert(InlineKeyboardButton('С.%s' % str(page + 1), callback_data=self.CallbackData.PAGES_CB.new(LEVEL=3, PAGE=page, ACTION='PAGE')))
 
        if num_pages > 10:
            page_down10 = page - 9 if page > 8 else 0
            page_up10 = page + 9 if page < num_pages-10 else num_pages-1
            
            page_down = page - 1 if page > 0 else 0
            page_up = page + 1 if page < num_pages-1 else num_pages-1
            
            self.but1 = InlineKeyboardButton('с.{page}/{num_pages}'.format(page=page+1, num_pages=num_pages), callback_data=self.CallbackData.PAGES_CB.new(LEVEL=3, PAGE=page, ACTION='PAGE'))
            self.but2 = InlineKeyboardButton('⏪ 10', callback_data=self.CallbackData.PAGES_CB.new(LEVEL=3, PAGE=page_down10, ACTION='PAGE'))
            self.but3 = InlineKeyboardButton('◀️ 1', callback_data=self.CallbackData.PAGES_CB.new(LEVEL=3, PAGE=page_down, ACTION='PAGE'))
            self.but4 = InlineKeyboardButton('⏩ 10', callback_data=self.CallbackData.PAGES_CB.new(LEVEL=3, PAGE=page_up10, ACTION='PAGE'))
            self.but5 = InlineKeyboardButton('▶️️ 1', callback_data=self.CallbackData.PAGES_CB.new(LEVEL=3, PAGE=page_up, ACTION='PAGE'))
            self.add(self.but2, self.but3, self.but1, self.but5, self.but4) 
           
        self.back = InlineKeyboardButton('◀️ Назад', callback_data=self.CallbackData.BACK_CB.new(LEVEL=3, ACTION='BACK'))
        self.add(self.back)
        

    class CallbackData:
        TASKS_CB = CallbackData("TASK", "LEVEL", "TASK_ID", 'PAGE', 'ACTION')
        PAGES_CB = CallbackData("PAGES", "LEVEL", "PAGE", "ACTION")
        BACK_CB = CallbackData("BACK", "LEVEL", "ACTION")



### Меню действия с задачей
class TaskActionMenu(InlineKeyboardMarkup):
    def __init__ (self, accepted : str = 'Нет', done : str = 'Нет'):
        super().__init__(row_width=2)
        self.but1  = InlineKeyboardButton('✅ Принять задачу', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="ACCEPT"))
        self.but2  = InlineKeyboardButton('✏️ Комментарий', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="COMMENT"))
        self.but3  = InlineKeyboardButton('❌ Отменить задачу', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="DECLINE"))
        self.but4  = InlineKeyboardButton('▶️ Варианты', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="VARS"))
        self.but5  = InlineKeyboardButton('▶️ Больше вариантов', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="MOREVARS"))
        self.but6  = InlineKeyboardButton('◀️ Назад', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="BACK"))
        if accepted == 'Нет':
            self.add(self.but1, self.but2, self.but6)
        
        elif done == 'Да':
            self.add(self.but2).add(self.but6)
        
        else: 
            self.add(self.but3, self.but2, self.but4, self.but5, self.but6)


    class CallbackData:
        ACTION_CB = CallbackData("ACTION", "LEVEL", 'ACTION')


### Меню действия с задачей (больше)
class TaskActionMoreMenu(InlineKeyboardMarkup):
    def __init__ (self):
        super().__init__(row_width=2)
        self.but1  = InlineKeyboardButton('👥 Пригласить пользователя', 
                     callback_data=self.CallbackData.MOREVAR_CB.new(LEVEL=5, ACTION="INVITE"))
        self.but2  = InlineKeyboardButton('☑️ Выполненные работы', 
                     callback_data=self.CallbackData.MOREVAR_CB.new(LEVEL=5, ACTION="WORK"))
        self.but3  = InlineKeyboardButton('🛅 Передать задачу', 
                     callback_data=self.CallbackData.MOREVAR_CB.new(LEVEL=5, ACTION="TRANSFER"))
        self.but4  = InlineKeyboardButton('📷 Фото / видео', 
                     callback_data=self.CallbackData.MOREVAR_CB.new(LEVEL=5, ACTION="FILE"))
        self.but5  = InlineKeyboardButton('◀️ Назад', 
                     callback_data=self.CallbackData.MOREVAR_CB.new(LEVEL=5, ACTION="BACK"))

        self.add(self.but1, self.but2, self.but3, self.but4, self.but5)


    class CallbackData:
        MOREVAR_CB = CallbackData("MOREVAR", "LEVEL", 'ACTION')

class UsersMenu(InlineKeyboardMarkup):
    def __init__ (self, user_list: typing.List):
        super().__init__(row_width=2)
        for user in user_list:
            if sqlDB.User.get_or_none(login=user) != None:
                user_ = sqlDB.User.login_auth(user)
                chat_id = user_.chat_id
            else:
                chat_id = '_'
            self.add(InlineKeyboardButton(text=user, callback_data=self.CallbackData.USER_CB.new(CHAT_ID=chat_id, ACTION='USERS')))
        
        self.add(InlineKeyboardButton('❌ Отмена', callback_data=self.CallbackData.USER_CB.new(CHAT_ID='_', ACTION='CANCEL_B')))
                               
    class CallbackData:
        USER_CB = CallbackData("USERS", "CHAT_ID", 'ACTION')
     
        
class UsersNotification(InlineKeyboardMarkup):
    def __init__ (self, user_requestID: str):
        super().__init__(row_width=2)
        self.but1 = InlineKeyboardButton('✅ Принять', callback_data = self.CallbackData.USER_NOT.new(ACTION='ACCEPT', REPLY=user_requestID))
        self.but2 = InlineKeyboardButton('❌ Отклонить', callback_data = self.CallbackData.USER_NOT.new(ACTION='DECLINE', REPLY=user_requestID))
        
        self.add(self.but1, self.but2)
        
    class CallbackData:
        USER_NOT = CallbackData("USERS_N", 'ACTION', 'REPLY')
        
    
     

### клавиатура отмены действия
cancel_kb = InlineKeyboardMarkup()
cancel_button = InlineKeyboardButton('❌ Отмена', callback_data='cancel_b')
cancel_kb.add(cancel_button)

### клафиатура принятия варианта
option_kb = InlineKeyboardMarkup()
accept_button = InlineKeyboardButton('✅ Принять', callback_data='accept_b')
option_kb.row(accept_button, cancel_button)

### клавиатура - пользователь для приглашения
add_user_kb = InlineKeyboardMarkup()
add_user_b = InlineKeyboardButton('✅ Принять', callback_data='users_invite')
add_user_kb.row(add_user_b, cancel_button)

### клавиатура для выполненных работ
add_work_done_kb = InlineKeyboardMarkup()
works_button = InlineKeyboardButton('Работы', switch_inline_query_current_chat ='tasks:')
tools_button = InlineKeyboardButton('Оборудование', switch_inline_query_current_chat ='tools:')
# cancel_button2 = InlineKeyboardButton('❌ Отмена', callback_data='hide_message')
add_work_done_kb.row(works_button, tools_button).add(cancel_button)

accept_work_done_kb = InlineKeyboardMarkup()
acccept_work_button = InlineKeyboardButton('✅ Принять', callback_data='work_accepted')
decline_work_button = InlineKeyboardButton('❌ Отмена', callback_data='work_declined')
accept_work_done_kb.row(acccept_work_button, decline_work_button)