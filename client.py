import asyncio
import json
import logging
import os
from json import JSONDecodeError
from aiofile import async_open

import aiohttp
import requests
from settings import (
    REFRESH_TOKEN,
    URL_OAUTH,
    URL_API,
    EXCHANGE,
    LOGGING, FUTURES_SET
)

if LOGGING:
    logging.basicConfig(
        filename='status.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d-%b-%y %H:%M:%S',
        level=logging.DEBUG
    )


def get_jwt_token(refresh=REFRESH_TOKEN):
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
    bearer = os.environ.get('JWT_TOKEN')
    if not bearer:
        return None
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {bearer}"
               }
    res = requests.get(
        url=f'{URL_API}/client/v1.0/users/{username}/portfolios',
        headers=headers
    )
    if res.status_code != 200:
        if LOGGING:
            logging.error(f'Ошибка: {res.status_code}')
        return
    try:
        return json.loads(res.content)
    except JSONDecodeError as e:
        if LOGGING:
            logging.error(f'Ошибка декодирования JSON: {e}')


async def _get_orderbook(sec, depth=5, save=False):
    session = aiohttp.ClientSession()
    bearer = os.environ.get('JWT_TOKEN')
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {bearer}"
               }
    res = await session.get(
        url=f'{URL_API}/md/v2/orderbooks/{EXCHANGE}/{sec}?depth={depth}',
        headers=headers
    )
    if res.status != 200:
        await session.close()
        return sec, None

    data = await res.json()
    await session.close()
    if save:
        async with async_open(f'futures_log/{sec}.txt', 'a+') as afp:
            await afp.write(json.dumps(data) + '\n')
    return sec, data


def get_orderbooks(sec_ls: list = None, depth: int = 5, save=False):
    """
    Получить списки заявок bid/ask для ценных бумаг
    :param save: Сохранять результат в файл (опция)
    :param depth: Глубина стакана
    :param sec_ls: Список ценных бумаг
    :return:
    """
    if sec_ls is None:
        return None

    futures = [_get_orderbook(sec, depth=depth, save=save) for sec in sec_ls]
    loop = asyncio.get_event_loop()
    orderbooks = loop.run_until_complete(asyncio.gather(*futures))
    return orderbooks


def check_or_create_files():
    for sec in FUTURES_SET:
        try:
            with open(f'futures_log/{sec}.txt', 'r'):
                pass
        except FileNotFoundError:
            with open(f'futures_log/{sec}.txt', 'a+'):
                pass
            continue


if __name__ == '__main__':
    get_jwt_token(REFRESH_TOKEN)
    print(os.environ.get('JWT_TOKEN'))
