from client import get_jwt_token, get_orderbooks
from settings import REFRESH_TOKEN


class Order:
    def __init__(self):
        self.price = 0
        self.volume = 0


class BidOrder(Order):
    pass


class AskOrder(Order):
    pass


class FuturPair:
    def __init__(self, first, second):
        get_jwt_token(REFRESH_TOKEN)
        get_orderbooks([first, second])
        self.f_b_pice = None
        self.f_b_volume = None
        self.f_a_price = None
        self.f_a_volume = None
        self.s_b_pice = None
        self.s_b_volume = None
        self.s_a_price = None
        self.s_a_volume = None
