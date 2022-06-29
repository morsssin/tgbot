# -*- coding: utf-8 -*-

from aiogram.types import (ReplyKeyboardMarkup, 
                           KeyboardButton,  
                           InlineKeyboardMarkup, 
                           InlineKeyboardButton)

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

