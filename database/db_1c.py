# -*- coding: utf-8 -*-

# URL = 'http://10.10.100.150:8079/ERP/hs/tg_bot'
# api_methods = {'PING': URL + '/ping',
#                'TASKS': URL + '/tasks',
#                'SetComment':'/SetComment',
#                'SetAccept':'/SetAccept',
#                'SetRedirect':'/SetRedirect',
#                'SetFile':'/SetFile',
#                '':'',}

import logging
import requests

from config import URL, LOGIN, PASS
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import NewConnectionError, MaxRetryError
from requests.exceptions import ConnectionError, ConnectTimeout

# URL = 'http://10.10.100.150:8079'
# LOGIN = 'tgbottestuser'
# PASS = 'tort101'

def check_connection(request):
    if request:
        logging.INFO('Соединение с 1С установлено')
        return True
    
    else:
        logging.error('Ошибка {0}. Текст: {1}'.format(request.status_code, request.text))
        ### TODO отправить уведомление об ошибке в чат            
        return


class Database_1C:
    def __init__(self, URL, LOGIN, PASS):
        self.url = URL
        self.login = LOGIN
        self.password = PASS   
        self.session = requests.Session()        
        self.timeout = 2
                
        try:
            requests.get(self.url + '/ERP/hs/tg_bot/ping', auth=HTTPBasicAuth(self.login, self.password), timeout=self.timeout)
        
        except (requests.exceptions.ConnectionError, ConnectTimeout, MaxRetryError, NewConnectionError) as error:
            logging.error(error)
            return

    def ping (self):      
        r = self.session.get(self.url + '/ERP/hs/tg_bot/ping', auth=HTTPBasicAuth(self.login, self.password))
        return check_connection(r)
    
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
            
            
            

    # def SetComment (self, data):
    #     r = self.session.get(self.url + '/ERP/hs/tg_bot/SetComment', auth=HTTPBasicAuth(self.login, self.password))
        
    #     if check_connection(r) != True:
    #         return



    


db_1c = Database_1C(URL, LOGIN, PASS)


# db_1c.ping()






# import paramiko

# url_1 = 'rt.itpark70.ru'
# url_2 = '10.10.100.20'
# url_3 = '10.10.100.150:8059'

# port = 20388

# username = "ПеньковДА"
# password = "pm8Q~d}3uE"

# headers = {
#         'Content-Type': 'application/json',
#         'accept': 'application/json',
#     }

# requests.get('http://rt.itpark70.ru:20388', auth=HTTPBasicAuth(username.encode('utf-8'), password), timeout=5)

# proxies = {'http': 'http://ПеньковДА:pm8Q~d}3uE@rt.itpark70.ru:20388/'}

# requests.get('http://10.10.100.20', auth=HTTPBasicAuth(username.encode('utf-8'), password), timeout=5, proxies=proxies)

# try:
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(url_2,username=username,password=password, port=port)
#     print("Connected to %s" % hostname)
# except paramiko.AuthenticationException:
#     print("Failed to connect to %s due to wrong username/password" %hostname)
#     exit(1)
# except Exception as e:
#     print(e.message)    
#     exit(2)
    
    
    
    
# import socket

# server = socket.socket()
# server.connect(('rt.itpark70.ru', 20388))

# server = socket.socket()
# server.connect(('10.10.100.20', 22))
# server.close()



# server.listen(1)
# data = socket_client.recv(1000) 
# data = sock.recv(1024)

# print data