# -*- coding: utf-8 -*-
import os
import logging
import asyncio
import datetime


from aiogram.utils import executor
from database import sqlDB, DB1C
from load_bot import bot, dp

import notifier
import urllib3

async def on_startup(dp):
    DB1C.test_connection.ping()
    sqlDB.create_tables()
    logging.info('Bot loaded')

async def on_shutdown(dp):
    logging.info('Shutting down..')
    sqlDB.close_conn()
    await dp.storage.close()
    logging.info("DB Connection closed")


### Запуск бота
if __name__ == "__main__":
    from handlers import client, auth
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        
    filename = os.path.join(logs_dir, datetime.date.today().strftime("%d_%m_%Y") + "_log.log")
    logging.basicConfig(level=logging.INFO, filename=filename, filemode="a",
                        format='[%(asctime)s] %(filename)s [LINE:%(lineno)d] #%(levelname)-8s %(message)s')
     
    client.reg_handlers_client(dp)
    auth.reg_handlers_auth(dp)

    loop = asyncio.get_event_loop()
    loop.create_task(notifier.run_service())
    loop.create_task(notifier.resend_notifications())
    loop.create_task(notifier.update_database())

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
