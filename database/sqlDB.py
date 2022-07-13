# -*- coding: utf-8 -*-
import os
import logging
import sqlite3 as sq

from peewee import *

#  Создание базы данных
db = SqliteDatabase('bot_database.db', pragmas={'journal_mode': 'wal', 'foreign_keys': "on"})


class BaseModel(Model):
    class Meta:
        database = db
        

class User(BaseModel):
    chat_id = BigAutoField()
    login: str = CharField()
    password: str = CharField(default="tort101")
    login_db: str = CharField(default="tgbottestuser")

    
    @property
    def get_login(self):
        return self.login
    
    def get_password(self):
        return self.password
    
    @staticmethod
    def basic_auth(chat_id):
        return User.get_or_none(chat_id=chat_id)
    
    def get_chat_id(login):
        return User.get_or_none(User.login == login).chat_id
    
    
        
class UserRequest(BaseModel):
    requestID = AutoField()
    from_user: User = ForeignKeyField(User)
    to_user: User = ForeignKeyField(User)
    action: str = TextField()
    decision: str = TextField()
    text: str = TextField()


def create_tables():

    db.connect()    
    db.create_tables([User, UserRequest])
    
def close_conn():
    db.close()
