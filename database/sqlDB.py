# -*- coding: utf-8 -*-
import os
import logging
import sqlite3 as sq

from peewee import *

def generate_uuid(length: int = 11) -> str:
    import string
    import random 
    uuid = ""
    template = list(string.digits + string.ascii_letters)
    for x in range(1, length):
        uuid = uuid + random.choice(template)
    return uuid

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
    to_userID: User = ForeignKeyField(User, null=True)
    action: str = TextField()
    decision: str = TextField(default='DECLINED')

    @staticmethod
    def new_request(taskID: str, 
                    taskNAME: str,
                    from_userID: [str, int],
                    action: str,
                    ):
        request_id = generate_uuid()
        request = UserRequest.create(id=request_id, 
                                     taskID=taskID, 
                                     taskNAME=taskNAME,
                                     from_userID=from_userID,
                                     action=action,
                                     )
        return request



    
    @staticmethod
    def basic_auth(id):
        return UserRequest.get_or_none(id=id)
    
    def get_text(self):
        if self.action == 'INVITE':
            txt = '<b>{0}</b> приглашает вас присоединиться к задаче "{1}"'.format(self.from_userID.login, self.taskNAME)
            
        elif self.action == 'TRANSFER':
            txt = '<b>{0}</b> предлагает вам принять задачу "{1}"'.format(self.from_userID.login, self.taskNAME)
        return txt
            
    def det_text_reply(self):
        if self.decision == 'ACCEPT':
            if self.action == 'INVITE':
                txt = '<b>{0}</b> принял задачу "{1}". Выполняется добавление пользователя.'.format(self.to_userID.login,self.taskNAME)
                
            elif self.action == 'TRANSFER':
                txt = '<b>{0}</b> принял задачу "{1}". Выполняется переадресация задачи.'.format(self.to_userID.login,self.taskNAME)
        else:
            txt = '<b>{0}</b> отклонил задачу "{1}"'.format(self.to_userID.login,self.taskNAME)
        return txt


def create_tables():

    db.connect()    
    db.create_tables([User, UserRequest])
    
def close_conn():
    db.close()
