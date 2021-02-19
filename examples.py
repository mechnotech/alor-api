import time

from client import get_jwt_token, get_orderbooks, get_portfolios
from settings import REFRESH_TOKEN, OIL, USERNAME

# Запросить JWT токен используя Refresh токен, JWT токен будет помещён в env
get_jwt_token(REFRESH_TOKEN)

# Запросить номера счетов пользователя для рынков:
portfolios = get_portfolios(USERNAME)
for k, v in portfolios.items():
    print(k, v[0].get('portfolio'))


count = 0
while True:
    if count % 60 == 0:
        get_jwt_token(REFRESH_TOKEN)
        print('Токен обновлен')
    result = get_orderbooks(1, OIL)
    print(count, result)
    time.sleep(1)
    count += 1
