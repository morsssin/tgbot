# -*- coding: utf-8 -*-

import json
import logging
import requests

from config import URL, LOGIN, PASS
from requests.auth import HTTPBasicAuth
# from urllib3.exceptions import NewConnectionError, MaxRetryError, ConnectTimeoutError
# from requests.exceptions import ConnectionError, ConnectTimeout


def check_connection(request):
    if request.status_code == 200:
        logging.info('Соединение с 1С установлено')
    else:
        logging.error('Ошибка {0}. Текст: {1}'.format(request.status_code, request.text))
        return 'Ошибка {0}. Текст: {1}'.format(request.status_code, request.text)


class Database_1C:
    def __init__(self, URL, LOGIN, PASS):
        self.url = URL
        self.login = LOGIN
        self.password = PASS   
        self.session = requests.Session()        
        self.timeout = 2

    def ping (self):
        try:
            self.r = self.session.get(self.url + '/ERP/hs/tg_bot/ping', auth=HTTPBasicAuth(self.login, self.password), timeout=self.timeout)
            return check_connection(self.r)
        
        except Exception as error:
            logging.error(error)
            return         

    
    def tasks (self, params={}): # DONE 
        """
        Parameters
        ----------
        Author     : str, имя пользователя
        id         : str, уникальный идентификатор задачи
        DateBegin  : str в формате 20221231235959, дата начала
        DateEnd    : str в формате 20221231235959. Дата окончания.
        Executed   : str, значения “yes” или “no” – выполнена (да или нет).
        Importance : str, значения “низкая”, “обычная”  или “высокая”  - важность.
        Accepted   : str, значения “yes” или “no” – принята (да или нет).
        Condition  : str, значения “активен” или “остановлен”  - состояние задачи
        Executor   : str, имя пользователя (Исполнителя задачи).

        """ 
        
        r = self.session.get(self.url + '/ERP/hs/tg_bot/tasks', auth=HTTPBasicAuth(self.login, self.password), params=params)
        
        if check_connection(r) != None:
            return
        
        if r.json()['Errors'] != []:        
            logging.warning('Ошибки при загрузке БД: {0}'.format(r.json()['Errors'].join('/n')))        
            
        dataDB = r.json()['Tasks']      
        dataDB = { dataDB[key]['id'] : value for key, value in enumerate(dataDB) }
        return dataDB

    def users(self): # DONE WORK
        r = self.session.get(self.url + '/ERP/hs/tg_bot/users', auth=HTTPBasicAuth(self.login, self.password))
        if check_connection(r) != None:
            return
        users = r.json()['Users']
        return users

    def GetVariants(self, taskID: str): # DONE WORK
        r = self.session.get(self.url + '/ERP/hs/tg_bot/getvariants', auth=HTTPBasicAuth(self.login, self.password), params={'id':taskID})
        if check_connection(r) != None:
            if r.json()['Errors'] != []:        
                return 'Ошибки при загрузке БД: {0}'.format('/n'.join(r.json()['Errors']))
            else:               
                return check_connection(r)
                
        variants = r.json()['Variants']
        return variants

            
    def SetAccept(self, taskID: str, accept: str): # DONE WORK
        data = {"id" : taskID, 'Accept' : accept}
        r = self.session.post(self.url + '/ERP/hs/tg_bot/setaccept', auth=HTTPBasicAuth(self.login, self.password), json=data)
        return check_connection(r)      

        
    def SetComment(self, taskID: str, comment: str, user : str): # DONE WORK
        data = {"id": taskID, "Comment": comment, "user": user}
        r = self.session.post(self.url + '/ERP/hs/tg_bot/setcomment', auth=HTTPBasicAuth(self.login, self.password), json=data)
        return check_connection(r)      



    def SetFile(self, taskID, file64, file_name, file_extension):
        data = {"id": taskID, "file": file64, "name": file_name, 'extension': file_extension}
        r = self.session.post(self.url + '/ERP/hs/tg_bot/setfile', auth=HTTPBasicAuth(self.login, self.password), json=data)
        return check_connection(r)      

        
    def SetRedirect(self, taskID: str, user : str): # DONE WORK
        data = {"id": taskID, "user": user}
        r = self.session.post(self.url + '/ERP/hs/tg_bot/setredirect', auth=HTTPBasicAuth(self.login, self.password), json=data)
        return check_connection(r)      

        
    def AddUsers(self, taskID: str,  users : list): # DONE при приглашении никак не отображается в задаче
        data = {"id": taskID, "users": users}
        r = self.session.post(self.url + '/ERP/hs/tg_bot/addusers', auth=HTTPBasicAuth(self.login, self.password), json=data)
        return check_connection(r)      

    def SetExecutor(self, taskID: str,  user : str): # DONE WORK
        data = {"id": taskID, "executor": user}
        r = self.session.post(self.url + '/ERP/hs/tg_bot/setexecutor', auth=HTTPBasicAuth(self.login, self.password), json=data)
        return check_connection(r)      

        
test_connection = Database_1C(URL, LOGIN, PASS)
