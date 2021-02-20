import asyncio
import json
import logging
import os
from json import JSONDecodeError

import aiohttp
import requests
from settings import (
    REFRESH_TOKEN,
    URL_OAUTH,
    URL_API,
    EXCHANGE,
    LOGGING
)

if LOGGING:
    logging.basicConfig(
        filename='status.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d-%b-%y %H:%M:%S',
        level=logging.DEBUG
    )


def _get_headers():
    bearer = os.environ.get('JWT_TOKEN')
    if not bearer:
        logging.error('Не найден JWT токен, запустите get_jwt()!')
        return None
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {bearer}"
               }
    return headers


def _check_results(res):
    if res.status_code != 200:
        if LOGGING:
            logging.error(f'Ошибка: {res.status_code}')
        return
    try:
        return json.loads(res.content)
    except JSONDecodeError as e:
        if LOGGING:
            logging.error(f'Ошибка декодирования JSON: {e}')


async def _get_orderbook(sec: str, depth: int = 5):
    session = aiohttp.ClientSession()
    res = await session.get(
        url=f'{URL_API}/md/v2/orderbooks/{EXCHANGE}/{sec}?depth={depth}',
        headers=_get_headers()
    )
    if res.status != 200:
        await session.close()
        return sec, None

    data = await res.json()
    await session.close()
    return sec, data


# ---------------- Блок "Информация о клиенте -------------------
def get_jwt(refresh=REFRESH_TOKEN):
    """
    Создать JWT Token и поместить в env окружение процесса.
    Следует вызывать перед любым обращением к другим функциям API
    Время жизни JWT ~ 5 мин, обновляйте чаще!

    :param refresh: Токен обновления, создается в личном кабинете
    https://oauthdev.alor.ru
    """
    payload = {'token': refresh}
    res = requests.post(
        url=f'{URL_OAUTH}/refresh',
        params=payload
    )
    if res.status_code != 200:
        if LOGGING:
            logging.error(f'Ошибка получения JWT токена: {res.status_code}')
        return None
    try:
        token = res.json()
        os.environ["JWT_TOKEN"] = token.get('AccessToken')
    except JSONDecodeError as e:
        if LOGGING:
            logging.error(f'Ошибка декодирования JWT токена: {e}')


def get_portfolios(username):
    """
    Получение списка серверов и идентификаторы клиентского портфеля

    :param username: Имя пользователя (например P002034)
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/client/v1.0/users/{username}/portfolios',
        headers=_get_headers()
    )
    return _check_results(res)


def get_orders_info(portfolio: str, exchange: str = 'MOEX'):
    """
    Запрос информации о всех заявках

    :param portfolio: Идентификатор клиентского портфеля (например D39004)
    :param exchange: Биржа Available values : MOEX, SPBX
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/clients/{exchange}/{portfolio}/orders',
        headers=_get_headers()
    )
    return _check_results(res)


def get_order_info(portfolio: str, orderId: str, exchange: str = 'MOEX'):
    """
    Запрос информации о выбранной заявке

    :param portfolio: Идентификатор клиентского портфеля (например D39004)
    :param orderId: Идентификатор заявки (например 18995978560)
    :param exchange: Биржа Available values : MOEX, SPBX
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/clients/{exchange}/{portfolio}/orders/{orderId}',
        headers=_get_headers()
    )
    return _check_results(res)


def get_stoporders_info(portfolio: str, exchange: str = 'MOEX'):
    """Запрос информации о всех стоп-заявках

    :param portfolio: Идентификатор клиентского портфеля (например D39004)
    :param exchange: Биржа Available values : MOEX, SPBX
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/clients/{exchange}/{portfolio}/stoporders',
        headers=_get_headers()
    )
    return _check_results(res)


def get_stoporder_info(portfolio: str, orderId: str, exchange: str = 'MOEX'):
    """Запрос информации о выбранной стоп-заявке

    :param portfolio: Идентификатор клиентского портфеля (например D39004)
    :param orderId: Идентификатор заявки (например 18995978560)
    :param exchange: Биржа Available values : MOEX, SPBX
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/clients/{exchange}'
            f'/{portfolio}/stoporders/{orderId}',
        headers=_get_headers()
    )
    return _check_results(res)


def get_summary_info(portfolio: str, exchange: str = 'MOEX'):
    """
    Запрос сводной информации

    :param portfolio: Идентификатор клиентского портфеля (например D39004)
    :param exchange: Биржа Available values : MOEX, SPBX
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/clients/{exchange}/{portfolio}/summary',
        headers=_get_headers()
    )
    return _check_results(res)


def get_positions_info(portfolio: str, exchange: str = 'MOEX'):
    """
    Запрос информации о позициях

    :param portfolio: Идентификатор клиентского портфеля
    :param exchange: Биржа Available values : MOEX, SPBX
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/Clients/{exchange}/{portfolio}/positions',
        headers=_get_headers()
    )
    return _check_results(res)


def get_position_info(symbol: str, portfolio: str, exchange: str = 'MOEX'):
    """
    Запрос информации о позици по инструменту

    :param symbol: Инструмент (GAZP)
    :param portfolio: Идентификатор клиентского портфеля
    :param exchange: Биржа Available values : MOEX, SPBX
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/'
            f'Clients/{exchange}/{portfolio}/positions/{symbol}',
        headers=_get_headers()
    )
    return _check_results(res)


