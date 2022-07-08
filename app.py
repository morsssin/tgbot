# -*- coding: utf-8 -*-
import os
import config
import logging

from aiogram.utils import executor
# from handlers import client, admin
from database import sqlDB, DB1C



from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.redis import RedisStorage2
# from aiogram.contrib.fsm_storage.memory import MemoryStorage


logging.basicConfig(level=logging.INFO)


### Создание бота 
storage = RedisStorage2(config.REDIS_HOST, config.REDIS_PORT)
bot = Bot(config.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

### Функции
async def on_startup(_):
    DB1C.test_connection.ping()
    sqlDB.create_tables()
    logging.warning('Bot loaded')

async def on_shutdown(dp):
    logging.warning('Shutting down..')
    # закрытие соединения с БД
    sqlDB.close_conn
    dp.storage.close()
    # await dp.storage.wait_closed()
    logging.warning("DB Connection closed")



### Запуск бота
if __name__ == "__main__":
    from handlers.client import reg_handlers_client as client_handlers
    from handlers.auth import reg_handlers_auth as auth_handlers

    client_handlers(dp)
    auth_handlers(dp)
    
    # admin.reg_handlers_admin(dp)
    
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown= on_shutdown(dp))


