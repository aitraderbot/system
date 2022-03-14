"""
    Mr.Amin 2/21/2022
    This is strategy occ + Heikin Ashi + Stdev
    replace this strategy as Opal in telegram bot  
    and check every 15 min in bot
    
    - Get Data From bitfinex
    - We use last open Candle
    - ADAUSDT
    - !! Pay attention !!  I write Main setting here:
    
    "Get Data From bitfinex" 
    >>from Libraries.data_collector import get_candle_bitfinex as candle
    
    "Get ADAUSDT 1 hour"
    >>data = candle(symbol='ADAUSDT', timeframe='1h', limit=1000)
    
    
    >>analysis_setting={
        'analysis_setting': {'basisType':"DEMA", 'len':5, 'offSig':6, 'offsetALMA':0.85},
        'indicators_setting':{'Stdev':{'length':14, 'condition':0.0041 }}
    }
"""

import pandas as pd
from .Indicator import Indicator as indicator


class Opal:
    def __init__(self, data):
        # Strategy.__init__(self, data=data, coin_id=coin_id, analysis_id=analysis_id,
        #   timeframe_id=timeframe_id, bot_ins=bot_ins)

        self.data = data
        self.setting = {
                'analysis_setting': {'basisType': "DEMA", 'len': 5, 'offSig': 6, 'offsetALMA': 0.85},
                'indicators_setting': {'Stdev': {'length': 14, 'condition': 0.0041}}
        }
        self.analysis_setting = self.setting['analysis_setting']
        self.length = self.analysis_setting['len']
        self.offSig = self.analysis_setting['offSig']
        self.offsetALMA = self.analysis_setting['offsetALMA']
        self.basisType = self.analysis_setting['basisType']
        self.stdev = self.setting['indicators_setting']['Stdev']
        # self.preprocess()

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

        # convert Heikin Ashi

        HA_DataFrame = indicator().ha(dataframe=self.data)

        self.data['HA_open'] = HA_DataFrame["open"]
        self.data['HA_high'] = HA_DataFrame["high"]
        self.data['HA_low'] = HA_DataFrame["low"]
        self.data['HA_close'] = HA_DataFrame["close"]

        self.data['closeSeriesAlt'] = occ(source=self.data['close'], volume=self.data['volume'])
        self.data['openSeriesAlt'] = occ(source=self.data['open'], volume=self.data['volume'])

        self.data['std_close'] = indicator().stdev(self.data['close'], length=self.stdev['length'])
        self.data['std_close'] = self.data['std_close'].fillna(value=0)

        self.data['std_close'] = self.data['std_close'].apply(lambda x: 1 if x > self.stdev['condition'] else 0)

        self.data['diff'] = self.data['closeSeriesAlt'] - self.data['openSeriesAlt']
        self.data['crossover'] = self.data['diff'].apply(lambda x: 1 if x > 0 else 0)
        self.data['crossunder'] = self.data['diff'].apply(lambda x: 1 if x < 0 else 0)

        self.data['buy'] = self.data['crossover'] * self.data['std_close']
        self.data['sell'] = self.data['crossunder'] * self.data['std_close']

        return self.data
        # print(self.data.loc[:,['date','crossover','crossunder']].tail(50))
        # self.data["open"] = self.data['HA_open']
        # self.data["high"] = self.data['HA_high']
        # self.data["low"] = self.data['HA_low']
        # self.data["close"] = self.data['HA_close']

    # def logic(self, row):
    #     # implement your strategy here , you need all rows you need appended to one row in preprocess
    #     if row['buy']:
    #         self._set_recommendation(position='buy', risk='low', index=row.name)
    #     elif row['sell']:
    #         self._set_recommendation(position='sell', risk='low', index=row.name)

#######################

# "Get Data From bitfinex" 
# from Libraries.data_collector import get_candle_bitfinex as candle

# "Get ADAUSDT  1 hour"
# data = candle(symbol='ADAUSDT', timeframe='1h', limit=1000)

# "settings"
# analysis_setting={
#     'analysis_setting': {'basisType':"DEMA", 'len':5, 'offSig':6, 'offsetALMA':0.85},
#     'indicators_setting':{'Stdev':{'length':14, 'condition':0.0041 }}
# }
