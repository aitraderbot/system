"""
    Mr.Amin 2/24/2022
    This is strategy RSI Strategy_karimi(amber)
    set this strategy as "Amber" in telegram bot
    and check every 15 min in bot

    - Get Data From bitfinex
    - We use last open Candle
    - ETHUSDT
    - !! Pay attention !!  I write Main setting here:

    "Get Data From bitfinex"
    >>from Libraries.data_collector import get_candle_bitfinex as candle

    "Get ADAUSDT 1 hour"
    >>data = candle(symbol='ETHUSDT', timeframe='15m', limit=1000)


    >>analysis_setting={
        'indicators_setting':{'RSI':{'length':4, 'cumlen':5,'Oversold_Level':89 ,'Overbought_Level':12 }}
    }
"""
import pandas_ta as ta
from .Indicator import Indicator as indicator   


class Amber:
    def __init__(self, data):
        self.data = data
        self.setting = {'indicators_setting':{'RSI':{'length':4, 'cumlen':5,'Oversold_Level':89 ,'Overbought_Level':12 }}}
        self.RSI = self.setting['indicators_setting']['RSI']
        self.preprocess()

    def preprocess(self):
        self.data.drop(self.data.tail(1).index, inplace=True)

        self.data['rsi'] = indicator().rsi(self.data['close'], length=self.RSI['length'])

        self.data['cumRSI'] = self.data['rsi'].rolling(self.RSI['cumlen']).sum()

        self.data['ob'] = 100 * self.RSI['cumlen'] * self.RSI['Oversold_Level'] * 0.01
        self.data['os'] = 100 * self.RSI['cumlen'] * self.RSI['Overbought_Level'] * 0.01

        self.data['buy'] = ta.cross(self.data['cumRSI'], self.data['os'], above=True)
        self.data['sell'] = ta.cross(self.data['cumRSI'], self.data['ob'], above=True)

        return self.data

    def logic(self, row):
        # implement your strategy here , you need all rows you need appended to one row in preprocess
        if row['buy']:
            self._set_recommendation(position='buy', risk='low', index=row.name)
        elif row['sell']:
            self._set_recommendation(position='sell', risk='low', index=row.name)
