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

Токен обновления создается вручную в личном кабинете (сроком на 1 год для тестовых серверов)
https://devsdev.alor.ru/login

Описание функций и ответов функций см. в докстрингах а так-же:
https://alor.dev/docs

Чат разработчиков:
https://t.me/alor_openapi_chat

**Первые шаги:**

```
# Создаем объект API используя Refresh токен и Аккаунт - username
alor = Api(REFRESH_TOKEN, USERNAME)
# Указываем биржу
alor.exchange = 'MOEX'
# Получение списка серверов для рынков: Валютный, Срочный, Фондовый,
print(alor.get_portfolios())
```

Получаем вот такую выдачу:
```
{
    "Валютный рынок": [
        {
            "portfolio": "G00031",
            "tks": "MB0063104103",
            "tradeServersInfo": [
                {
                    "tradeServerCode": "FX1",
                    "addresses": None,
                    "type": None,
                    "contracts": "",
                    "market": None,
                    "accountNum": None,
                }
            ],
        }
    ],
    "Срочный рынок": [
        {
            "portfolio": "7500031",
            "tks": "7500031",
            "tradeServersInfo": [
                {
                    "tradeServerCode": "FUT1",
                    "addresses": None,
                    "type": None,
                    "contracts": "фьючерсы",
                    "market": None,
                    "accountNum": None,
                }
            ],
        }
    ],
    "Фондовый рынок": [
        {
            "portfolio": "D00031",
            "tks": "L01-00000F00",
            "tradeServersInfo": [
                {
                    "tradeServerCode": "ITRADE",
                    "addresses": None,
                    "type": None,
                    "contracts": "ИЦБ",
                    "market": None,
                    "accountNum": None,
                },
                {
                    "tradeServerCode": "TRADE",
                    "addresses": None,
                    "type": None,
                    "contracts": "РЦБ",
                    "market": None,
                    "accountNum": None,
                },
            ],
        }
    ],
}

```
В дальнейшем, при работе с функциями API нам потребуются значения *portfolio*, а так же tks
и tradeServerCode. Обратите внимание, они разные для разных рынков!
Так у данного клиента для Фондового рынка: portfolio = D00031, tks = L01-00000F00, tradeServerCode = TRADE



Автор клиентской части API:

Евгений Шумилов (По вопросам и предложениям пишите в телеграм @mechnotech)
