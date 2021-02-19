from datetime import datetime


def print_orderbook(result):
    timestamp = result[1].get('timestamp')
    bids = result[1].get('bids')
    asks = result[1].get('asks')
    depth = len(asks) if len(asks) >= len(bids) else len(bids)
    print('\n')
    print(result[0], datetime.fromtimestamp(timestamp))
    print(f'|volume{" ":5} bids{"":7} asks{" ":5} volume|')
    for i in range(depth):
        try:
            b_price = bids[i].get('price')
            b_volume = bids[i].get('volume')
        except IndexError:
            b_price = b_volume = 0
        try:
            a_price = asks[i].get('price')
            a_volume = asks[i].get('volume')
        except IndexError:
            a_price = a_volume = 0
        print(f'|{b_volume:4} {b_price:12} {a_price:12} {a_volume:9}|')
