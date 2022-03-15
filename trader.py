"""
    Mr Charehei 2022-03-10
    trade (market or limit) by each broker (kucoin or coinex)
    create transaction and save it in database (redis)
    using kucoin trade account 

    trade = trade("amir@gmail.com", "opal")

"""
from kucoin.client import Client
from kucoin.exceptions import KucoinAPIException
from numpy import size

from redis import Redis
from json import dumps, loads
from time import time

from database import DatabaseRouter


class KucoinTrader:

    def __init__(self, symbol: str = None, side: str = None) -> None:

        """ 
            :param symbol = valid symbol for kucoin like BTC-USDT
            :param side = buy or sell
        """

        self.redis = Redis()
        self.symbol = symbol
        self.side = side

        api_key, secret_key, passphrase = self.get_keys()
        self.client = Client(api_key, secret_key, passphrase)

    def get_keys(self, email: str = None):

        """
            read keys from mysql by each user email
        """

        # read keys from mysql database by email
        api_key1 = "622712c56b173b000124c40c"
        secret_key1 = "f3d13987-378d-46ed-9606-7721910d3ec3"
        passphrase1 = "aran.run"
        return api_key1, secret_key1, passphrase1

    def account_info(self, symbol: str = None, account_type: str = "trade"):

        """
            https://docs.kucoin.com/#get-an-account
            get an individual account

            :param symbol:
            :param account_type = main or trade or something else
        """

        if symbol == "all":
            return self.client.get_accounts()

        if symbol:
            s = symbol
        else:
            s = self.symbol

        return self.client.get_accounts(s, account_type)

    def inner_transfer(self, _from: str, _to: str):
        amount = self.account_info(symbol="all")[0]["available"]
        if self.symbol:
            s = self.symbol.split("-")[0]
        self.client.create_inner_transfer(s, _from, _to, amount)
        print("transfer done")

    def market_order(self, amount=None):

        """
            https://docs.kucoin.com/#place-a-new-order
            create a market order
        """

        if not self.symbol:
            raise Exception("symbol is invalid or is null")

        if amount is None:
            # trade on whole asset of trade
            if self.side == "buy":
                symbol = self.symbol.split("-")[1]
            elif self.side == "sell":
                symbol = self.symbol.split("-")[0]
            else:
                raise Exception("invalid side")

            amount = float(self.account_info(symbol)[0]["available"])

        if self.side == "buy":
            try:
                res = self.client.create_market_order(symbol=self.symbol, side=self.side, funds=amount)
                return res
            except KucoinAPIException as error:
                if error.code == "200004":
                    raise Exception("no enough asset in account for buying %s" % self.symbol)
                elif error.code == "400100":
                    raise Exception("parameter error")

        elif self.side == "sell":
            count = 1
            while True:
                try:
                    int_amount = int(amount)
                    decimal = str(amount).split(".")

                    if len(decimal) == 1:
                        amount = int_amount
                    else:
                        str_decimal = decimal[1][:-count]
                        amount = float("%s.%s" % (int_amount, str_decimal))

                    res = self.client.create_market_order(symbol=self.symbol, side=self.side, size=str(amount))
                    break
                except KucoinAPIException as error:
                    if error.code == "200004":
                        continue
                        # raise Exception("cannot trade with size %s for %s" % (amount, self.symbol))
                    elif error.code == "400100":
                        continue
            return res

    def limit_order(self, amount, price):
        if not self.symbol:
            raise Exception("symbol is invalid or is null")

        if not self.symbol:
            raise Exception("symbol is invalid or is null")

        if not amount:
            # trade on whole asset of trade
            if self.side == "buy":
                symbol = self.symbol.split("-")[1]
            elif self.side == "sell":
                symbol = self.symbol.split("-")[0]
            else:
                raise Exception("invalid side")

            amount = float(self.account_info(symbol)[0]["available"])

        amount = round(amount, 4)
        try:
            res = self.client.create_limit_order(self.symbol, self.side, str(price), str(amount))
            return res
        except KucoinAPIException as error:
            if error.code == "200004":
                self.inner_transfer("main", "trade")
                return self.limit_order(amount, price)
                
        except Exception as error:
            print("error: ", error)

    def save_trx(self, data: dict):
        # current_USDT, current_ETH, trade_ETH,  trade_USDT, side, datetime, order_id, strategy_name
        if self.redis.hgetall("kucoin_trx"):
            strategy_name = data["strategy_name"]
            trx_list = self.read_trx(strategy_name)
            if not trx_list:
                trx_list = []
            trx_list.append(data)
            data = dumps(trx_list)
            self.redis.hset("kucoin_trx", strategy_name, data)
        else:
            strategy_name = data["strategy_name"]
            data = dumps([data])
            self.redis.hset("kucoin_trx", strategy_name, data)

    def read_trx(self, strategy_name: str):
        # current_USDT, current_ETH, trade_ETH,  trade_USDT, side, datetime, order_id
        trx = self.redis.hget("kucoin_trx", strategy_name)
        if trx:
            return loads(trx)

    def last_trade_price(self):
        return self.client.get_ticker(self.symbol)

    def trade(self, email: str, strategy_name: str, symbol: str, time_frame: str):
        try:
            database = DatabaseRouter(broker="kucoin")
            setting = database.read_asset_strategy(email, strategy_name, symbol, time_frame)
        except:
            raise Exception("no settings are set for %s on %s" % (email, strategy_name))

        # read all transactions for strategy_name
        last_trx = self.read_trx(strategy_name)
        # get all coin and pair available
        account_info = self.account_info("all")
        size = None

        coin, pair = self.symbol.split("-")
        if self.side == "buy":
            symbol = pair
        elif self.side == "sell":
            symbol = coin
        else:
            raise Exception("invalid side (sell or buy)")

        if not last_trx:
            # should buy
            if not [i for i in account_info if i["currency"] == symbol]:
                print("symbol not found in account .. waiting for buy")
                return

            if self.side == "sell":
                return

            size = float(self.account_info(symbol)[0]["available"])
            if size > setting["amount"]:
                size = setting["amount"]
        else:
            last_trx = last_trx[-1]
            if self.side == "buy" and last_trx["side"] == "sell":
                size = setting["amount"]
            elif self.side == "sell" and last_trx["side"] == "buy":
                size = last_trx["trade_%s" % coin]
            else:
                return

        # just market order for now
        order_id = self.market_order(amount=size)["orderId"]
        last_price = self.last_trade_price()["price"]
        print("market order sent")

        # create new transaction
        account_info_after_order = self.account_info("all")

        before_available_coin = [i for i in account_info if i["currency"] == coin]
        if before_available_coin:
            before_current_coin = before_available_coin[0]["available"]
        else:
            before_current_coin = 0

        before_available_pair = [i for i in account_info if i["currency"] == pair]
        if before_available_pair:
            before_current_pair = before_available_pair[0]["available"]
        else:
            before_current_pair = 0

        current_coin_after = [i for i in account_info_after_order if i["currency"] == coin][0]["available"]
        current_pair_after = [i for i in account_info_after_order if i["currency"] == pair][0]["available"]

        trade_coin = float(current_coin_after) - float(before_current_coin)
        trade_pair = float(current_pair_after) - float(before_current_pair)

        data = {"current_%s" % coin: current_coin_after, "current_%s" % pair: current_pair_after,
                "trade_%s" % coin: trade_coin, "trade_%s" % pair: trade_pair,
                "side": self.side, "last_price": last_price, "email": email,
                "timestamp": time(), "order_id": order_id, "strategy_name": strategy_name
                }

        self.save_trx(data)
        print("Done")

    def get_order_list(self):
        res = self.client.get_orders()
        print(res)


class CoinexTrader:

    def __init__(self, symbol: str, side: str):
        self.symbol = symbol
        self.side = side


# app = KucoinTrader("MATIC-USDT", "sell")
# print(app.market_order())

app = KucoinTrader()
print(app.account_info(symbol="all"))

# app.inner_transfer("trade", "main")
# print(app.last_trade_price()["price"])
# app.trade("amir@gmail.com", "opal")
# app.get_order_list()
