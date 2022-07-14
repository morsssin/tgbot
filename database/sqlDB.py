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
    
    def login_auth(login):
        return User.get_or_none(User.login == login)
        
        
class UserRequest(BaseModel):
    id = CharField(primary_key=True)
    taskID = TextField()
    taskNAME = TextField()
    
    from_userID: User = ForeignKeyField(User)
    to_userID: User = ForeignKeyField(User)
    action: str = TextField()
    decision: str = TextField()
    
    @staticmethod
    def basic_auth(id):
        return UserRequest.get_or_none(id=id)
    
    def get_text(self):
        if self.action == 'INVITE':
            txt = f'{0} приглашает вас присоединиться к задаче "{1}"'.format(self.from_userID.login, self.taskNAME)
            
        elif self.action == 'TRANSFER':
            txt = f'{0} предлагает вам принять задачу "{1}"'.format(self.from_userID.login, self.taskNAME)
        return txt
            
    def det_text_reply(self):
        if self.decision == 'ACCEPTED':
            if self.action == 'INVITE':
                txt = '<b>{0}</b> принял задачу "{1}". Выполняется добавление пользователя.'.format(self.to_userID.login,self.taskNAME)
                
            elif self.action == 'TRANSFER':
                txt = '<b>{0}</b> принял задачу "{1}". Выполняется переадресация задачи.'.format(self.to_userID.login,self.taskNAME)
        else:
            txt = '{0} отклонил задачу "{1}"'.format(self.to_userID.login,self.taskNAME)
        return txt


def create_tables():

    db.connect()    
    db.create_tables([User, UserRequest])
    
def close_conn():
    db.close()
