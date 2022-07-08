# -*- coding: utf-8 -*-
import typing

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


### Стартовая клавиатура
class StartMenu (InlineKeyboardMarkup):
    def __init__(self):
        super().__init__(row_width=2)
        self.auth  = InlineKeyboardButton('🔑 Авторизация', 
                     callback_data=self.CallbackData.START_CB.new(LEVEL=1, ACTION="AUTH"))
        self.tasks = InlineKeyboardButton('📓 Задачи', 
                     callback_data=self.CallbackData.START_CB.new(LEVEL=1, ACTION="SHOWTASKS"))
        
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
        self.back  = InlineKeyboardButton('◀️ Назад', 
                     callback_data=self.CallbackData.FILTER_CB.new(LEVEL=2, ACTION="BACK"))
        
        self.add(self.full, self.user, self.free, self.past, self.back)

    
    class CallbackData:
        FILTER_CB = CallbackData("FILTER", "LEVEL", "ACTION")


### Список задач
class TasksMenu(InlineKeyboardMarkup):
    def __init__(self, data: typing.Dict, per_page: int = 40, page: int = 0):
        from datetime import datetime as dt
        from aiogram.utils.markdown import text
        
        super().__init__(resize_keyboard=True, row_width=7)
        
        tasks = list(data.items())
        num_pages = round((len(data)/per_page) + 0.5)
        
        for task in tasks[per_page*page : per_page*page + per_page]:
            date_task = dt.strptime(task[1]['Дата'], '%d.%m.%Y %H:%M:%S').strftime('%d/%m/%Y')
            button_label = text(str(date_task), task[1]['Наименование'], sep=' ')
            
            self.add(InlineKeyboardButton(button_label, 
                     callback_data=self.CallbackData.TASKS_CB.new(LEVEL=3, TASK_ID=task[0], PAGE=page, ACTION='TASK')))

        if num_pages > 1:
            self.add(InlineKeyboardButton('С.1', callback_data=self.CallbackData.PAGES_CB.new(LEVEL=3, PAGE=0, ACTION='PAGE')))        
            for page in range(1, num_pages):
                self.insert(InlineKeyboardButton('С.%s' % str(page + 1), callback_data=self.CallbackData.PAGES_CB.new(LEVEL=3, PAGE=page, ACTION='PAGE')))
        
        self.back = InlineKeyboardButton('◀️ Назад', callback_data=self.CallbackData.BACK_CB.new(LEVEL=3, ACTION='BACK'))
        self.add(self.back)
        

    class CallbackData:
        TASKS_CB = CallbackData("TASK", "LEVEL", "TASK_ID", 'PAGE', 'ACTION')
        PAGES_CB = CallbackData("PAGES", "LEVEL", "PAGE", "ACTION")
        BACK_CB = CallbackData("BACK", "LEVEL", "ACTION")



### Меню действия с задачей
class TaskActionMenu(InlineKeyboardMarkup):
    def __init__ (self, accepted : str = 'Нет'):
        super().__init__(row_width=2)
        self.but1  = InlineKeyboardButton('✅ Принять задачу', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="ACCEPT"))
        self.but2  = InlineKeyboardButton('✏️ Комментарий', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="COMMENT"))
        self.but3  = InlineKeyboardButton('❌ Отменить задачу', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="DECLINE"))
        self.but4  = InlineKeyboardButton('▶️ Варианты', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="SHOWVAR"))
        self.but5  = InlineKeyboardButton('▶️ Больше вариантов', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="SHOWMOREVAR"))
        self.but6  = InlineKeyboardButton('◀️ Назад', 
                     callback_data=self.CallbackData.ACTION_CB.new(LEVEL=4, ACTION="BACK"))
        if accepted == 'Нет':
            self.add(self.but1, self.but2, self.but6)
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
    def __init__ (self, user_list: typing.List, action: str):
        super().__init__(row_width=2)
        for user in user_list:
            self.add(InlineKeyboardButton(text=user, callback_data=self.CallbackData.USER_CB.new(LOGIN=user, ACTION=action)))
        
        self.add(InlineKeyboardButton('❌ Отмена', callback_data=self.CallbackData.USER_CB.new(LOGIN=user, ACTION='CANCEL_B')))
                               
    class CallbackData:
        USER_CB = CallbackData("USER", "LOGIN", 'ACTION')
            

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
cancel_button2 = InlineKeyboardButton('❌ Отмена', callback_data='hide_message')
add_work_done_kb.row(works_button, tools_button).add(cancel_button2)

accept_work_done_kb = InlineKeyboardMarkup()
acccept_work_button = InlineKeyboardButton('✅ Принять', callback_data='work_accepted')
decline_work_button = InlineKeyboardButton('❌ Отмена', callback_data='work_declined')
accept_work_done_kb.row(acccept_work_button, decline_work_button)