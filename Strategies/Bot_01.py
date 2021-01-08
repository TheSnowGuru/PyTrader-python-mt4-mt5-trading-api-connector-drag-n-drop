# -*- coding: utf-8 -*-

'''
This script is ment as example how to use the Pytrader_API in live trading.
The logic is a simple crossing of two sma averages.
'''


import time
import pandas as pd
import talib as ta

from utils.Pytrader_API_V1_04 import Pytrader_API

# settings
timeframe = 'M5'
instrument = 'EURUSD'
server_IP = '127.0.0.1'
server_port = 1122
SL_in_pips = 40
TP_in_pips = 25
#SL_in_pips_fake = 250
#TP_in_pips_fake = 150
volume = 0.01
slippage = 5
magicnumber = 1000
multiplier = 10000              # multiplier for calculating SL and TP, for JPY pairs should have the value of 100 
sma_period_1 = 9
sma_period_2 = 34
date_value_last_bar = 0 
number_of_bars = 200                 

#   Create simple lookup table, for the demo api only the following instruments can be traded
brokerInstrumentsLookup = {
    'EURUSD': 'EURUSD',
    'AUDCHF': 'AUDCHF',
    'NZDCHF': 'NZDCHF',
    'GBPNZD': 'GBPNZD',
    'USDCAD': 'USDCAD'}

# Define pytrader API
MT = Pytrader_API()

connection = MT.Connect(server_IP, server_port, brokerInstrumentsLookup)
forever = True
if (connection == True):
    while(forever):

        # retrieve open positions
        positions_df = MT.Get_all_open_positions()
        # if open positions check for closing, if SL and/or TP are defined.
        # using hidden SL/TP
        # first need actual bar info
        actual_bar_info = MT.Get_actual_bar_info(instrument=instrument, timeframe=MT.get_timeframe_value(timeframe))
        if (len(positions_df) > 0):
            for position in positions_df.itertuples():

                if (position.instrument == instrument and position.position_type == 'buy' and TP_in_pips > 0.0 and position.magic_number == magicnumber):
                    tp = position.open_price + TP_in_pips / multiplier
                    if (actual_bar_info['close'] > tp):
                        # close the position
                        MT.Close_position_by_ticket(ticket=position.ticket)
                if (position.instrument == instrument and position.position_type == 'buy' and SL_in_pips > 0.0 and position.magic_number == magicnumber):
                    sl = position.open_price - SL_in_pips / multiplier
                    if (actual_bar_info['close'] < sl):
                        # close the position
                        MT.Close_position_by_ticket(ticket=position.ticket)
                
                if (position.instrument == instrument and position.position_type == 'sell' and TP_in_pips > 0.0 and position.magic_number == magicnumber):
                    tp = position.open_price - TP_in_pips / multiplier
                    if (actual_bar_info['close'] < tp):
                        # close the position
                        MT.Close_position_by_ticket(ticket=position.ticket)
                if (position.instrument == instrument and position.position_type == 'sell' and SL_in_pips > 0.0 and position.magic_number == magicnumber):
                    sl = position.open_price + SL_in_pips / multiplier
                    if (actual_bar_info['close'] > sl):
                        # close the position
                        MT.Close_position_by_ticket(ticket=position.ticket)

        # only if we have a new bar, we want to check the conditions for opening a trade/position
        # at start check will be done immediatly
        if (actual_bar_info['date'] > date_value_last_bar):
            date_value_last_bar = actual_bar_info['date']
            # new bar, so read last x bars
            bars = MT.Get_last_x_bars_from_now(instrument=instrument, timeframe=MT.get_timeframe_value(timeframe), nbrofbars=number_of_bars)
            # convert to dataframe
            df = pd.DataFrame(bars)
            df.rename(columns = {'tick_volume':'volume'}, inplace = True)
            df['date'] = pd.to_datetime(df['date'], unit='s')
            # add the 2x sma's to
            df.insert(0, column='sma_1', value=ta.SMA(df['close'], timeperiod=sma_period_1))
            df.insert(0, column='sma_2', value=ta.SMA(df['close'], timeperiod=sma_period_2))

            # conditions will be checked on bar [1] and [2], bar [0] is actual bar and not yet closed
            index = len(df) - 2
            if (df['sma_1'][index] > df['sma_2'][index] and df['sma_1'][index-1] < df['sma_2'][index-1]):           # buy condition
                
                buy_OK = MT.Open_order(instrument=instrument,
                                        ordertype='buy',
                                        volume = volume,
                                        openprice=0.0,
                                        slippage = slippage,
                                        magicnumber = magicnumber,
                                        stoploss=0.0,
                                        takeprofit=0.0,
                                        comment='strat_1')  

                if (buy_OK > 0):
                    # check if not a sell position is active, if yes close this sell position 
                    for position in positions_df.itertuples():
                        if (position.instrument== instrument and position.position_type== 'sell' and position.magic_number == magicnumber):
                            # close
                            close_OK = MT.Close_position_by_ticket(ticket=position.ticket)  
            
            if (df['sma_1'][index] < df['sma_2'][index] and df['sma_1'][index-1] > df['sma_2'][index-1]):           # sell condition
                
                sell_OK = MT.Open_order(instrument=instrument,
                                        ordertype='sell',
                                        volume = volume,
                                        openprice=0.0,
                                        slippage = slippage,
                                        magicnumber = magicnumber,
                                        stoploss=0.0,
                                        takeprofit=0.0,
                                        comment='strat_1')  

                if (sell_OK > 0):
                    # check if not a buy position is active, if yes close this buy position 
                    for position in positions_df.itertuples():
                        if (position.instrument == instrument and position.position_type == 'buy' and position.magic_number == magicnumber):
                            # close
                            close_OK = MT.Close_position_by_ticket(ticket=position.ticket)

        # wait 2 seconds
        time.sleep(2)

        # check if still connected to MT terminal
        still_connected = MT.Check_connection()
        if (still_connected == False):
            forever = False
            print('Loop stopped')