def get_trades_info(portfolio: str, exchange: str = 'MOEX'):
    """Запрос информации о сделках

    :param portfolio: Идентификатор клиентского портфеля
    :param exchange: Биржа Available values : MOEX, SPBX
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/'
            f'Clients/{exchange}/{portfolio}/trades',
        headers=_get_headers()
    )
    return _check_results(res)


def get_trade_info(ticker: str, portfolio: str, exchange: str = 'MOEX'):
    """Запрос информации о сделках по выбранному инструменту

    :param ticker: Инструмент (GAZP)
    :param portfolio: Идентификатор клиентского портфеля
    :param exchange: Биржа Available values : MOEX, SPBX
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/'
            f'Clients/{exchange}/{portfolio}/{ticker}/trades',
        headers=_get_headers()
    )
    return _check_results(res)


def get_fortrisk_info(portfolio: str, exchange: str = 'MOEX'):
    """
    Запрос информации о рисках

    :param portfolio: Идентификатор клиентского портфеля
    :param exchange: Биржа Available values : MOEX
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/'
            f'Clients/{exchange}/{portfolio}/fortsrisk',
        headers=_get_headers()
    )
    return _check_results(res)


def get_risk_info(portfolio: str, exchange: str = 'MOEX'):
    """
    Запрос информации о рисках

    :param portfolio: Идентификатор клиентского портфеля
    :param exchange: Биржа Available values : MOEX, SPBX
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/'
            f'Clients/{exchange}/{portfolio}/risk',
        headers=_get_headers()
    )
    return _check_results(res)


# ------------------ Блок Ценные бумаги / инструменты ---------------------
def get_securities_info(query: str,
                        limit: int = None,
                        sector: str = None,
                        cficode: str = None,
                        exchange: str = None):
    """
    Запрос информации об имеющихся ценных бумагах

    :param exchange: Фильтр по коду биржи MOEX или SPBX
    :param limit: Ограничение на количество выдаваемых результатов поиска
    :param sector: Рынок на бирже Available values : FORTS, FOND, CURR
    :param cficode: Код финансового инструмента по стандарту ISO 10962 (EXXXXX)
    :param query: Фильтр про инструменту GAZP
    :return: [ Simple JSON ]
    """
    payload = {'query': query,
               'limit': limit,
               'sector': sector,
               'cficode': cficode,
               'exchange': exchange
               }
    res = requests.get(
        url=f'{URL_API}/md/v2/securities',
        params=payload,
        headers=_get_headers()
    )
    return _check_results(res)


def get_all_securities_info(exchange: str):
    """
    Запрос информации об инструментах на выбранной бирже
    ВНИМАНИЕ! Возвращает все инструменты! ~ 25 мб

    :param exchange:  Биржа Available values : MOEX, SPBX

    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/Securities/{exchange}',
        headers=_get_headers()
    )
    return _check_results(res)


def get_security_info(exchange: str, ticker: str):
    """
    Запрос информации о выбранном финансовом инструменте на бирже
    (Аналог get_securities_info())

    :param exchange: Биржа : MOEX, SPBX
    :param ticker: Инструмент GAZP
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/Securities/{exchange}/{ticker}',
        headers=_get_headers()
    )
    return _check_results(res)


def get_quotes_list(symbols: str):
    """
    Запрос информации о котировках для выбранных инструментов и бирж

    :param symbols: Принимает несколько пар биржа-тикер.
     Пары отделены запятыми. Биржа и тикер разделены двоеточием.
     Например MOEX:SBER,MOEX:GAZP,SPBX:AAPL
    :return: Simple JSON
    """
    res = requests.get(
        url=f'{URL_API}/md/v2/securities/{symbols}/quotes',
        headers=_get_headers()
    )
    return _check_results(res)


def get_orderbooks(sec_ls: list = None, depth: int = 5):
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

    futures = [_get_orderbook(sec, depth=depth) for sec in sec_ls]
    loop = asyncio.get_event_loop()
    orderbooks = loop.run_until_complete(asyncio.gather(*futures))
    return orderbooks


def get_today_trades(
        exchange: str,
        ticker: str,
        start: int = None,
        finish: int = None):
    """
    Запросить данные о всех сделках (лента) по ценным бумагам за сегодняшний
     день. Если указать UTC метки start и finish, вернет данные
     трейдов в промежутке между ними.

    :param exchange: Биржа : MOEX, SPBX
    :param ticker: Инструмент GAZP
    :param start: Начало отрезка времени (UTC) для фильтра результатов
    :param finish: Конец отрезка времени (UTC) для фильтра результатов
    :return: Simple JSON
    """
    payload = {'from': start, 'to': finish}
    res = requests.get(
        url=f'{URL_API}/md/v2/Securities/{exchange}/{ticker}/alltrades',
        data=payload,
        headers=_get_headers()
    )
    return _check_results(res)


if __name__ == '__main__':
    get_jwt(REFRESH_TOKEN)
    print(os.environ.get('JWT_TOKEN'))
    # print(get_summary_info('7500031'))
    # print(get_order_info('7500031', '18995978560'))
    # print(get_position_info('GDH1', '7500031'))
    # print(get_trades_info('7500031'))
    # print(get_fortrisk_info('7500031'))
    # print(get_risk_info('7500031'))
    print(get_securities_info('GAZP'))
    print(get_security_info('MOEX', 'GAZP'))
    print(get_quotes_list('MOEX:SBER,MOEX:GAZP,SPBX:AAPL'))

    results = get_today_trades('MOEX', 'GDH1', 1613744707932, 1613751791675)
    for r in results:
        print(r)
    print(len(results), '-- трейдов за период (за сегодня)')
    # results = get_exchange_securities('MOEX')
    # for r in result:
    #     print(r)
    # print(len(result), '-- инструментов')
