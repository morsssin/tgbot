# -*- coding: utf-8 -*-
import os


TOKEN = os.getenv('TOKEN')

URL = os.getenv('URL')
PASS = os.getenv('PASS')
LOGIN = os.getenv('LOGIN')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASS = os.getenv('REDIS_PASS')


DEBUG_MODE = False

LEN_TASKS = 30

# import configparser
# config = configparser.ConfigParser().read('config.ini')
# print(config.sections())

