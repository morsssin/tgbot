# -*- coding: utf-8 -*-
import os
import config
import logging

from aiogram.utils import executor
from database import sqlDB, DB1C

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


storage = RedisStorage2(config.REDIS_HOST, config.REDIS_PORT)
bot = Bot(config.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

