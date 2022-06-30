# -*- coding: utf-8 -*-

import json
import logging
import requests

# from config import URL, LOGIN, PASS
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import NewConnectionError, MaxRetryError, ConnectTimeoutError
from requests.exceptions import ConnectionError, ConnectTimeout

URL = 'http://10.10.100.150:8079'
PASS = 'tgbottestuser'
LOGIN = 'tort101'

def check_connection(request):
    if request:
        logging.INFO('Соединение с 1С установлено')
        return True
    
    else:
        logging.error('Ошибка {0}. Текст: {1}'.format(request.status_code, request.text))
        ### TODO отправить уведомление об ошибке в чат            
        return False


class Database_1C:
    def __init__(self, URL, LOGIN, PASS):
        self.url = URL
        self.login = LOGIN
        self.password = PASS   
        self.session = requests.Session()        
        self.timeout = 2
                
        # try:
        #     requests.get(self.url + '/ERP/hs/tg_bot/ping', auth=HTTPBasicAuth(self.login, self.password), timeout=self.timeout)
        #     logging.info('Соединение с 1С установлено')
        #     return True
        
        # except (requests.exceptions.ConnectionError, ConnectTimeout, MaxRetryError, NewConnectionError) as error:
        #     logging.error(error)
        #     return 

    def ping (self):     
        try:
            r = self.session.get(self.url + '/ERP/hs/tg_bot/ping', auth=HTTPBasicAuth(self.login, self.password), timeout=self.timeout)
            return check_connection(r)
        
        except Exception as error:
            # MaxRetryError, NewConnectionError, ConnectTimeoutError
            logging.error(error)
            return         

    
    def tasks (self, params={}):
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

        """ 
        r = self.session.get(self.url + '/ERP/hs/tg_bot/tasks', auth=HTTPBasicAuth(self.login, self.password), params=params)
        
        if check_connection(r) != True:
            return
        
        if r.json()['Errors'] != []:        
            logging.warning('Ошибки при загрузке БД: {0}'.format(r.json()['Errors'].join('/n')))        
            
        dataDB = r.json()['Tasks']
        dataDB = { dataDB[key]['id'] : value for key, value in dataDB.items() }
        return dataDB
            
    def SetAccept(self, taskID: str, accept: str):
        # TODO: добавить метод исполнителя
        data = json.dumps({"id" : taskID, 'Accept' : accept}, ensure_ascii=False)
        r = self.session.get(self.url + '/ERP/hs/tg_bot/SetAccept', auth=HTTPBasicAuth(self.login, self.password), json=data)
        if check_connection(r) != True:
            return
        
    def SetComment(self, taskID: str, comment: str, user : str):
        data = json.dumps({"id": taskID, "Comment": comment, "user": user}, ensure_ascii=False)
        r = self.session.get(self.url + '/ERP/hs/tg_bot/SetComment', auth=HTTPBasicAuth(self.login, self.password), data=data)
        if check_connection(r) != True:
            return

    def SetRedirect(self, taskID: str, comment: str, user : str):
        # TODO: добавить метод исполнителя
        data = json.dumps({"id": taskID, "user": user}, ensure_ascii=False)
        r = self.session.get(self.url + '/ERP/hs/tg_bot/SetRedirect', auth=HTTPBasicAuth(self.login, self.password), data=data)
        if check_connection(r) != True:
            return

    def SetFile(self, taskID, file64, file_name, file_extension):
        data = json.dumps({"id": taskID, "file": file64, "name": file_name, 'extension': file_extension}, ensure_ascii=False)
        r = self.session.get(self.url + '/ERP/hs/tg_bot/SetFile', auth=HTTPBasicAuth(self.login, self.password), data=data)
        if check_connection(r) != True:
            return

test_connection = Database_1C(URL, LOGIN, PASS)
# test_connection.ping()

