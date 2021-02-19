from client import get_jwt_token, get_orderbooks, get_portfolios
from misc import print_orderbook
from settings import REFRESH_TOKEN, USERNAME

# Запросить JWT токен используя Refresh токен, JWT токен будет помещён в env
get_jwt_token(REFRESH_TOKEN)

# Запросить номера счетов пользователя для рынков:
portfolios = get_portfolios(USERNAME)
for k, v in portfolios.items():
    print(k, v[0].get('portfolio'))

# Запросить стакан для одного инструмента (глубина стакана 20 ордеров)
securities = ['GAZP', ]
depth = 20
result = get_orderbooks(securities, depth)
for r in result:
    print_orderbook(r)

# Запросить стаканы нескольких инструментов (глубина стакана по умолчнию =
# 5 ордеров)
securities = ['GAZP', 'SBER', 'AFLT']
result = get_orderbooks(securities)
for r in result:
    print_orderbook(r)
