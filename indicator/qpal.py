"""
    Mr.Amin 2/21/2022
    This is strategy Qpal
    -------------------------------
    set this strategy as Qpal in telegram bot
    and check every 5 min in bot
    - Get Data From bitfinex
    - We use last open Candle
    - ETHUSDT
    - !! Pay attention !!  I write Main setting here:
    "Get Data From bitfinex"
    >>from Libraries.data_collector import get_candle_bitfinex as candle

    "Get ETHUSDT 15 min"
    >>data = candle(symbol='ETHUSDT', timeframe='15m', limit=1000)

    >>analysis_setting={
        'analysis_setting': {'basisType':"DEMA", 'len':3, 'offSig':6, 'offsetALMA':0.85,
        'useRes':True,'strares':24}
    }

"""
import pandas as pd
from .Indicator import Indicator as indicator   
from .data import Data


class Qpal:
    def __init__(self, data):
        
        self.setting = {
            'analysis_setting': {'basisType':"DEMA", 'len':3, 'offSig':6, 'offsetALMA':0.85, 'useRes':True, 'strares':24}
        }
        self.data = data
        self.analysis_setting = self.setting['analysis_setting']
        self.length = self.analysis_setting['len']
        self.offSig = self.analysis_setting['offSig']
        self.offsetALMA = self.analysis_setting['offsetALMA']
        self.useRes = self.analysis_setting['useRes']
        self.basisType = self.analysis_setting['basisType']
        self.strares = self.analysis_setting['strares']
        self.preprocess()

    def preprocess(self):

        def occ(source: pd.Series, volume: pd.Series = None):
            """
            :param volume: for additional condition we need volume too
            :param source: series of close or open , ...
            :return
            """
            result = None

            if self.basisType == "SMA":
                # v1 - Simple Moving Average
                result = indicator().sma(source, self.length)
            elif self.basisType == "EMA":
                # v2 - Exponential Moving Average
                result = indicator().ema(source, self.length)

            elif self.basisType == "DEMA":
                # v3 - Double Exponential
                result = indicator().dema(source, self.length)

            elif self.basisType == "TEMA":
                # v4 - Triple Exponential
                result = indicator().tema(source, self.length)

            elif self.basisType == "WMA":
                # v5 - Weighted
                result = indicator().wma(source, self.length)

            elif self.basisType == "VWMA":
                # v6 - Volume Weighted
                # volume must be second variable
                result = indicator().vwma(source, volume, self.length)

            elif self.basisType == "HullMA":
                # v8 - Hull
                result = indicator().hma(source, self.length)

            elif self.basisType == "TMA":
                # v11 - Triangular (extreme smooth)
                result = indicator().sma(source, self.length)
                 
            return result

        if self.useRes:
            d = Data()
            data = d.get("kucoin", "ETH-USDT", "6hour", limit=1000)
            temp = pd.DataFrame(data)
            temp.drop("amount", axis=1, inplace=True)
            temp.rename(columns={"time": "date", "open_price": "open", "close_price": "close",
                                 "high_price": "high", "low_price": "low"}, inplace=True)

            temp.sort_values("date", inplace=True)
            temp.reset_index(inplace=True)

            temp["open"] = temp["open"].astype(float)
            temp["close"] = temp["close"].astype(float)
            temp["high"] = temp["high"].astype(float)
            temp["low"] = temp["low"].astype(float)
            temp["volume"] = temp["volume"].astype(float)
            

            # temp = candle(symbol='ETHUSDT', timeframe='6h', limit=1000)[1]

            temp.loc[len(temp)] = [0, self.data.tail(1).iloc[-1].date, indicator().wma(self.data["close"], 3).iloc[-1],
                                   indicator().wma(self.data["close"], 3).iloc[-1], indicator().wma(self.data["close"], 3).iloc[-1],
                                   indicator().wma(self.data["close"], 3).iloc[-1], indicator().wma(self.data["close"], 3).iloc[-1]]

            temp['closeSeriesAlt'] = occ(source=temp['close'], volume=temp['volume'])
            temp['openSeriesAlt'] = occ(source=temp['open'], volume=temp['volume'])

            self.data = pd.merge(self.data, temp.loc[:, ["date", "closeSeriesAlt", "openSeriesAlt"]], how="left",on="date")
            print(self.data)
            self.data.ffill(inplace=True)
            self.data.bfill(inplace=True)
        else:
            self.data['closeSeriesAlt'] = occ(source=self.data['close'], volume=self.data['volume'])
            self.data['openSeriesAlt'] = occ(source=self.data['open'], volume=self.data['volume'])

        print(self.data.columns)
        print("------------------------------")
        self.data['buy'] = indicator().cross(self.data['closeSeriesAlt'], self.data['openSeriesAlt'], above=True)
        self.data['sell'] = indicator().cross(self.data['closeSeriesAlt'], self.data['openSeriesAlt'], above=False)
        return self.data

    def logic(self, row):
        # implement your strategy here , you need all rows you need appended to one row in preprocess
        if row['buy']:
            self._set_recommendation(position='buy', risk='low', index=row.name)
        elif row['sell']:
            self._set_recommendation(position='sell', risk='low', index=row.name)
