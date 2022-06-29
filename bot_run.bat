@echo off


cd %~dp0

set TOKEN=5321759824:AAEzZnvwVHx3U7unXviVvI0e9BD5i1npgi0

set URL=http://10.10.100.150:8079
set LOGIN=tgbottestuser
set PASS=tort101


set REDIS_HOST=localhost
set REDIS_PORT=6379
set REDIS_PASS=None

python app.py

pause