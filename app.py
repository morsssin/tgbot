# -*- coding: utf-8 -*-
import os
import config
import logging

from aiogram.utils import executor
# from handlers import client, admin
from database.sqlite_db import database as db
from database.DB1C import test_connection



from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.redis import RedisStorage2


logging.basicConfig(level=logging.INFO)


### Создание бота 
storage = RedisStorage2(config.REDIS_HOST, config.REDIS_PORT)
bot = Bot(config.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

### Функции
async def on_startup(_):
    test_connection.ping()
    logging.warning('Bot loaded')

async def on_shutdown(dp):
    logging.warning('Shutting down..')
    # закрытие соединения с БД
    db._conn.close()
    await dp.storage.close()
    # await dp.storage.wait_closed()
    logging.warning("DB Connection closed")



### Запуск бота
if __name__ == "__main__":
    from handlers.client import reg_handlers_client as client_handlers
    from handlers.auth import reg_handlers_auth as auth_handlers

    client_handlers(dp)
    auth_handlers(dp)
    
    # admin.reg_handlers_admin(dp)
    
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown(dp))

    



# HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# # webhook settings
# WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
# WEBHOOK_PATH = f'/webhook/{TOKEN}'
# WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# # webserver settings
# WEBAPP_HOST = '0.0.0.0'
# WEBAPP_PORT = os.getenv('PORT', default=8000)

# async def on_startup(dispatcher):
#     await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


# async def on_shutdown(dispatcher):
#     await bot.delete_webhook()


# @dp.message_handler()
# async def echo(message: types.Message):
#     await message.answer(message.text)


# if __name__ == '__main__':
#    logging.basicConfig(level=logging.INFO)
#    start_webhook(
#        dispatcher=dp,
#        webhook_path=WEBHOOK_PATH,
#        skip_updates=True,
#        on_startup=on_startup,
#        on_shutdown=on_shutdown,
#        host=WEBAPP_HOST,
#        port=WEBAPP_PORT,
#    )
