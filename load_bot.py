# -*- coding: utf-8 -*-
import config
import redis

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2


storage = RedisStorage2(config.DATABASE_REDIS.REDIS_HOST, config.DATABASE_REDIS.REDIS_PORT)
bot = Bot(config.BOT_SETTINGS.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

