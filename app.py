# -*- coding: utf-8 -*-

import logging

from aiogram.utils import executor
from database import sqlDB, DB1C
from load_bot import bot, dp


### Функции
async def on_startup(dp):
    DB1C.test_connection.ping()
    sqlDB.create_tables()
    logging.info('Bot loaded')

async def on_shutdown(dp):
    # закрытие соединения с БД
    logging.warning('Shutting down..')
    sqlDB.close_conn
    await dp.storage.close()
    # await dp.storage.wait_closed()
    logging.warning("DB Connection closed")
    
    # await bot.close()


### Запуск бота
if __name__ == "__main__":
    from handlers import client, auth
    
    client.reg_handlers_client(dp)
    auth.reg_handlers_auth(dp)
        
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)

