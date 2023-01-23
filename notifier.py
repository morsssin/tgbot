# -*- coding: utf-8 -*-
import asyncio
import logging


from aiogram.types import ParseMode
from aiogram import Bot, exceptions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from app import bot
from database import sqlDB



class Config:
    NAME = "New_Task_Notify"


async def notify_user(user: sqlDB.User, msg_type: str, data: dict): 
    if msg_type == 'user':
        txt = 'Вам наздачена новая задача: {0}'.format(data['Наименование'])
    elif msg_type == 'group':
        txt = 'Группе исполнителей {0} новая задача: {1}'.format(data['РольИсполнителя'],data['Наименование'])
           
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton('Скрыть', callback_data='cancel_call_b')
    keyboard.add(button)

    try:
        await bot.send_message(chat_id = user.chat_id, text=txt, reply_markup=keyboard, parse_mode=ParseMode.HTML)  
    except (exceptions.BotBlocked, exceptions.BadRequest, exceptions.UserDeactivated):
        pass


async def run_service():
    logging.info(f'[{Config.NAME}] Сервис запущен!')
    while True:
        from database.DB1C import Database_1C
        from config import DATABASE_1C

        DB1C = Database_1C(DATABASE_1C.LOGIN, DATABASE_1C.PASS)
        try_connection = True
        
        while try_connection:
            dataDB = DB1C.tasks(params={'Executed':'no', 'Accepted': 'no'})
            roles = DB1C.GetRolesFull()

            if (isinstance(dataDB, dict))&(isinstance(roles, dict)):
                try_connection = False
            else:
                logging.info("No connection to 1C")
                await asyncio.sleep(60)

        query = sqlDB.Tasks.select(sqlDB.Tasks.taskID).dicts()
        id_list = [row['taskID'] for row in query]
        
        new_tasks = {}       
        for key, value in dataDB.items():
            if key not in id_list:
                new_tasks.update({key: {'Наименование': value['Наименование'],
                                        'Исполнитель' : value['Исполнитель'],
                                        'РольИсполнителя' : value['РольИсполнителя']}})
            else:
                continue
                   
        if new_tasks != {}:
            logging.info("New tasks updated")
            for key, value in new_tasks.items():
                if value['Исполнитель'] != '':
                    user = sqlDB.User.login_auth(value['Исполнитель'])
                    
                    
                    if isinstance(user, sqlDB.User):
                        await notify_user(user, msg_type='user', data=value)
                    else:
                        logging.info("User {0} not found in tg_bot".format(value['Исполнитель']))
                    
                if value['РольИсполнителя'] != '':                    
                    users = roles[value['РольИсполнителя']]
                    for user_ in users:
                        user = sqlDB.User.login_auth(user_)
                        if isinstance(user, sqlDB.User):
                            await notify_user(user, msg_type='group', data=value)
                        else:
                            logging.info("User {0} not found in tg_bot".format(user_))

        else:
            logging.info("No new tasks")
            

        sqlDB.Tasks.base_init()
        await asyncio.sleep(60)
