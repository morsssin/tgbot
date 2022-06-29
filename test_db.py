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

full_list = list(test_DB.keys())
user_list = ['id03', 'id04', 'id05', 'id06', 'id07', 'id08', 'id09', 'id010']
free_list = ['id09', 'id010', 'id011', 'id012', 'id013']
past_list = ['id02', 'id014', 'id015']

users = ['admin', 'admin1', 'client']    
users_pass = {'admin':'pass', 'admin1': 'password', 'client':'password'}
users_chat_id = {'admin':'', 'admin1': '', 'client':''}

len_tasks = 30

actions_var_list = ['Проблема решена', 'Проблема не решена', 'Требуется выезд тех.специалиста', 'Не в нашей юрисдикции']

tools_list = []
works_list = []
for i in range(1, 100):
    tools_list.append('Оборудование №%s' % i)
    works_list.append('Работа №%s' % i)