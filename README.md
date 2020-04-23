In developing ...
# sms-sending-service
Quart app for sms sending

# Запуск
Python 3.8 required

`pip install -r requirements.txt`

`export LOGIN={логин к api  sms.ru}`

`export PASSWORD={пароль к api  sms.ru}`

`export PHONES={телефоны, отделенные точкой с запятой ';''}`

`export REDIS_URI={}`

`export REDIS_PASSWORD={}`

Или создать файл .env с этими переменными окружения


`python main.py
`
