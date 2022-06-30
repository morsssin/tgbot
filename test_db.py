# -*- coding: utf-8 -*-

test_DB = {}

for i in range(1, 101):
    test_DB['id0%s' % i] = {'Номер':'№ 000%s от 25.04.2022' % i,
                            'Наименование':'Название задачи %s' % i,
                            'CRM_Партнер':'Иванов Иван ИП %s' % i,
                            'Описание':'Описание %s' % i,
                            'Исполнитель':'Дирекция %s' % i,
                            'РезультатВыполнения':'07.05.2022 12.25 Принята к исполнению',
                            'COMMENTS': 'Комментарий 1. ',
                            'Дата' : '20221231235959',
                            'ДатаИсполнения':'20221231235959', 
                            'ПринятаКИсполнению':'Нет'}

users = ['admin', 'admin1', 'user', 'user1']    
users_pass = {'admin':'pass', 'admin1': 'password', 'client':'password'}
users_chat_id = {'admin':'', 'admin1': '', 'user':'', 'user1':''}

len_tasks = 30

actions_var_list = ['Проблема решена', 'Проблема не решена', 'Требуется выезд тех.специалиста', 'Не в нашей юрисдикции']

tools_list = []
works_list = []
for i in range(1, 100):
    tools_list.append('Оборудование №%s' % i)
    works_list.append('Работа №%s' % i)