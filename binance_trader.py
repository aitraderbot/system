from binance import Client

from redis import Redis
from json import dumps, loads
from time import time

from database import DatabaseRouter



class BinanceTrader:

    def account_info():