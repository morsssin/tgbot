# -*- coding: utf-8 -*-

import json
import warnings
import logging
import requests
import pandas as pd

from config import DATABASE_1C
from base64 import b64encode
from requests._internal_utils import to_native_string
from requests.compat import basestring, str, urlparse
from cryptography.fernet import Fernet



def _basic_auth_str(username, password):

    if not isinstance(username, basestring):
        warnings.warn(
            "Non-string usernames will no longer be supported in Requests "
            "3.0.0. Please convert the object you've passed in ({!r}) to "
            "a string or bytes object in the near future to avoid "
            "problems.".format(username),
            category=DeprecationWarning,
        )
        username = str(username)

    if not isinstance(password, basestring):
        warnings.warn(
            "Non-string passwords will no longer be supported in Requests "
            "3.0.0. Please convert the object you've passed in ({!r}) to "
            "a string or bytes object in the near future to avoid "
            "problems.".format(type(password)),
            category=DeprecationWarning,
        )
        password = str(password)
    # -- End Removal --

    if isinstance(username, str):
        username = username.encode("utf-8")

    if isinstance(password, str):
        password = password.encode("utf-8")

    authstr = "Basic " + to_native_string(
        b64encode(b":".join((username, password))).strip()
    )

    return authstr


class AuthBase:

    def __call__(self, r):
        raise NotImplementedError("Auth hooks must be callable.")


class BasicAuth(AuthBase):

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __eq__(self, other):
        return all(
            [
                self.username == getattr(other, "username", None),
                self.password == getattr(other, "password", None),
            ]
        )

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers["Authorization"] = _basic_auth_str(self.username, self.password)
        return r




def check_connection(request):
    if request.status_code == 200:
        logging.info('Соединение с 1С установлено')
    else:
        try:
            logging.warning('Ошибки при загрузке БД: {0}'.format('/n'.join(request.json()['Errors'])))
            return 'Ошибки при загрузке БД: {0}'.format('/n'.join(request.json()['Errors']))
        except:
            logging.error('Ошибка {0}. Текст: {1}'.format(request.status_code, request.text))
            return 'Ошибка {0}. Текст: {1}'.format(request.status_code, request.text)


