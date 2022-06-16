# -*- coding: utf-8 -*-
import os
import logging

from create_bot import dp 
from aiogram.utils import executor
from handlers import client, admin

logging.basicConfig(level=logging.INFO)


async def on_startup(_):
    print('Я РОДИЛСЯ')


client.reg_handlers_client(dp)
admin.reg_handlers_client(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
