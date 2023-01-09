# -*- coding: utf-8 -*-

from datetime import datetime as dt
from urllib import request
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

import requests
import pandas as pd
import json

LOGIN = 'tgBottesTuser'
PASS = 'torT101'


URL = 'http://10.10.100.150:8079'
taskID = '75c16b49-0113-11ed-a7b1-d89d67149b67'
# myUrl = 'http://10.10.100.150:8079/'


### Список задач
res = requests.get(URL + '/ERP/hs/tg_bot/ping', auth=HTTPBasicAuth(LOGIN, PASS))


res = requests.get(URL + '/ERP/hs/tg_bot/tasks', auth=HTTPBasicAuth(LOGIN, PASS), params={'Executed':'no', 'Accepted': 'yes'})
res = requests.get(URL + '/ERP/hs/tg_bot/getvariants', auth=HTTPBasicAuth(LOGIN, PASS), params={'id' : '75c16b49-0113-11ed-a7b1-d89d67149b67'})
res = requests.get(URL + '/ERP/hs/tg_bot/tasks', auth=HTTPBasicAuth(LOGIN, PASS), params= {'Executed' : 'no', 
            'DateBegin': '20001231235959', 
            'DateExecuted'  : dt.now().strftime('%Y%m%d%H%M%S'), 
            })

print(res)

data = res.json()['Tasks']
data = pd.json_normalize(res.json()['Tasks'])

dataDB = { data[key]['id'] : value for key, value in enumerate(data) }


#### Отправить коммент

data_req = {"id":taskID, 
             "Comment":"Test", 
             "user":"tgbottestuser"}

json_data = json.dumps(data_req)

res = requests.post(URL + '/ERP/hs/tg_bot/setcomment', 
                    auth=HTTPBasicAuth(LOGIN, PASS), 
                    data=json_data)
res.status_code

print(res.status_code)




### отправить принятие задачи
data_req = {"id":taskID, "Accept":"no"}

json_data = json.dumps(data_req)

# res = requests.post( URL + '/ERP/hs/tg_bot/SetAccept', auth=HTTPBasicAuth(LOGIN, PASS), json=data_req)
res = requests.post( URL + '/ERP/hs/tg_bot/setaccept', auth=HTTPBasicAuth(LOGIN, PASS),  json=data_req)
print(res.status_code)



### редирект
data_req = {"id":'9a5c9873-2e6f-11ed-a7c0-d89d67149b65',
            "users":"БотТест"}

res = requests.post( URL + '/ERP/hs/tg_bot/setredirect', auth=HTTPBasicAuth(LOGIN, PASS), json=data_req)
print(res.text)




("id", "cb066214-e4bb-11ec-a7a6-d89d67149b66");
("user", "ED");


### файл
data_req = {"id":"cb066214-e4bb-11ec-a7a6-d89d67149b66",
            "file": "jshjshd"}

json_data = json.dumps(data_req)

# res = requests.post( URL + '/ERP/hs/tg_bot/SetFile', auth=HTTPBasicAuth(LOGIN, PASS), json=data_req)
res = requests.post( URL + '/ERP/hs/tg_bot/SetFile', auth=HTTPBasicAuth(LOGIN, PASS), data=json_data)

print(res.text)

7e81bfde-7c3c-11ed-9ba9-9457a55a8a23


data = {"id": "75c16b49-0113-11ed-a7b1-d89d67149b67",
"variant": "2",
"variantstring": "Подобрать более дешевый вариант "
}
res = requests.post( URL + '/ERP/hs/tg_bot/setvariant', auth=HTTPBasicAuth(LOGIN, PASS), json=data)




# от ED
data_req = {"id": "7e81bfde-7c3c-11ed-9ba9-9457a55a8a23"}
res = requests.get( URL + '/ERP/hs/tg_bot/getfiles', auth=HTTPBasicAuth(LOGIN, PASS), params=data_req)
files = res.json()['Files']



data_req = {"id": "75c16b49-0113-11ed-a7b1-d89d67149b67"}
res = requests.get( URL + '/ERP/hs/tg_bot/getfiles', auth=HTTPBasicAuth(LOGIN, PASS), params=data_req)
data = res.json()['Files']

    import magic
    import mimetypes
    import re
    import io
    
    media = types.MediaGroup()
    media_docs = types.MediaGroup()
    docs = False
    
    # for file in files:
    
file = re.sub(r"^data\:.+base64\,(.+)$", r"\1", files[0])

decoded = base64.b64decode(file)

with open("imageToSave.png", "wb") as fh:
  fh.write(decoded)

mime_type = magic.from_buffer(decoded, mime=True)
file_ext = mimetypes.guess_extension(mime_type)

bytesio = io.BytesIO(decoded)
bytesio.seek(0)


if file_ext in ['.jpg']:
    media.attach_photo(types.InputMediaPhoto(types.InputFile(bytesio)))            
elif file_ext in ['.mp4']:
    media.attach_video(types.InputMediaVideo(types.InputFile(bytesio)))
else:
    docs = True
    media_docs.attach_document(types.InputMediaDocument(types.InputFile(bytesio)))
            
if docs:
    return [media, media_docs]
else:
    return [media]














# data_req = {'id':taskID}
res = requests.get( URL + '/ERP/hs/tg_bot/users', auth=HTTPBasicAuth(LOGIN, PASS))
data = res.json()['Users']

data = pd.json_normalize(data)


data = res.json()['Roles']


new_data = pd.DataFrame()
for row in data:
    for user in row['Исполнители']:
        new_data = pd.concat([new_data, pd.DataFrame({'Исполнители': [user], 'Роль' : [row['Роль']]})], ignore_index=True)

data = {}
for i in list(set(new_data['Исполнители'])):
    data[i] = list(set(new_data.loc[new_data['Исполнители'] == i, 'Роль']))












