import pandas as pd
import pandas_ta as ta

class Indicator:

    def sma(self, close: pd.Series, length: int):
        '''
        Indicator: Simple Moving Average (SMA)
        :param close: a list of data
        :param length: an integer value
        :return a list 
        '''
        sma = ta.sma(close, length)
        return sma 

    def ema(self, close: pd.Series, length: int):
        '''
        Indicator: Exponential Moving Average (EMA)
        :param close: a list of data
        :param length: an integer value
        :return a list 
        '''
        ema = ta.ema(close, length)
        return ema

    def dema(self, close: pd.Series, length: int):
        '''
        Indicator: Double Exponential Moving Average (DEMA)
        :param close: a list of data
        :param length: an integer value
        :return a list 
        '''
        dema = ta.dema(close, length)
        return dema

    def tema(self, close: pd.Series, length: int):
        '''
        Indicator: Triple Exponential Moving Average (TEMA)
        :param close: a list of data
        :param length: an integer Value
        :return a list 
        '''
        tema = ta.tema(close, length)
        return tema
    
    def wma(self, close: pd.Series, length: int):
        '''
        Indicator: Weighted Moving Average (WMA)
        :param close: a list of data
        :param length: an integer Value
        :return a list 
        '''
        wma = ta.wma(close, length)
        return wma

    def vwma(self, close: pd.Series, volume: pd.Series, length: int):
        '''
        Indicator: Volume Weighted Moving Average (VWMA)
        :param close: a list of data
        :param volume : a list of data
        :param length: an integer Value
        :return a list 
        '''
        wma = ta.vwma(close, volume, length)
        return wma   

    def hma(self, close: pd.Series, length: int):
        '''
        Indicator: Hull Moving Average (HMA)
        :param close: a list of data
        :param length: an integer Value
        :return a list of data
        '''
        hma = ta.hma(close, length)
        return hma 

    def tma(self, close: pd.Series, length: int):
        '''
        Indicator: Triangular (extreme smooth) (TMA)
        :param close: a list of data
        :param length: an integer Value
        :return a list of data
        '''
        sma = ta.sma(close, length)
        tma = ta.sma(sma, length)
        return tma 

    def ha(self, dataframe: pd.DataFrame):
        '''
        calculate Heikin Ashi Candle Type
        :param dataframe: open high low close Dataframe
        :return a dict Heikin Ashi 
            first  open  Heikin Ashi list
            second high  Heikin Ashi list
            third  low   Heikin Ashi list
            forth  close Heikin Ashi list
        '''
        HA_DataFrame=ta.ha(open_=dataframe["open"], high=dataframe["high"],\
                            low=dataframe["low"], close=dataframe["close"])

        # return HA_DataFrame.to_dict("records")

        return {'open': HA_DataFrame["HA_open"].values, 'high': HA_DataFrame["HA_high"].values ,\
                'low': HA_DataFrame["HA_low"].values, 'close': HA_DataFrame["HA_close"].values} 

    def stdev(self, close: pd.Series, length: int):
        '''
        calculate StandardDeviation 
        :param close: a list of data
        :param length: an integer Value
        :return a list of data
        '''
        StandardDeviation=ta.stdev(close, length=length, talib=False)
        return StandardDeviation

    def rsi(self, close: pd.Series, length: int):
        '''
        Indicator: Relative Strength Index (RSI)
        :param close: a list of data
        :param length: an integer Value
        :return a list of data
        '''
        rsi = ta.rsi(close, length=length)
        return rsi

    def cross(self,series_a: pd.Series, series_b: pd.Series, above: bool = True):
        '''
        Check cross two list
        :param series_a: a list of data
        :param series_b: a list of data
        :param above: a boolian Value
        :return a list of data
        '''
        result = ta.cross(series_a, series_b, above=above)
        return result