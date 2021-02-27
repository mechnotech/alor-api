import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime, date
from json import JSONDecodeError

import aiohttp
import requests
from settings import (
    URL_OAUTH,
    URL_API,
    LOGGING, TTL_JWT_TOKEN
)

if LOGGING:
    logging.basicConfig(
        filename='status.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d-%b-%y %H:%M:%S',
        level=logging.DEBUG
    )


def _check_results(res):
    if res.status_code != 200:
        if LOGGING:
            logging.error(f'Ошибка: {res.status_code} {res.text}')
        return
    try:
        return json.loads(res.content)
    except JSONDecodeError as e:
        if LOGGING:
            logging.error(f'Ошибка декодирования JSON: {e}')


def _random_order_id(account: str) -> str:
    data = account + str(datetime.timestamp(datetime.now()))
    rand_id = hashlib.sha256(data.encode('utf-8')).hexdigest()
    return rand_id[:-30]


class Connection:

    @property
    def _headers(self):
        now = int()
        if now - self.token_ttl > TTL_JWT_TOKEN:
            self.jwt_token = self._get_jwt_token()
        bearer = self.jwt_token
        if not bearer:
            logging.error('Не найден JWT токен, запустите get_jwt()!')
            return None
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {bearer}"
                   }
        return headers

    @property
    def is_working_hours(self) -> bool:
        if 0 <= date.today().weekday() < 5 and 10 <= datetime.now().hour < 23:
            return True
        return False

    def __init__(self, refresh=None, username=None):
        self.username = username
        self.refresh_token = refresh
        if not refresh:
            self.refresh_token = os.getenv('REFRESH_TOKEN')
        if not username:
            self.username = os.getenv('ALOR_USERNAME')
        self.portfolio = None
        self.exchange = None
        self.token_ttl = None
        self.jwt_token = self._get_jwt_token()

    def _get_jwt_token(self):
        """
        Создать JWT Token и поместить в env окружение процесса.
        Следует вызывать перед любым обращением к другим функциям API
        Время жизни JWT ~ 5 мин, обновляйте чаще!

        Токен обновления, создается в личном кабинете
        https://oauthdev.alor.ru
        :return: JSON
        """
        payload = {'token': self.refresh_token}
        res = requests.post(
            url=f'{URL_OAUTH}/refresh',
            params=payload
        )
        if res.status_code != 200:
            if LOGGING:
                logging.error(
                    f'Ошибка получения JWT токена: {res.status_code}')
            return None
        try:
            token = res.json()
            jwt = token.get('AccessToken')
            self.token_ttl = int(datetime.timestamp(datetime.now()))
            return jwt
        except JSONDecodeError as e:
            if LOGGING:
                logging.error(f'Ошибка декодирования JWT токена: {e}')
                return None

    def _payload(self,
                 ticker,
                 side,
                 quantity,
                 type_order,
                 price: float = None,
                 portfolio: str = None,
                 exchange: str = None,
                 ):
        if self.exchange:
            exchange = self.exchange
        account = os.getenv('ALOR_USERNAME')
        payload = {
            "symbol": ticker,
            "side": side,
            "type": type_order,
            "quantity": quantity,
        }
        if price:
            payload['price'] = price
        payload['instrument'] = {
            "symbol": ticker,
            "exchange": exchange
        }
        payload['user'] = {
            "account": account,
            "portfolio": portfolio
        }
        return payload

    # ---------------- Блок "Информация о клиенте -------------------

    def get_portfolios(self):
        """
        Получение списка серверов и идентификаторы клиентского портфеля
        :return: Simple JSON
        """
        res = requests.get(
            url=f'{URL_API}/client/v1.0/users/{self.username}/portfolios',
            headers=self._headers
        )
        return _check_results(res)

    def get_orders_info(self, portfolio: str = None, exchange: str = None):
        """
        Запрос информации о всех заявках

        :param portfolio: Идентификатор клиентского портфеля (например D39004)
        :param exchange: Биржа Available values : MOEX, SPBX
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/clients/{exchange}/{portfolio}/orders',
            headers=self._headers
        )
        return _check_results(res)

    def get_order_info(self, orderId: str, portfolio: str = None,
                       exchange: str = None):
        """
        Запрос информации о выбранной заявке

        :param portfolio: Идентификатор клиентского портфеля (например D39004)
        :param orderId: Идентификатор заявки (например 18995978560)
        :param exchange: Биржа Available values : MOEX, SPBX
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/clients/{exchange}/{portfolio}'
                f'/orders/{orderId}',
            headers=self._headers
        )
        return _check_results(res)

    def get_stoporders_info(self, portfolio: str = None,
                            exchange: str = 'MOEX'):
        """Запрос информации о всех стоп-заявках

        :param portfolio: Идентификатор клиентского портфеля (например D39004)
        :param exchange: Биржа Available values : MOEX, SPBX
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/clients/{exchange}/{portfolio}/stoporders',
            headers=self._headers
        )
        return _check_results(res)

    def get_stoporder_info(self, orderId: str, portfolio: str = None,
                           exchange: str = None):
        """Запрос информации о выбранной стоп-заявке

        :param portfolio: Идентификатор клиентского портфеля (например D39004)
        :param orderId: Идентификатор заявки (например 18995978560)
        :param exchange: Биржа Available values : MOEX, SPBX
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/clients/{exchange}'
                f'/{portfolio}/stoporders/{orderId}',
            headers=self._headers
        )
        return _check_results(res)

    def get_summary_info(self, portfolio: str = None, exchange: str = None):
        """
        Запрос сводной информации

        :param portfolio: Идентификатор клиентского портфеля (например D39004)
        :param exchange: Биржа Available values : MOEX, SPBX
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/clients/{exchange}/{portfolio}/summary',
            headers=self._headers
        )
        return _check_results(res)

    def get_positions_info(self, portfolio: str = None, exchange: str = None):
        """
        Запрос информации о позициях

        :param portfolio: Идентификатор клиентского портфеля
        :param exchange: Биржа Available values : MOEX, SPBX
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/Clients/{exchange}/{portfolio}/positions',
            headers=self._headers
        )
        return _check_results(res)

    def get_position_info(self, symbol: str, portfolio: str = None,
                          exchange: str = None):
        """
        Запрос информации о позици по инструменту

        :param symbol: Инструмент (GAZP)
        :param portfolio: Идентификатор клиентского портфеля
        :param exchange: Биржа Available values : MOEX, SPBX
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/'
                f'Clients/{exchange}/{portfolio}/positions/{symbol}',
            headers=self._headers
        )
        return _check_results(res)

    def get_trades_info(self, portfolio: str = None, exchange: str = None):
        """Запрос информации о сделках

        :param portfolio: Идентификатор клиентского портфеля
        :param exchange: Биржа Available values : MOEX, SPBX
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/'
                f'Clients/{exchange}/{portfolio}/trades',
            headers=self._headers
        )
        return _check_results(res)

    def get_trade_info(self, ticker: str, portfolio: str = None,
                       exchange: str = None):
        """Запрос информации о сделках по выбранному инструменту

        :param ticker: Инструмент (GAZP)
        :param portfolio: Идентификатор клиентского портфеля
        :param exchange: Биржа Available values : MOEX, SPBX
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/'
                f'Clients/{exchange}/{portfolio}/{ticker}/trades',
            headers=self._headers
        )
        return _check_results(res)

    def get_fortrisk_info(self, portfolio: str = None, exchange: str = None):
        """
        Запрос информации о рисках

        :param portfolio: Идентификатор клиентского портфеля
        :param exchange: Биржа Available values : MOEX
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/'
                f'Clients/{exchange}/{portfolio}/fortsrisk',
            headers=self._headers
        )
        return _check_results(res)

    def get_risk_info(self, portfolio: str = None, exchange: str = None):
        """
        Запрос информации о рисках

        :param portfolio: Идентификатор клиентского портфеля
        :param exchange: Биржа Available values : MOEX, SPBX
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/'
                f'Clients/{exchange}/{portfolio}/risk',
            headers=self._headers
        )
        return _check_results(res)

    # ------------------ Блок Ценные бумаги / инструменты ---------------------

    def get_securities_info(self, query: str, limit: int = None,
                            sector: str = None, cficode: str = None,
                            exchange: str = None):
        """
        Запрос информации об имеющихся ценных бумагах

        :param exchange: Фильтр по коду биржи MOEX или SPBX
        :param limit: Ограничение на количество выдаваемых результатов поиска
        :param sector: Рынок на бирже Available values : FORTS, FOND, CURR
        :param cficode: Код финансового инструмента
        по стандарту ISO 10962 (EXXXXX)
        :param query: Фильтр про инструменту GAZP
        :return: [ Simple JSON ]
        """
        if self.exchange:
            exchange = self.exchange
        payload = {
            'limit': limit,
            'sector': sector,
            'cficode': cficode,
            'exchange': exchange
        }
        query = {'query': query}
        res = requests.get(
            url=f'{URL_API}/md/v2/securities',
            params=query,
            data=payload,
            headers=self._headers
        )
        return _check_results(res)

    def get_all_securities_info(self, exchange: str = None):
        """
        Запрос информации об инструментах на выбранной бирже
        ВНИМАНИЕ! Возвращает все инструменты! ~ 25 мб

        :param exchange:  Биржа Available values : MOEX, SPBX

        :return: Simple JSON
        """
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/Securities/{exchange}',
            headers=self._headers
        )
        return _check_results(res)

    def get_security_info(self, ticker: str, exchange: str = None):
        """
        Запрос информации о выбранном финансовом инструменте на бирже
        (Аналог get_securities_info())

        :param exchange: Биржа : MOEX, SPBX
        :param ticker: Инструмент GAZP
        :return: Simple JSON
        """
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/Securities/{exchange}/{ticker}',
            headers=self._headers
        )
        return _check_results(res)

    def get_quotes_list(self, symbols: str):
        """
        Запрос информации о котировках для выбранных инструментов и бирж

        :param symbols: Принимает несколько пар биржа-тикер.
         Пары отделены запятыми. Биржа и тикер разделены двоеточием.
         Например MOEX:SBER,MOEX:GAZP,SPBX:AAPL
        :return: Simple JSON
        """
        res = requests.get(
            url=f'{URL_API}/md/v2/securities/{symbols}/quotes',
            headers=self._headers
        )
        return _check_results(res)

    async def _get_orderbook(self, sec: str, depth: int = 5):
        session = aiohttp.ClientSession()
        exchange = self.exchange
        res = await session.get(
            url=f'{URL_API}/md/v2/orderbooks/{exchange}/{sec}?depth={depth}',
            headers=self._headers
        )
        if res.status != 200:
            await session.close()
            return sec, None

        data = await res.json()
        await session.close()
        return sec, data

    def get_orderbooks(self, sec_ls: list = None, depth: int = 5):
        """
        Получить списки заявок bid/ask для ценных бумаг

        :param depth: Глубина стакана
        :param sec_ls: Список ценных бумаг
        :return: [(Название бумаги, JSON), ... ]
        """

        if sec_ls is None:
            return None
        if isinstance(sec_ls, str):
            sec_ls = [sec_ls]

        futures = [self._get_orderbook(sec, depth=depth) for sec in sec_ls]
        loop = asyncio.get_event_loop()
        order_books = loop.run_until_complete(asyncio.gather(*futures))
        return order_books

    def get_today_trades(self,
                         ticker: str,
                         exchange: str = None,
                         start: int = None,
                         finish: int = None
                         ):
        """
        Запросить данные о всех сделках (лента) по ценным бумагам
        за сегодняшний день. Если указать UTC метки start и finish,
        вернет данные трейдов в промежутке между ними.

        :param exchange: Биржа : MOEX, SPBX
        :param ticker: Инструмент GAZP
        :param start: Начало отрезка времени (UTC) для фильтра результатов
        :param finish: Конец отрезка времени (UTC) для фильтра результатов
        :return: Simple JSON
        """
        if self.exchange:
            exchange = self.exchange
        payload = {'from': start, 'to': finish}
        res = requests.get(
            url=f'{URL_API}/md/v2/Securities/{exchange}/{ticker}/alltrades',
            data=payload,
            headers=self._headers
        )
        return _check_results(res)

    def get_futures_quotes(self, ticker: str, exchange: str = None):
        """
        Запрос информации о фьючерсах

        :param exchange: Биржа MOEX
        :param ticker: Инструмент SBRF
        :return: Simple JSON
        """
        if self.exchange:
            exchange = self.exchange
        res = requests.get(
            url=f'{URL_API}/md/v2/Securities/'
                f'{exchange}/{ticker}/actualFuturesQuote',
            headers=self._headers
        )
        return _check_results(res)

    def get_history(self,
                    exchange: str,
                    ticker: str,
                    start: int,
                    finish: int,
                    tf: int
                    ):
        """
        Запрос истории рынка для выбранных биржи и финансового инструмента.
        Данные имеют задержку в 15 минут, если запрос не авторизован.
        Для авторизованных клиентов задержка не применяется.

        :param exchange: Биржа - допустимые значения MOEX, SPBX
        :param ticker: Код инструмента SBER
        :param start: От (unix time seconds)
        :param finish: До (unix time seconds)
        :param tf: Длительность таймфрейма в секундах.
         Допустимые значения 15, 60, 300, 900, 3600, 86400
        :return: Simple JSON
        """
        if self.exchange:
            exchange = self.exchange
        payload = {
            'exchange': exchange,
            'symbol': ticker,
            'from': start,
            'to': finish,
            'tf': tf}
        res = requests.get(
            url=f'{URL_API}/md/v2/history',
            params=payload,
            headers=self._headers
        )
        return _check_results(res)

    # ------------- Другое --------------------------
    def get_time(self):
        """
        Запрос текущего UTC времени в формате Unix. Если этот запрос выполнен
        без авторизации, то будет возвращено время,
        которое было 15 минут назад.

        :return:
        """
        res = requests.get(
            url=f'{URL_API}/md/v2/time',
            headers=self._headers
        )
        return _check_results(res)

    # ------------- Работа с заявками ---------------

    def set_market_order(self, ticker: str,
                         side: str,
                         quantity: int,
                         portfolio: str = None,
                         exchange: str = None,
                         order_id: str = None):
        """
        Создание рыночной заявки ПО РЫНКУ

        В качестве идентификатора запроса (order_id) требуется уникальная
        случайная строка. Если таковая не указана, генерируется случайно.
        В ответе возвращается id ордера, который стоит сохранить.
        Если уже приходил запрос с таким идентификатором, то заявка не будет
        исполнена повторно, а в качестве ответа будет возвращена копия ответа
        на предыдущий запрос с таким значением идентификатора.


        :param exchange: Биржа MOEX, SPBX
        :param ticker: Инструмент GDH1
        :param side: Купить или продать по рынку sell, buy
        :param quantity: Количество лотов
        :param portfolio: Идентификатор клиентского портфеля
        :param order_id: Уникальная строка ордера
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if not order_id:
            order_id = _random_order_id
        payload = self._payload(ticker, side, quantity, type_order='market',
                                exchange=exchange)
        headers = self._headers
        headers['X-ALOR-REQID'] = f'{portfolio};{order_id};{quantity}'
        res = requests.post(
            url=f'{URL_API}/commandapi/warptrans/TRADE/'
                f'v2/client/orders/actions/market',
            headers=headers,
            json=payload
        )
        return _check_results(res)

    def set_limit_order(self,
                        ticker: str,
                        side: str,
                        quantity: int,
                        price: float,
                        portfolio: str = None,
                        exchange: str = None,
                        order_id: str = None,
                        ):
        """
        Создание отложенной рыночной заявки (LIMIT)

            В качестве идентификатора запроса (order_id) требуется уникальная
        случайная строка. Если таковая не указана, генерируется случайно.
            Если уже приходил запрос с таким идентификатором,
        то заявка не будет исполнена повторно, а в качестве ответа будет
        возвращена копия ответа на предыдущий запрос с таким значением
        идентификатора.

        :param exchange: Биржа MOEX, SPBX
        :param ticker: Инструмент GDH1
        :param side: Купить или продать по рынку sell, buy
        :param quantity: Количество лотов
        :param price: Цена
        :param portfolio: Идентификатор клиентского портфеля
        :param order_id: Уникальная строка ордера
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        if not order_id:
            order_id = _random_order_id
        payload = self._payload(ticker, side, quantity, type_order='limit',
                                price=price, exchange=exchange)
        headers = self._headers
        headers['X-ALOR-REQID'] = f'{portfolio};{order_id};{quantity}'
        res = requests.post(
            url=f'{URL_API}/commandapi/warptrans/TRADE/'
                f'v2/client/orders/actions/limit',
            headers=headers,
            json=payload
        )
        return _check_results(res)

    def set_stoploss(self,
                     ticker: str,
                     side: str,
                     quantity: int,
                     price: float,
                     portfolio: str = None,
                     exchange: str = None,
                     order_id: str = None,
                     ):
        """
        Создание стоп лосс заявки

            В качестве идентификатора запроса (order_id) требуется уникальная
        случайная строка. Если таковая не указана, генерируется случайно

        Если уже приходил запрос с таким идентификатором, то заявка не будет
        исполнена повторно, а в качестве ответа будет возвращена копия ответа
        на предыдущий запрос с таким значением идентификатора.

        :param exchange: Биржа MOEX, SPBX
        :param ticker: Инструмент GDH1
        :param side: Купить или продать по рынку sell, buy
        :param quantity: Количество лотов
        :param price: Цена
        :param portfolio: Идентификатор клиентского портфеля
        :param order_id: Уникальная строка ордера
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        account = os.getenv('ALOR_USERNAME')
        if not order_id:
            order_id = _random_order_id(account)
        payload = {
            "Quantity": quantity,
            "Side": side,
            "TriggerPrice": price,
            "Instrument": {
                "Symbol": ticker,
                "Exchange": exchange
            },
            "User": {
                "Account": account,
                "Portfolio": portfolio
            },
            "OrderEndUnixTime": 0
        }
        headers = self._headers
        headers['X-ALOR-REQID'] = order_id
        res = requests.post(
            url=f'{URL_API}/commandapi/warptrans/TRADE/'
                f'v2/client/orders/actions/stopLoss',
            headers=headers,
            json=payload
        )
        return _check_results(res)

    def change_market_order(self,
                            ticker: str,
                            side: str,
                            quantity: int,
                            order_id: str,
                            portfolio: str = None,
                            exchange: str = None,
                            ):
        """
        Правка рыночной заявки ПО РЫНКУ

        В качестве идентификатора запроса (order_id) требуется уникальная
        строка, соответствующая созданному ранее ордеру.
        Если уже приходил запрос с таким идентификатором, то заявка не будет
        исполнена повторно, а в качестве ответа будет возвращена копия ответа
        на предыдущий запрос с таким значением идентификатора.


        :param exchange: Биржа MOEX, SPBX
        :param ticker: Инструмент GDH1
        :param side: Купить или продать по рынку sell, buy
        :param quantity: Количество лотов
        :param portfolio: Идентификатор клиентского портфеля
        :param order_id: Уникальная строка ордера
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        if self.exchange:
            exchange = self.exchange
        payload = self._payload(ticker, side, quantity, type_order='market',
                                exchange=exchange)
        headers = self._headers
        headers['X-ALOR-REQID'] = f'{portfolio};{order_id};{quantity}'
        res = requests.put(
            url=f'{URL_API}/commandapi/warptrans/TRADE/'
                f'v2/client/orders/actions/market/{order_id}',
            headers=headers,
            json=payload
        )
        return _check_results(res)

    def change_limit_order(self,
                           ticker: str,
                           side: str,
                           quantity: int,
                           price: float,
                           order_id: str,
                           portfolio: str = None,
                           exchange: str = None,
                           ):
        """
        Изменение отложенной рыночной заявки (LIMIT)

            В качестве идентификатора запроса (order_id) требуется уникальная
        строка, соответствующая созданному ранее ордеру.
        Если уже приходил запрос с таким идентификатором, то заявка не будет
        исполнена повторно, а в качестве ответа будет возвращена копия ответа
        на предыдущий запрос с таким значением идентификатора.

        :param exchange: Биржа MOEX, SPBX
        :param ticker: Инструмент GDH1
        :param side: Купить или продать по рынку sell, buy
        :param quantity: Количество лотов
        :param price: Цена
        :param portfolio: Идентификатор клиентского портфеля
        :param order_id: Уникальная строка ордера
        :return: Simple JSON
        """
        if self.portfolio:
            portfolio = self.portfolio
        payload = self._payload(ticker, side, quantity, type_order='limit',
                                price=price, exchange=exchange)
        headers = self._headers
        headers['X-ALOR-REQID'] = f'{portfolio};{order_id};{quantity}'
        res = requests.put(
            url=f'{URL_API}/commandapi/warptrans/TRADE/'
                f'v2/client/orders/actions/limit/{order_id}',
            headers=headers,
            json=payload
        )
        return _check_results(res)

    def cancel_order(self,
                     order_id: str,
                     stop: bool,
                     exchange: str = None,
                     portfolio: str = None,
                     ):
        """
        Снятие заявки

        :param exchange:
        :param portfolio:
        :param order_id:
        :param stop:
        :return:
        """
        account = os.getenv('ALOR_USERNAME')
        payload = {
            'exchange': exchange,
            'portfolio': portfolio,
            'account': account,
            'stop': 'true' if stop else 'false',
            'format': 'Simple'
        }
        headers = self._headers
        path_part = '/commandapi' if not stop else ''
        res = requests.delete(
            url=f'{URL_API}{path_part}/warptrans/TRADE/'
                f'v2/client/orders/{order_id}',
            headers=headers,
            params=payload
        )
        if res.text == 'success':
            return res.text
        return _check_results(res)


if __name__ == '__main__':
    pass
    # get_jwt(REFRESH_TOKEN)
    # print(_is_working_hours())
    # print(os.environ.get('JWT_TOKEN'))

    # print(_random_order_id('ddd'))
    # print(set_limit_order('MOEX', 'GDH1', 'sell', 1, 1800, '7500031'))
    # print(get_summary_info('7500031'))
    # print(get_order_info('7500031', '18995978560'))
    # print(get_position_info('GDH1', '7500031'))
    # print(get_trades_info('7500031'))
    # print(get_fortrisk_info('7500031'))
    # print(get_risk_info('7500031'))
    # ??
    # print(get_securities_info(query='GAZP', exchange='MOEX'))
    # print(get_security_info('MOEX', 'GAZP'))
    # print(get_futures_quotes('SBRF'))
    # print(get_time())
    # results = get_history('MOEX', 'GAZP', 1613750579, 1613751791, 60)
    # for r in results.get('history'):
    #     print(r)
    # print(len(results.get('history')), '-- трейдов за период (за сегодня)')
    # print(get_quotes_list('MOEX:SBER,MOEX:GAZP,SPBX:AAPL'))
    #
    # results = get_today_trades('MOEX', 'GDH1', 1613750579, 1613751791)
    # for r in results:
    #     print(r)
    # print(len(results), '-- трейдов за период (за сегодня)')
    # results = get_exchange_securities('MOEX')
    # for r in result:
    #     print(r)
    # print(len(result), '-- инструментов')
