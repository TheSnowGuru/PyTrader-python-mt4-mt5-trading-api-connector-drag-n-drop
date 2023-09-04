#strategy based on Trading geek channel ONE Strategy (FULL BREAKDOWN)
# -*- coding: utf-8 -*-
import time
import pandas as pd
from utils.Pytrader_API_V1_06a import Pytrader_API
from utils.LogHelper import Logger

# Function to calculate EMA
def calculate_ema(series: pd.Series, n: int) -> pd.Series:
    return series.ewm(span=n).mean()

log = Logger()
log.configure()

# settings
timeframe = 'M5'
instrument = 'EURUSD'
server_IP = '127.0.0.1'
server_port = 1110
SL_in_pips = 20
TP_in_pips = 10
volume = 0.01
slippage = 5
magicnumber = 1000
multiplier = 10000
if instrument.find('JPY') >= 0:
    multiplier = 100.0
date_value_last_bar = 0 
number_of_bars = 100

brokerInstrumentsLookup = {
    'EURUSD': 'EURUSD',
    'AUDCHF': 'AUDCHF',
    'NZDCHF': 'NZDCHF',
    'GBPNZD': 'GBPNZD',
    'USDCAD': 'USDCAD'
}

MT = Pytrader_API()

connection = MT.Connect(server_IP, server_port, brokerInstrumentsLookup)
forever = True

if connection:
    log.debug('Strategy started')
    while forever:
        positions_df = MT.Get_all_open_positions()
        actual_bar_info = MT.Get_actual_bar_info(instrument=instrument, timeframe=MT.get_timeframe_value(timeframe))
        
        # ... existing logic for managing open positions ...

        if actual_bar_info['date'] > date_value_last_bar:
            date_value_last_bar = actual_bar_info['date']
            bars = MT.Get_last_x_bars_from_now(instrument=instrument, timeframe=MT.get_timeframe_value(timeframe), nbrofbars=number_of_bars)
            df = pd.DataFrame(bars)
            df.rename(columns = {'tick_volume':'volume'}, inplace = True)
            df['date'] = pd.to_datetime(df['date'], unit='s')

            df['8EMA'] = calculate_ema(df['close'], 8)
            df['14EMA'] = calculate_ema(df['close'], 14)

            df['Trend'] = df['8EMA'] > df['14EMA']
            resistance_level = 1.2000

            trade_entry_conditions = {
                'Trend': True,
                'Price': df['close'].iloc[-1] > resistance_level,
                'Candlestick': df['close'].iloc[-1] > df['open'].iloc[-1],
                'MovingAverageCrossover': df['8EMA'].iloc[-1] > df['14EMA'].iloc[-1]
            }

            if all(trade_entry_conditions.values()):
                buy_OK = MT.Open_order(
                    instrument=instrument,
                    ordertype='buy',
                    volume=volume,
                    openprice=0.0,
                    slippage=slippage,
                    magicnumber=magicnumber,
                    stoploss=0.0,
                    takeprofit=0.0,
                    comment='strategy_1'
                )

                if buy_OK > 0:
                    log.debug('Buy trade opened based on new strategy')
                    
            # ... existing logic for sell condition ...

        time.sleep(2)

        still_connected = MT.Check_connection()
        if not still_connected:
            forever = False
            print('Loop stopped')
            log.debug('Loop stopped')
