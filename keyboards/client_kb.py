from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, 
                           InlineKeyboardMarkup, InlineKeyboardButton)



#### клавиатура авторизации
# auth_kb_no = ReplyKeyboardMarkup(resize_keyboard=True)
# auth_kb_yes = ReplyKeyboardMarkup(resize_keyboard=True)

# login_button_no = KeyboardButton('Авторизация')
# login_button_yes = KeyboardButton('YES_Авторизация')
# task_button = KeyboardButton('Перейти к задачам')

# auth_kb_no.row(login_button_no, task_button)
# auth_kb_yes.row(login_button_yes, task_button)

auth_kb_no  = InlineKeyboardMarkup()
login_button_no = InlineKeyboardButton('🔑 Авторизация', callback_data='auth')
task_button = InlineKeyboardButton('📓 Задачи', callback_data='go_to_tasks')
auth_kb_no.row(login_button_no, task_button)


### клавиатура списка задач и фильтра
# task_list_kb = ReplyKeyboardMarkup(resize_keyboard=True)
# full_button = KeyboardButton('Все задачи')
# user_button = KeyboardButton('Мои задачи')
# free_button = KeyboardButton('Свободные задачи')
# past_button = KeyboardButton('Просроченные задачи')
# # undate_button = KeyboardButton('Обновить список')
# back_button = KeyboardButton('Назад')


task_list_kb = InlineKeyboardMarkup()
full_button = InlineKeyboardButton('📓 Все задачи', callback_data='all_tasks_page_1')
user_button = InlineKeyboardButton('👤 Мои задачи', callback_data='user_tasks_page_1')
free_button = InlineKeyboardButton('📗 Свободные', callback_data='free_tasks_page_1')
past_button = InlineKeyboardButton('📕 Просроченные', callback_data='past_tasks_page_1')
back_button = InlineKeyboardButton('◀️ Назад', callback_data='back_start')

task_list_kb.row(full_button,user_button)
task_list_kb.row(free_button, past_button)
task_list_kb.add(back_button)


### клавиатура действий с задачей - 1
task_actions_kb = InlineKeyboardMarkup()
task_actions_kb_accepted = InlineKeyboardMarkup()
button_1 = InlineKeyboardButton('✅ Принять задачу', callback_data='accept_task')
button_2 = InlineKeyboardButton('✏️ Комментарий', callback_data='comment')
button_3 = InlineKeyboardButton('◀️ Назад',callback_data='back_tasks_page_1')

button_4 = InlineKeyboardButton('❌ Отменить задачу', callback_data='decline_task')
button_5 = InlineKeyboardButton('▶️ Варианты', callback_data='show_vars')
button_6 = InlineKeyboardButton('▶️ Больше вариантов',callback_data='show_morevars')

task_actions_kb.row(button_1,button_2)
task_actions_kb.add(button_3)

task_actions_kb_accepted.row(button_4, button_2)
task_actions_kb_accepted.row(button_5, button_6)
task_actions_kb_accepted.add(button_3)



### клавиатура вариантов
more_options_kb = InlineKeyboardMarkup()
task_users_button = InlineKeyboardButton('👥 Пригласить пользователя', callback_data='adduser_invite')
todo_task_button = InlineKeyboardButton(' ☑️ Выполненные работы', callback_data='todowork')
transfer_task_button = InlineKeyboardButton('🛅 Передать задачу', callback_data='adduser_shift' )
upload_file_button = InlineKeyboardButton('📷 Фото / видео', callback_data='add_photo')
back_var_button = InlineKeyboardButton('◀️ Назад', callback_data='backvar')

more_options_kb.row(task_users_button,todo_task_button)
more_options_kb.row(transfer_task_button, upload_file_button)
more_options_kb.add(back_var_button)

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