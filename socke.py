import json

import websocket

try:
    import thread
except ImportError:
    import _thread as thread
from datetime import datetime
import time

from client import Api

from settings import REFRESH_TOKEN, USERNAME

alor = Api(REFRESH_TOKEN, USERNAME)
alor.exchange = 'MOEX'
now = datetime.now()
ts = datetime.timestamp(now)
guid = alor._random_order_id

request = {
  "opcode": "SummariesGetAndSubscribeV2",
  "portfolio": "7500031",
  "token": f"{alor.jwt_token}",
  "exchange": "MOEX",
  "format": "Simple",
  "guid": f"{alor._random_order_id}"
}

request1 = {
  "opcode": "OrderBookGetAndSubscribe",
  "code": "GDH1",
  "exchange": "MOEX",
  "depth": 2,
  "format": "Simple",
  "delayed": False,
  "guid": f"{alor._random_order_id}",
  "token": f"{alor.jwt_token}"
}

request1_1 = {
  "opcode": "OrderBookGetAndSubscribe",
  "code": "GDH1",
  "exchange": "MOEX",
  "depth": 2,
  "format": "Simple",
  "delayed": False,
  "guid": f"{alor._random_order_id}",
  "token": f"{alor.jwt_token}"
}

request2 = {
  "opcode": "BarsGetAndSubscribe",
  "code": "SBER",
  "token": f"{alor.jwt_token}",
  "tf": 'D',
  "from": 1583928181, #ts,
  "exchange": "SPBX",
  "format": "Simple",
  "delayed": False,
  "guid": f"{alor._random_order_id}"
}

request3 = {
  "opcode": "QuotesSubscribe",
  "code": "GAZP",
  "exchange": "MOEX",
  "format": "Simple",
  "guid": f"{alor._random_order_id}",
  "token": f"{alor.jwt_token}"
}

my_request = request1


def on_cont_message(ws, message):
    print(f'Продолжение от сервера: \n{message}')

def on_message(ws, message):
    print(f'Сообщение от сервера: \n{message}')


# def on_data(ws, message, data_type, flag):
#     print(f'Данные от сервера: {message} {data_type} {flag}')


def on_error(ws, error):
    print(error)


def on_close(ws):
    # unsub = {
    #     "opcode": "unsubscribe",
    #     "token": f"{alor.jwt_token}",
    #     "guid": my_request.get('guid')
    # }
    # ws.send(json.dumps(unsub))
    print("### closed ###")


def on_open(ws):
    ws.send(json.dumps(request))
    ws.send(json.dumps(my_request))
    ws.send(json.dumps(request1_1))
    ws.send(json.dumps(request3))
    # def run(*args):
    #     ws.send(json.dumps(request1))
    #     #ws.close()
    #     print("thread terminating...")
    #
    # thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://apidev.alor.ru/ws",
                                on_open=on_open,
                                on_message=on_message,
                                on_cont_message=on_cont_message,
                                on_error=on_error,
                                on_close=on_close,
                                #on_data=on_data
                                )

    ws.run_forever()
