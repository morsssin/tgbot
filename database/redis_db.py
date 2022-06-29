# -*- coding: utf-8 -*-

import redis
import config


redis_client = redis.Redis(config.REDIS_HOST, config.REDIS_PORT, db=0)

redis_client.close()
