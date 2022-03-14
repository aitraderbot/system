"""
    Mr.Amin 2/24/2022
    This is strategy amatis Strategy_karimi(amatis) 
    set this strategy as "amatis" in telegram bot  
    and check every 15 min in bot
    
    - Get Data From kucoin
    - ETHUSDT
    - !! Pay attention !!  I write Main setting here:
    
    "Get Data From kucoin" 
    
    "Get ETHUSDT 30m"
    >>data = candle(symbol='ETHUSDT', timeframe='30m', limit=1000)
    
    >>analysis_setting={
        'indicators_setting':{'EMA':{'length':2}}
    }
"""
from .Indicator import Indicator as indicator   


class Amatis:
    
    def __init__(self, data):
        self.setting = {'indicators_setting':{'EMA':{'length':2}}}
        
        self.EMA = self.setting['indicators_setting']['EMA']
        self.data = data
        self.preprocess()


    def preprocess(self):
        self.data.drop(self.data.tail(1).index,inplace=True)
        
        HA_DataFrame= indicator().ha(dataframe=self.data)
        self.data['HA_open']=HA_DataFrame["open"]
        self.data['HA_high']=HA_DataFrame["high"]
        self.data['HA_low'] =HA_DataFrame["low"]
        self.data['HA_close']=HA_DataFrame["close"]
        
        self.data['EMA']=indicator().ema(self.data['HA_close'], self.EMA['length'])
        self.data['HAclose1']=self.data['HA_close'].shift(1)
        self.data['HAopen1']=self.data['HA_open'].shift(1)
        self.data['result']= (self.data['HAopen1']*self.data['HAclose1'])/self.data['EMA']

        self.data['HAlow2']=self.data['HA_low'].shift(2)
        self.data['HAhigh2']=self.data['HA_high'].shift(2)
        
        self.data['buy']= self.data.apply(lambda row: 1 if row['result']<row['HAlow2'] else 0, axis=1)
        self.data['sell']= self.data.apply(lambda row: 1 if row['result']>row['HAhigh2'] else 0, axis=1)
        
        return self.data
                
    def logic(self, row):
        # implement your strategy here , you need all rows you need appended to one row in preprocess
        if row['buy']:
            self._set_recommendation(position='buy', risk='low', index=row.name)
        elif row['sell']:
            self._set_recommendation(position='sell', risk='low', index=row.name)


