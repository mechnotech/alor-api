import json

import websocket

try:
    import thread
except ImportError:
    import _thread as thread
import time

from client import Api

from settings import REFRESH_TOKEN, USERNAME

alor = Api(REFRESH_TOKEN, USERNAME)
alor.exchange = 'MOEX'

request = {
  "opcode": "SummariesGetAndSubscribeV2",
  "portfolio": "7500031",
  "token": f"{alor.jwt_token}",
  "exchange": "MOEX",
  "format": "Simple",
  "guid": f"{alor._random_order_id}"
}

request2 = {
  "opcode": "BarsGetAndSubscribe",
  "code": "SBER",
  "token": f"{alor.jwt_token}",
  "tf": 60,
  "from": 1536557084,
  "exchange": "MOEX",
  "format": "Simple",
  "delayed": False,
  "guid": f"{alor._random_order_id}"
}

request3 = {
  "opcode": "QuotesSubscribe",
  "code": "GDH1",
  "exchange": "MOEX",
  "format": "Simple",
  "guid": f"{alor._random_order_id}",
  "token": f"{alor.jwt_token}"
}

def on_message(ws, message):
    print(f'Сообщение от сервера: {message}')


# def on_data(ws, message, data_type, flag):
#     print(f'Данные от сервера: {message} {data_type} {flag}')


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        ws.send(json.dumps(request2))
        #ws.close()
        print("thread terminating...")

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://apidev.alor.ru/ws",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                # on_data=on_data
                                )

    ws.run_forever()
