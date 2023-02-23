# -*- coding: utf-8 -*-
import os
import logging
import sqlite3 as sq

from peewee import *
from datetime import datetime

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
    login_db: str = CharField(default="tgbottestuser")
    password: str = CharField(default="tort101")
    name_1C: str = CharField()

    
    @staticmethod
    def basic_auth(chat_id):
        return User.get_or_none(chat_id=chat_id)
    
    def name_auth(name):
        user = User.select().where(User.name_1C == name).first()
        return user
    
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

        DB1C = Database_1C(DATABASE_1C.LOGIN, DATABASE_1C.PASS, auth=True)
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
    to_userID = CharField(null=True)
    to_userName = CharField(null=True)
    action: str = TextField()

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

        DB1C = Database_1C(DATABASE_1C.LOGIN, DATABASE_1C.PASS, auth=True)
        dataDB = DB1C.tasks(params={'Executed':'no', 'Accepted': 'no'})  
        
        data = []
        
        for key, value in dataDB.items():
            data.append({'date' : datetime.strptime(value['Дата'],'%d.%m.%Y %H:%M:%S') ,
                         'taskID' : key,
                         'task_name' : value['Наименование'],
                         'executor' : value['Исполнитель'],
                         'group_executors': value['РольИсполнителя']})
            
        for record in data:
            Tasks.get_or_create(**record)
            
class Notifications(BaseModel):
    id = CharField(primary_key=True)
    taskID = CharField(null=True)
    messageID = CharField(null=True)
    userID = CharField(null=True)
    date = DateTimeField()
    text = CharField(null=True)
    result = CharField(default='SENT')
    

    @staticmethod
    def new_notification(taskID: [str, int], messageID:[str, int], userID: [str, int], text: str):
        id_ = generate_uuid(7)
        new = Notifications.create(id=id_,
                                   taskID=taskID,
                                   messageID=messageID,
                                   userID=userID,
                                   text = text,
                                   date=datetime.today())
        return new
    
    @staticmethod
    def basic_auth(id):
        return Notifications.get_or_none(id=id)  
    
    def delete_old():
        query = Notifications.select().where(Notifications.result != 'SENT')
        for item in query:
            item.delete_instance()

def create_tables():
    # db.connect()    
    db.create_tables([User, UserRequest, File, Tasks, Users1C, Notifications])
    Tasks.base_init()
    Users1C.base_init()
    
def close_conn():
    db.close()
