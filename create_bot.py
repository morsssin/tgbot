# -*- coding: utf-8 -*-
import os
import logging

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook

from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

TOKEN = os.getenv('TOKEN')
URL = os.getenv('URL')
PASS = os.getenv('PASS')
LOGIN = os.getenv('LOGIN')


bot = Bot(token=os.getenv('TOKEN'), parse_mode=types.ParseMode.MARKDOWN_V2)
dp = Dispatcher(bot, storage=storage)



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

