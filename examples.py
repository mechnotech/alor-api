import time

from client import Connection
# from misc import print_orderbook
from settings import REFRESH_TOKEN, USERNAME

# Запросить JWT токен используя Refresh токен, JWT токен будет помещён в env
cn = Connection(REFRESH_TOKEN, USERNAME)
cn.exchange = 'MOEX'
print(cn.get_portfolios())
cn.portfolio = '7500031'
print(cn.jwt_token)
time.sleep(1)
print(cn.get_summary_info())
print(cn.jwt_token)
time.sleep(2)
print(cn.get_orders_info())
print(cn.jwt_token)

# Запросить номера счетов пользователя для рынков:
# Получение списка серверов. В ответе в поле tradeServerCode содержится
# значение которое надо использовать
# portfolios = get_portfolios(USERNAME)
# for k, v in portfolios.items():
#     print(k, v[0].get('portfolio'))
#
# # Запросить стакан для одного инструмента (глубина стакана 20 ордеров)
# securities = ['GAZP', ]
# depth = 20
# result = get_orderbooks(securities, depth)
# for r in result:
#     print_orderbook(r)
#
# # Запросить стаканы нескольких инструментов (глубина стакана по умолчнию =
# # 5 ордеров)
# securities = ['GAZP', 'SBER', 'AFLT']
# result = get_orderbooks(securities)
# for r in result:
#     print_orderbook(r)
