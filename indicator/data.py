"""
    Mr Charehei 2022-03-10
    getting data from valid brokers (kucoin, coinex, binance)
    convert data to list of dicts
    valid time frames is ["5min", "4hour", "1hour", "1min", "1day"]
"""
import requests
import pandas as pd


class Data:
    
    columns = ["time", "open_price", "close_price", "high_price", "low_price", "volume", "amount"]
    headers = {
        "Content-Type": "application/json"
    }

    def get(self, broker: str, symbol: str, time_frame: str, limit: int = 100):

        """
            get data by broker
            :param broker = valid broker
            :param symbol = valid symbol for broker
            :param time_frame = time frame for broker
            :param limit = of data for broker
            :return list of data
        """

        if broker == "kucoin":
            data = self.kucoin(symbol, time_frame, limit)
            df = pd.DataFrame(data)            
            return df.to_dict("records")

        elif broker == "coinex":
            data = self.coinex(symbol, time_frame, limit)
            df = pd.DataFrame(data)
            return df.to_dict("records")

        elif broker == "binance":
            data = self.binance(symbol, time_frame, limit)
            df = pd.DataFrame(data)
            return df.to_dict("records")

        else:
            raise Exception("invalid broker")

    def coinex(self, symbol: str, time_frame: str, limit: int = 100):
        url = "https://api.coinex.com/v1/market/kline?market=%s&type=%s&limit=%s" % (symbol, time_frame, limit)
        res = requests.get(url, headers=self.headers).json()
        data = res["data"]
        return pd.DataFrame(data, columns=self.columns).to_dict("records")

    def binance(self, symbol: str, time_frame: str, limit: int = 100):
        return ""

    def kucoin(self, symbol: str, time_frame: str, limit: int = 100):
        url = "https://api.kucoin.com/api/v1/market/candles"

        url += "?symbol=%s&type=%s" % (symbol, time_frame)

        res = requests.get(url, headers=self.headers).json()
        if "data" in res.keys():
            data = res["data"]
            return pd.DataFrame(data, columns=self.columns).to_dict("records")
        else:
            self.kucoin(symbol, time_frame, limit)
