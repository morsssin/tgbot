# -*- coding: utf-8 -*-
import os
import logging
import sqlite3
# import redis
# import ujson

# import config

import sqlite3 as sq



class Database:
    """ Класс работы с базой данных """
    def __init__(self, name):
        self.name = name
        self._conn = self.connection()
        logging.info("Database connection established")

    def create_db(self):
        # global base, cursor
        connection = sqlite3.connect(f"{self.name}.db")
        logging.info("Database created")
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS auth_data
                          (chatID TEXT PRIMARY KEY, 
                           login TEXT,
                           password TEXT,
                           login_db TEXT
                           )''')
        
                
        cursor.execute('''CREATE TABLE IF NOT EXISTS msgIDs 
                          (user, name, msgID)''')
        connection.commit()
        cursor.close()


    def connection(self):
        db_path = os.path.join(os.getcwd(), f"{self.name}.db")
        if not os.path.exists(db_path):
            self.create_db()
        return sqlite3.connect(f"{self.name}.db")
    
            
    async def add_msgID(self, user, name, value):
        cursor = self._conn.cursor()
        is_existed = cursor.execute('SELECT msgID FROM msgIDs WHERE user == ? AND name == ?', (user, name)).fetchone()
        if is_existed == None:
            cursor.execute('INSERT INTO msgIDs VALUES (?, ?, ?)', (user, name, value))
        else:
            cursor.execute('UPDATE msgIDs SET msgID == ? WHERE user == ? AND name == ?', (value, user, name))
        self._conn.commit()
        cursor.close()
    
    async def get_msgID(self, user, name):
        cursor = self._conn.cursor()
        _id = cursor.execute('SELECT msgID FROM msgIDs WHERE user == ? AND name == ?', (user, name)).fetchone()
        cursor.close()
        return _id

    async def add_user_data(self, data):
        cursor = self._conn.cursor()
        cursor.execute("""INSERT INTO auth_data VALUES (?, ?, ?, ?)""", 
                       (data['chatID'], data['login'], data['password'], data['login_db']))                       
        self._conn.commit()
        cursor.close()        

    async def get_user_data(self, chatID, data_name):
        cursor = self._conn.cursor()
        result = cursor.execute('SELECT ? FROM auth_data WHERE chatID == ?', (data_name, chatID)).fetchone()
        cursor.close()
        return result 

    async def get_chatID(self, login):
        cursor = self._conn.cursor()
        chatID = cursor.execute('SELECT chatID FROM auth_data WHERE login == ?', (login, )).fetchone()
        cursor.close()
        return chatID 
    
    

database = Database('bot_database')

    # def _execute_query(self, query, select=False):
    #     cursor = self._conn.cursor()
    #     cursor.execute(query)
    #     if select:
    #         records = cursor.fetchone()
    #         cursor.close()
    #         return records
    #     else:
    #         self._conn.commit()
    #     cursor.close()


# def sql_start():
#     global base, cur
#     base = sq.connect('bot_database.db')
#     cur = base.cursor()
#     if base:
#         print('Data base connected!')
#     base.execute('CREATE TABLE IF NOT EXISTS auth_data(login TEXT PRIMARY KEY, password TEXT, chatID)')
#     base.commit()
#     base.execute('CREATE TABLE IF NOT EXISTS msgIDs(user, name, msgID)')
#     base.commit()

# async def sql_add_msgID(user, name, value):
#     if cursor.execute('SELECT msgID FROM msgIDs WHERE user == ? AND name == ?', (user, name)).fetchone() == None:
#         print('second')
#         cursor.execute('INSERT INTO msgIDs VALUES (?, ?, ?)', (user, name, value))
#         base.commit()
#     else:        
#         print('first')
#         cursor.execute('UPDATE msgIDs SET msgID == ? WHERE user == ? AND name == ?', (value, user, name))
#         base.commit()



# async def sql_get_msgID(user, name):
#     id_ = cursor.execute('SELECT msgID FROM msgIDs WHERE user == ? AND name == ?', (user, name)).fetchone()
#     return id_





