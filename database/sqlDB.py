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

def get_data_from_dataDB(dataDB):
    data = []
    for key, value in dataDB.items():
        data.append({'date': datetime.strptime(value['Дата'], '%d.%m.%Y %H:%M:%S'),
                     'taskID': key,
                     'task_name': value['Наименование'],
                     'executor': value['Исполнитель'],
                     'group_executors': value['РольИсполнителя'],
                     'number': value['Номер'],
                     'date_1c': value['Дата'],
                     'name': value['Наименование'],
                     'completed': value['Выполнена'],
                     'author': value['Автор'],
                     'group_of_executors': value['ГруппаИсполнителейЗадач'],
                     'execution_date': value['ДатаИсполнения'],
                     'start_date': value['ДатаНачала'],
                     'date_of_acceptance_and_execution': value['ДатаПринятияКИсполнению'],
                     'description': value['Описание'],
                     'subject': value['Предмет'],
                     'accepted_to_implementation': value['ПринятаКИсполнению'],
                     'execution_result': value['РезультатВыполнения'],
                     'status_business_process': value['СостояниеБизнесПроцесса'],
                     'period_of_execution': value['СрокИсполнения'],
                     'crm_execution_option': value['CRM_ВариантВыполнения'],
                     'crm_iteration': value['CRM_Итерация'],
                     'crm_contact_person': value['CRM_КонтактноеЛицо'],
                     'crm_partner': value['CRM_Партнер'],
                     'crm_forwarded': value['CRM_Переадресована'],
                     'crm_route_point': value['CRM_ТочкаМаршрута'],
                     'performance': value['Представление'],
                     'comment': value['Комментарий'],
                     'additional_executors': value['ДополнительныеИсполнители'],
                     })
    return data



#  Создание базы данных
db = SqliteDatabase(r'bot_database.db', pragmas={'journal_mode': 'wal', 
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
    taskID = TextField(unique=True)
    task_name = TextField(null=True)
    executor = TextField(null=True)
    group_executors = TextField(null=True)

    number = TextField(null=True)
    date_1c = TextField(null=True)
    name = TextField(null=True)
    completed = TextField(null=True)
    author = TextField(null=True)
    group_of_executors = TextField(null=True)
    execution_date = TextField(null=True)
    start_date = TextField(null=True)
    date_of_acceptance_and_execution = TextField(null=True)
    description = TextField(null=True)
    subject = TextField(null=True)
    accepted_to_implementation = TextField(null=True)
    execution_result = TextField(null=True)
    status_business_process = TextField(null=True)
    period_of_execution = TextField(null=True)
    crm_execution_option = TextField(null=True)
    crm_iteration = TextField(null=True)
    crm_contact_person = TextField(null=True)
    crm_partner = TextField(null=True)
    crm_forwarded = TextField(null=True)
    crm_route_point = TextField(null=True)
    performance = TextField(null=True)
    comment = TextField(null=True)
    additional_executors = TextField(null=True)

    @staticmethod
    def base_init(dataDB=None):
        from database.DB1C import Database_1C
        from config import DATABASE_1C

        if not dataDB:
            try:
                DB1C = Database_1C(DATABASE_1C.LOGIN, DATABASE_1C.PASS, auth=True)
                dataDB = DB1C.tasks()
            except:
                logging.warning('Ошибки при загрузке БД')

        if isinstance(dataDB, dict):
            data = get_data_from_dataDB(dataDB)
            for record in data:
                result = (Tasks.insert(**record).on_conflict('replace').execute())
    @staticmethod
    def update_DB(dataDB):
        if isinstance(dataDB, dict):
            data = get_data_from_dataDB(dataDB)
            for record in data:
                # Tasks.get_or_create(**record)
                result = (Tasks.insert(**record).on_conflict('replace').execute())


            
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

    @staticmethod
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
