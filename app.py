# -*- coding: utf-8 -*-

import logging
import asyncio


from aiogram.utils import executor
from database import sqlDB, DB1C
from load_bot import bot, dp

import notifier
import middleware


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
    dp.setup_middleware(middleware.Middleware())
    
    loop = asyncio.get_event_loop()
    loop.create_task(notifier.run_service())
    
    
    
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)


    # loop = asyncio.new_event_loop()
    # tasks = [loop.create_task(notifier.run_service())]
    # loop.run_forever()
    

        
    

