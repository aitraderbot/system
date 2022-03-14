"""
    Mr Charehei 2022-03-10
    main file for this system.
    run strategy by each python thread
    >>> python3 manager.py run strategy_name symbol time_frame broker
    >>> python3 manager.py run opal ADA-USDT 1hour kucoin

    trade by signal for each user who choose the strategy
    check condition by data and get signal (buy/sell)
"""
from time import sleep
import sys
import os
import pandas as pd
from datetime import datetime
import hashlib

from indicator.qpal import Qpal
from indicator.jasper import Jasper
from indicator.opal import Opal
from indicator.amber import Amber
from indicator.amatis import Amatis

from strategy import Strategy
from database import DatabaseRouter
from indicator.data import Data
from trader import CoinexTrader, KucoinTrader


class Manager:
    strategy = Strategy()
    database = DatabaseRouter("kucoin")
    data = Data()

    @staticmethod
    def make_hash(pwd: str):
        return hashlib.sha256(pwd.encode()).hexdigest()

    def authenticate(self, email: str, password: str):
        password = self.make_hash(password)
        user = self.database.read_user(email, password)
        if user:
            return True
        return False

    def add_user(self, data: dict):
        
        try:
            data["password"] = self.make_hash(data["password"])
        except KeyError:
            raise Exception("no password in data")

        self.database.write_user(data)

    def report(self, data: dict):
        transactions = self.strategy.get_transactions(data)
        if transactions:
            return transactions

    def report_file(self, data: dict):
        d = self.report(data)
        d = [i for i in d.values()][0]
        df = pd.DataFrame(d)
        print(df.columns)
        df["time"] = pd.to_datetime(df["timestamp"], unit="s")
        print(df)
        # ./transaction_broker_strategy-name.csv
        filename = "./transaction_%s_%s.csv" % (data["broker"], data["strategy_name"])
        df.to_csv(filename)
        return os.path.abspath(filename)

    def strategy_to_user(self, data: dict):
        # data = user_email: str, broker: str, stra_name: str, symbol: str, time_frame: str
        user_email = data["email"]
        broker = data["broker"]
        stra_name = data["strategy_name"]
        symbol = data["symbol"]
        time_frame = data["time_frame"]

        user = self.database.read_user(user_email)
        if user:
            stra = self.strategy.read(stra_name, symbol, time_frame, broker)
            if user_email not in stra["user_list"]:
                stra["user_list"].append(user_email)
            print(stra["user_list"])
            self.strategy.update(stra)

    @staticmethod
    def check_condition(data: dict, length: int, setting_strategy: dict) -> bool:

        """
            check condition [{parameters}]
            :param setting_strategy = setting for each strategy
            :param length = length of data
            :param data = OHCL data
            :return = True or False
        """

        df = pd.DataFrame(data)
        df.sort_values("time", inplace=True)
        df.reset_index(inplace=True)
        df.tail(length)
        df.rename(columns={"time": "date", "open_price": "open", "close_price": "close",
                           "high_price": "high", "low_price": "low"}, inplace=True)

        df["open"] = df["open"].astype(float)
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["volume"] = df["volume"].astype(float)

        if setting_strategy["strategy_name"] == "opal":
            o = Opal(df)
            result = o.preprocess()
        elif setting_strategy["strategy_name"] == "jasper":
            j = Jasper(df)
            result = j.preprocess()
        elif setting_strategy["strategy_name"] == "qpal":
            q = Qpal(df)
            result = q.preprocess()
        elif setting_strategy["strategy_name"] == "amber":
            a = Amber(df)
            result = a.preprocess()
        elif setting_strategy["strategy_name"] == "amatis":
            a = Amatis(df)
            result = a.preprocess()
        else:
            raise Exception("%s is invalid" % setting_strategy["strategy_name"])
        
        return result

    @staticmethod
    def send_signal(email_list: list, strategy: dict):

        broker = strategy["broker"]
        strategy_name = strategy["name"]
        symbol = strategy["symbol"]
        time_frame = strategy["time_frame"]
        side = strategy["type"]

        if broker == "kucoin":
            trader = KucoinTrader(symbol, side)
        elif broker == "coinex":
            trader = CoinexTrader(symbol, side)
        else:
            raise Exception("invalid broker")

        for email in email_list:
            # trading
            trader.trade(email, strategy_name, symbol, time_frame)

    @staticmethod
    def make_condition(now_time: datetime, time_frame: str):
        if "min" in time_frame:
            _min = int(time_frame.replace("min", ""))
            condition = (now_time.minute % _min == 0 and now_time.second == 0)
        elif "hour" in time_frame:
            _hour = int(time_frame.replace("hour", ""))
            condition = (now_time.hour % _hour == 0 and now_time.minute == 0 and now_time.second == 0)
        else:
            raise Exception("invalid duration")

        return condition

    def run_strategy(self, stra_name: str, symbol: str, time_frame: str, broker: str):

        """
            run each strategy in a thread
            :param stra_name = name of strategy like ruby
            :param symbol = valid symbol for broker
            :param time_frame = time frame for broker (5min, 1day, ...)
            :param broker = valid brokers (Binance,Coinex,Kucoin)
        """

        strategy = self.strategy.read(stra_name, symbol, time_frame, broker)
        strategy_setting = {
                "strategy_name": stra_name,
                "symbol": symbol, 
                "time_frame": time_frame,
                "broker": broker
        }

        while True:

            now = datetime.now()
            duration = 1
            condition = self.make_condition(now, strategy["duration"])

            if condition:
                
                while True:
                    try:
                        data = self.data.get(broker, symbol, time_frame, strategy["candle_count"])
                        result = self.check_condition(data, strategy["candle_count"], strategy_setting)
                    except:
                        pass
                    finally:
                        break
                
                if result.iloc[-1]["buy"] == 1:
                    print("buy signal")
                    # strategy = strategy_buy
                    strategy["type"] = "buy"
                elif result.iloc[-1]["sell"] == 1:
                    print("sell signal")
                    # strategy = strategy_sell
                    strategy["type"] = "sell"
                else:
                    print("no buy no sell")
                    continue

                self.send_signal(strategy["user_list"], strategy)
                print("sleeping ....")

            sleep(duration)


args = sys.argv
try:
    command = args[1]
except:
    command = ""

if command == "run":
    manager = Manager()
    _stra_name, _symbol, _time_frame, _broker = args[2], args[3], args[4], args[5]
    manager.run_strategy(_stra_name, _symbol, _time_frame, _broker)
elif command == "file_report":
    manager = Manager()
    __broker, __strategy_name = args[2], args[3]
    d = {"broker": __broker, "strategy_name": __strategy_name}
    # print(manager.report(d))
    manager.report_file({"broker": __broker, "strategy_name": __strategy_name})

