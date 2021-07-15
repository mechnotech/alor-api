from client import Api
from misc import print_orderbook
from settings import REFRESH_TOKEN, USERNAME

# Создаем объект API используя Refresh токен и Аккаунт - username
alor = Api(REFRESH_TOKEN, USERNAME)

# Указываем биржу
alor.exchange = 'MOEX'

# Получение списка серверов для рынков: Валютный, Срочный, Фондовый,
# интересует значения 'portfolio'
print('\n Получение списка серверов для рынков')
print(alor.get_portfolios())

# Указываем рынок (portfolio для Фондового рынка)
alor.portfolio = 'D00031'

# print('Установка ордера:')
# print(alor.set_market_order(ticker='GOLD-9.21', side='buy', quantity=1))

# Запрос сводной информации
# print(alor.get_summary_info())


# Запрос информации о всех заявках
print('\n Запрос информации о всех заявках')
print(alor.get_orders_info())

# print('\n Установить лимитную заявку: купить 10 лотов GAZP по 290')
# print(alor.set_limit_order(ticker='GAZP', quantity=10, price=290, side='buy'))

# print('\n Изменяю лимитную заявку №24640949466')
# print(alor.change_limit_order(ticker='GAZP', side='buy', quantity=10, price=295, order_id='24640949466'))

print('\n Отменяю лимитню заявку №24640950379')
print(alor.cancel_order(order_id='24640950379', stop=False))

# Запрос информации о выбранной заявке
# print('\n Запрос информации о выбранной заявке')
# print(alor.get_order_info(orderId='24640940528'))
#
# # Запрос информации о всех стоп-заявках
# print(alor.get_stoporders_info())
#
# # Запрос информации о выбранной стоп-заявке
# print(alor.get_stoporder_info(orderId='102200300403'))

# Запрос информации о позициях
print('\n Запрос информации о позициях')
print(alor.get_positions_info())


# Переключаем portfolio в режим Срочного рынка
alor.portfolio = '7500031'

# Запрос информации о позиции по инструменту (фьючерс Золото 9.21) если такой
# фьючерс был куплен/продан, иначе вернет None
print('\n Запрос информации о позиции по инструменту: GOLD-9.21')
print('GOLD-9.21', alor.get_position_info(ticker='GOLD-9.21'))

# Запрос информации о сделках
print(alor.get_trades_info())

# Запрос информации о сделках по выбранному инструменту
# print(alor.get_trade_info(ticker='GDU1'))

# # Запрос информации о рисках
# print(alor.get_fortrisk_info())
# print(alor.get_risk_info())
#
# Запрос информации об имеющихся ценных бумагах
print('\n Запрос информации об имеющихся ценных бумагах GOLD-9.21')
print(alor.get_securities_info(ticker='GOLD-9.21'))
# print(alor.get_security_info(ticker='GAZP'))
#
# # Запрос информации о котировках для выбранных инструментов и бирж
# symbols = 'MOEX:SBER,MOEX:GAZP,SPBX:AAPL'
# print(alor.get_quotes_list(symbols=symbols))

# Запросить стакан для одного инструмента (глубина стакана 20 ордеров)
securities = ['GOLD-9.21', ]
depth = 20
result = alor.get_orderbooks(securities, depth)
for r in result:
    print_orderbook(r)

# Запросить стаканы нескольких инструментов (глубина стакана по умолчнию =
# 5 ордеров)
# securities = ['GAZP', 'SBER', 'AFLT']
# result = alor.get_orderbooks(securities)
# for r in result:
#     print_orderbook(r)

# Запросить данные о всех сделках (лента) по ценным бумагам
# за сегодняшний день
# print(alor.get_today_trades(ticker='GAZP'))
#
# Запрос инфо фьючерсе (возвращает ближайший
# к экспирации фьючерс из семейства GOLD)
print('\n Запрос инфо о фьючерсе GOLD')
print(alor.get_futures_quotes(symbol='GOLD'))

# # Запрос истории рынка для выбранных биржи и финансового инструмента
# print(alor.get_history(ticker='GAZP', start=1614329535,
#                        finish=1614347535, tfs=300))
#
# # Запрос текущего UTC времени в формате Unix.
# print(alor.get_time())
