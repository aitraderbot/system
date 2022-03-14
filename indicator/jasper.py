"""
    Mr.Amin 03/10/2022
    This is strategy Jasper (Mr Hoveyda)
    -------------------------------
    set this strategy as Jasper in telegram bot
    and check every 1 hour in bot

    - Get Data From kucoin
    - MATIC
    - !! Pay attention !!  I write Main setting here:

    "Get Data From kucoin"

    "Get MATIC-USDT 1 hour"


    >>analysis_setting={
        'analysis_setting': {'len':3}
    }

"""
from .Indicator import Indicator as indicator   

class Jasper:
    def __init__(self, data):
        
        self.data = data
        self.setting = {'analysis_setting': {'len': 3}}

        self.analysis_setting = self.setting['analysis_setting']
        self.length = self.analysis_setting['len']

        self.preprocess()

    def preprocess(self):
        self.data.drop(self.data.tail(1).index, inplace=True)

        HA_DataFrame = indicator().ha(dataframe=self.data)

        self.data['HA_open']=HA_DataFrame["open"]
        self.data['HA_high']=HA_DataFrame["high"]
        self.data['HA_low'] =HA_DataFrame["low"]
        self.data['HA_close']=HA_DataFrame["close"]
        
        self.data['hlc3']=(self.data['HA_close']+self.data['HA_low']+self.data['HA_high'])/3

        self.data['highestHighs'] = self.data['hlc3'].rolling(self.length).max()
        self.data['lowestLows'] = self.data['hlc3'].rolling(self.length).min()

        self.data['DiffClose_Hh'] = self.data['HA_close'] - self.data['highestHighs']
        self.data['DiffClose_Ll'] = self.data['HA_close'] - self.data['lowestLows']

        self.data['X6'] = -1 * self.data['DiffClose_Hh']
        self.data['X5'] = self.data['DiffClose_Ll'] - self.data['X6']

        self.data['emaX5'] = indicator().ema(self.data['X5'], self.length)
        self.data['x7'] = 2 * self.data['emaX5'] - indicator().ema(self.data['emaX5'], self.length)

        self.data['buy'] = self.data['x7'].apply(lambda x: 1 if x > 0 else 0)
        self.data['sell'] = self.data['x7'].apply(lambda x: 1 if x <= 0 else 0)

        # self.data["close"] = self.data['HA_close']
        return self.data

    def logic(self, row):
        # implement your strategy here , you need all rows you need appended to one row in preprocess
        if row['buy']:
            self._set_recommendation(position='buy', risk='low', index=row.name)
        elif row['sell']:
            self._set_recommendation(position='sell', risk='low', index=row.name)

