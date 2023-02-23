# -*- coding: utf-8 -*-
import asyncio
import logging

from datetime import datetime
from aiogram.types import ParseMode
from aiogram import Bot, exceptions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from app import bot
from database import sqlDB
from keyboards import NotificationKB


class Config:
    NAME = "New_Task_Notify"


async def notify_user(user: sqlDB.User, msg_type: str, data: dict):
    
    logging.info(f"notify_user - {user.chat_id} - {user.login_db}")
    if msg_type == 'user':
        txt = 'Вам наздачена новая задача: {0}'.format(data['Наименование'])
    elif msg_type == 'group':
        txt = 'Группе исполнителей {0} назначена новая задача: {1}'.format(data['РольИсполнителя'],data['Наименование'])
    
    new_not = sqlDB.Notifications.new_notification(taskID=data['taskID'], messageID=0, userID = user.chat_id, text = txt)
    new_not.save()
    keyboard = NotificationKB(taskID=data['taskID'], notificationID=new_not.id)

    try:
        msg = await bot.send_message(chat_id = user.chat_id, text=txt, reply_markup=keyboard, parse_mode=ParseMode.HTML)        
        new_not.messageID = msg.message_id
        new_not.save()
        logging.info(f"notify_user - {user.login_db} - notification send successfull")
    except (exceptions.BotBlocked, exceptions.BadRequest, exceptions.UserDeactivated):
        logging.error(f"notify_user - {user.login_db} - error")


async def run_service():
    logging.info(f'[{Config.NAME}] Сервис запущен!')
    while True:
        from database.DB1C import Database_1C
        from config import DATABASE_1C

        DB1C = Database_1C(DATABASE_1C.LOGIN, DATABASE_1C.PASS, auth=True)
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
                                        'РольИсполнителя' : value['РольИсполнителя'],
                                        'taskID':value['id']}})
            else:
                continue
                   
        if new_tasks != {}:
            logging.info("New tasks updated")
            for key, value in new_tasks.items():
                if value['Исполнитель'] != '':
                    user = sqlDB.User.name_auth(value['Исполнитель'])
                    
                    
                    if isinstance(user, sqlDB.User):
                        await notify_user(user=user, msg_type='user', data=value)
                    else:
                        logging.info("User {0} not found in tg_bot".format(value['Исполнитель']))
                    
                if value['РольИсполнителя'] != '':                    
                    users = roles[value['РольИсполнителя']]
                    for user_ in users:
                        user = sqlDB.User.name_auth(user_)
                        if isinstance(user, sqlDB.User):
                            await notify_user(user=user, msg_type='group', data=value)
                        else:
                            logging.info("User {0} not found in tg_bot".format(user_))

        else:
            logging.info("No new tasks")
            

        sqlDB.Tasks.base_init()
        await asyncio.sleep(60)


async def resend_notifications():
    logging.info('Resend notifications on')
    while True:
        sqlDB.Notifications.delete_old()
        
        query = sqlDB.Notifications.select().where(sqlDB.Notifications.result == 'SENT')
        
        for notification in query:
            
            if (datetime.today() - notification.date).seconds/(60*60) > 24:
                user = sqlDB.User.basic_auth(notification.userID)
                
                await bot.delete_message(chat_id=notification.userID, message_id=notification.messageID)
                      
                new_not = sqlDB.Notifications.new_notification(taskID=notification.taskID, 
                                                               messageID=notification.messageID, 
                                                               userID = notification.userID, 
                                                               text = notification.text)
                new_not.save()
                keyboard = NotificationKB(taskID=notification.taskID, notificationID=new_not.id)
    
                try:
                    msg = await bot.send_message(chat_id = notification.userID, text=notification.text, reply_markup=keyboard, parse_mode=ParseMode.HTML)        
                    new_not.messageID = msg.message_id
                    new_not.save()
                    
                    notification.delete_instance()
                    
                    logging.info(f"resend_notifications - {user.login_db} - notification send successfull")
                except (exceptions.BotBlocked, exceptions.BadRequest, exceptions.UserDeactivated):
                    logging.error(f"resend_notifications - {user.login_db} - error")        
        
        
        await asyncio.sleep(60)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        