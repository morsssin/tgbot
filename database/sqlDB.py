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
db = SqliteDatabase(r'C:\Users\ПеньковДА\Desktop\tgbot\tgbot\bot_database.db', pragmas={'journal_mode': 'wal', 
                                                'foreign_keys': "on",
                                                'wal_autocheckpoint': 10})


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
        user = User.select().where(User.login_db == login.lower()).first()
        return user.chat_id
    
    def login_auth(login):
        user = User.select().where(User.login_db == login.lower()).first()
        return user
 
class Users1C(BaseModel):
    id = AutoField(primary_key=True)
    login = CharField()

    @staticmethod
    def base_init():
        from database.DB1C import Database_1C
        from config import DATABASE_1C

        DB1C = Database_1C(DATABASE_1C.LOGIN, DATABASE_1C.PASS)
        users = DB1C.users()  
        
        data = []
        
        for user in users:
            data.append({'login' : user})
            
        for record in data:
            Users1C.get_or_create(**record)
            
    def login_auth(login):
        user = Users1C.select().where(Users1C.login == login).first()
        return user
       
        
class UserRequest(BaseModel):
    id = CharField(primary_key=True)
    taskID = TextField()
    taskNAME = TextField()
    
    from_userID = CharField()
    from_userName = CharField()
    # to_userID = CharField(null=True)
    to_userName = CharField(null=True)
    action: str = TextField()
    # decision: str = TextField(null=True)

    @staticmethod
    def new_request(taskID: str, 
                    taskNAME: str,
                    from_userID: [str, int],
                    from_userName: [str],
                    action: str,
                    ):
        request_id = generate_uuid()
        request = UserRequest.create(id=request_id, 
                                     taskID=taskID, 
                                     taskNAME=taskNAME,
                                     from_userID=from_userID,
                                     from_userName=from_userName,
                                     action=action,
                                     )
        return request



    
    @staticmethod
    def basic_auth(id):
        return UserRequest.get_or_none(id=id)
    
    # def get_text(self):
    #     if self.action == 'INVITE':
    #         txt = '<b>{0}</b> приглашает вас присоединиться к задаче \n\n{1}'.format(self.from_userName, self.taskNAME)
            
    #     elif self.action == 'TRANSFER':
    #         txt = '<b>{0}</b> предлагает вам принять задачу \n\n{1}'.format(self.from_userName, self.taskNAME)
    #     return txt
            
    # def det_text_reply(self):
    #     if self.decision == 'ACCEPT':
    #         if self.action == 'INVITE':
    #             txt = '<b>{0}</b> принял задачу "{1}". Выполняется добавление пользователя.'.format(self.to_userName,self.taskNAME)
                
    #         elif self.action == 'TRANSFER':
    #             txt = '<b>{0}</b> принял задачу "{1}". Выполняется переадресация задачи.'.format(self.to_userName,self.taskNAME)
    #     else:
    #         txt = '<b>{0}</b> отклонил задачу "{1}"'.format(self.to_userName,self.taskNAME)
    #     return txt

class File(BaseModel):
    tgID = TextField(primary_key=True)
    taskID = TextField()
    ftype = TextField()
    name = TextField(null=True)
    extension = TextField(null=True)
    description = TextField(null=True)
    size = BitField()
    date = DateTimeField()
    
    @staticmethod
    def basic_auth(tgID):
        return File.get_or_none(tgID=tgID)

class Tasks(BaseModel):
    id = AutoField(primary_key=True)
    date = DateTimeField()
    taskID = TextField()
    task_name = TextField(null=True)
    executor = TextField(null=True)
    group_executors = TextField(null=True)
    
    
    @staticmethod
    def base_init():
        from database.DB1C import Database_1C
        from config import DATABASE_1C

        DB1C = Database_1C(DATABASE_1C.LOGIN, DATABASE_1C.PASS)
        dataDB = DB1C.tasks(params={'Executed':'no', 'Accepted': 'no'})  
        
        data = []
        
        for key, value in dataDB.items():
            data.append({'date' : value['Дата'],
                         'taskID' : key,
                         'task_name' : value['Наименование'],
                         'executor' : value['Исполнитель'],
                         'group_executors': value['РольИсполнителя']})
            
        for record in data:
            Tasks.get_or_create(**record)
    

def create_tables():
    # db.connect()    
    db.create_tables([User, UserRequest, File, Tasks, Users1C])
    Tasks.base_init()
    Users1C.base_init()
    
def close_conn():
    db.close()