class Database_1C:
    def __init__(self, LOGIN, PASS, auth=False):
        from config import DATABASE_SQL
        
        cipher = Fernet(DATABASE_SQL.key)
        
        
        self.url = DATABASE_1C.URL
        self.login = LOGIN
        self.session = requests.Session()        
        self.timeout = 5
        
        if auth:
            self.password = PASS
        else:
            self.password = cipher.decrypt(PASS.encode('utf-8')).decode('utf-8')      


    def ping (self):
        try:
            self.r = self.session.get(self.url + '/ERP/hs/tg_bot/ping', auth=BasicAuth(self.login, self.password), timeout=self.timeout)
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
        try:
            r = self.session.get(self.url + '/ERP/hs/tg_bot/tasks', auth=BasicAuth(self.login, self.password), params=params, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С'
                       
        check = check_connection(r)
        if check != None:
            return check
       
        dataDB = r.json()['Tasks']      
        dataDB = { dataDB[key]['id'] : value for key, value in enumerate(dataDB) }
        return dataDB

    def users(self): # DONE WORK
        r = self.session.get(self.url + '/ERP/hs/tg_bot/users', auth=BasicAuth(self.login, self.password), timeout=self.timeout)
        check = check_connection(r)
        if check != None:
            return check
        
        users = r.json()['Users']
        return users

    def GetVariants(self, taskID: str): # DONE WORK
        try:
            r = self.session.get(self.url + '/ERP/hs/tg_bot/getvariants', auth=BasicAuth(self.login, self.password), params={'id':taskID}, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С'        
                
        check = check_connection(r)
        if check != None:
            return check
                   
        variants = r.json()['Variants']
        return variants
    
    def GetRoles (self, username):

        try:
            r = self.session.get(self.url + '/ERP/hs/tg_bot/getroles', auth=BasicAuth(self.login, self.password), timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С'
                       
        check = check_connection(r)
        if check != None:
            return check
       
        data = r.json()['Roles']      
        new_data = pd.DataFrame()
        
        for row in data:
            for user in row['Исполнители']:
                new_data = pd.concat([new_data, pd.DataFrame({'Исполнители': [user], 'Роль' : [row['Роль']]})], ignore_index=True)
             
        data = {}
        for i in list(set(new_data['Исполнители'])):
            data[i.lower()] = list(set(new_data.loc[new_data['Исполнители'] == i, 'Роль']))
            
        try: 
            return data[username] 
        except KeyError:
            return None

    def GetRolesFull (self):
        try:
            r = self.session.get(self.url + '/ERP/hs/tg_bot/getroles', auth=BasicAuth(self.login, self.password), timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С'
                       
        check = check_connection(r)
        if check != None:
            return check
       
        data = r.json()['Roles']  
        data = { value['Роль'] : value['Исполнители'] for key, value in enumerate(data) }
        return data

    
    def GetFiles(self, taskID: str): # DONE WORK
        try:
            r = self.session.get(self.url + '/ERP/hs/tg_bot/getfiles', auth=BasicAuth(self.login, self.password), params={'id':taskID}, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С' 
            
        check = check_connection(r)
        if check != None:
            return check
    
                
        files = r.json()['Files']
        return files

            
    def SetAccept(self, taskID: str, accept: str): # DONE WORK
        data = {"id" : taskID, 'Accept' : accept}
        try:
            r = self.session.post(self.url + '/ERP/hs/tg_bot/setaccept', auth=BasicAuth(self.login, self.password), json=data, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С' 
        return check_connection(r)      

        
    def SetComment(self, taskID: str, comment: str, user : str): # DONE WORK
        data = {"id": taskID, "Comment": comment, "user": user}
        try:
            r = self.session.post(self.url + '/ERP/hs/tg_bot/setcomment', auth=BasicAuth(self.login, self.password), json=data, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С' 
        return check_connection(r)      

    def SetFile(self, taskID, file64, file_name, file_extension):
        data = {"id": taskID, "file": file64, "name": file_name, 'extension': file_extension}
        try:
            r = self.session.post(self.url + '/ERP/hs/tg_bot/setfile', auth=BasicAuth(self.login, self.password), json=data, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С' 
        return check_connection(r)      
        
    def SetRedirect(self, taskID: str, user : str): # DONE WORK
        data = {"id": taskID, "user": user}
        try:
            r = self.session.post(self.url + '/ERP/hs/tg_bot/setredirect', auth=BasicAuth(self.login, self.password), json=data, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С' 
        return check_connection(r)      

        
    def AddUsers(self, taskID: str,  users : list): # DONE при приглашении никак не отображается в задаче
        data = {"id": taskID, "users": users}
        try:
            r = self.session.post(self.url + '/ERP/hs/tg_bot/addusers', auth=BasicAuth(self.login, self.password), json=data, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С' 
        return check_connection(r)      

    def SetExecutor(self, taskID: str,  user : str): # DONE WORK
        data = {"id": taskID, "executor": user}
        try:
            r = self.session.post(self.url + '/ERP/hs/tg_bot/setexecutor', auth=BasicAuth(self.login, self.password), json=data, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С' 
        return check_connection(r)      

    def SetVariant (self, taskID: str, chosen_variant: list):
        data = {"id": taskID, "variant": chosen_variant[0], "variantstring": chosen_variant[1]}
        try:
            r = self.session.post(self.url + '/ERP/hs/tg_bot/setvariant', auth=BasicAuth(self.login, self.password), json=data, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С' 
        return check_connection(r)  

    def SetExecute(self, taskID: str):
        data = {"id": taskID}
        try:
            r = self.session.post(self.url + '/ERP/hs/tg_bot/setexecute', auth=BasicAuth(self.login, self.password), json=data, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            return 'Отсутствует подключение к базе данных 1С' 
        return check_connection(r) 

        
test_connection = Database_1C(DATABASE_1C.LOGIN, DATABASE_1C.PASS)
