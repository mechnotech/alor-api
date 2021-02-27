# Alor API client

Клиент для API Alor.ru

Для старта с нуля:
* Созадть окружение venv (`python3 -m venv venv && source venv/bin/activated`)
* Установить библиотеки pip из requirements.txt (`pip install -r requirements.txt`)
* создать .env файл с персональными настройками по шаблону .env.example
* См. файл examples.py - примеры функций для работы с API брокера.

В Settings.py:

```
LOGGING = True (Записывать ошибки в debug.log)
DEVMODE = True (в режиме разработчика, подключения идут к тествовым серверам)
TTL_JWT_TOKEN = 60 (Время жизни jwt-токена в секундах)
```

Токен обновления создается в личном кабинете
https://oauthdev.alor.ru

Описание функций и ответов функций см. в докстрингах а так-же:
https://alor.dev/docs

Чат разработчиков:
https://t.me/alor_openapi_chat

Автор клиентской части API:

Евгений Шумилов (По вопросам и предложениям пишите в телеграм @mechnotech)
