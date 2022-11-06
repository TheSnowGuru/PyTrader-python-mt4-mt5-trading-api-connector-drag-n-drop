# -*- coding: utf-8 -*-

'''
This script is a starter script of how to use the Pytrader_API in live trading.
The strategy is NFP scalper on EURUSD according to historical data.

NFP release. Strategy will be taking trades on EURUSD on the following criteria,

e.g  (est 200k).
if nfp >215k, go short
if nfp <185k, go long

Backtests show that the trade length should be in and out in just 10s. Aiming for a 2s past the release execution time.

backtest needed.
'''


import time
import pandas as pd
import talib as ta

from utils.Pytrader_API_V1_06a import Pytrader_API
from utils.LogHelper import Logger                              # for logging events


log = Logger()
log.configure()

# settings
timeframe = 'M1'
instrument = 'EURUSD'
server_IP = '127.0.0.1'
server_port = 1110                                              # check port number
SL_in_pips = 20
TP_in_pips = 10

volume = 0.01
slippage = 5
magicnumber = 1000
multiplier = 10000                                              # multiplier for calculating SL and TP, for JPY pairs should have the value of 100
if instrument.find('JPY') >= 0:
    multiplier = 100.0  
sma_period_1 = 9
sma_period_2 = 16
date_value_last_bar = 0 
number_of_bars = 100                 

#   Create simple lookup table, for the demo api only the following instruments can be traded
brokerInstrumentsLookup = {'EURUSD'}

# Define pytrader API
MT = Pytrader_API()

connection = MT.Connect(server_IP, server_port, brokerInstrumentsLookup)
forever = True
if (connection == True):
    log.debug('Strategy started')
    while(forever):

        
        
        
        # retrieve open positions
        positions_df = MT.Get_all_open_positions()
        # if open positions, check for closing, if SL and/or TP are defined.
        # using hidden SL/TP
        # first need actual bar info
        actual_bar_info = MT.Get_actual_bar_info(instrument=instrument, timeframe=MT.get_timeframe_value(timeframe))
        if (len(positions_df) > 0):
            for position in positions_df.itertuples():
              
        # only if we have a new bar, we want to check the conditions for opening a trade/position
        # at start check will be done immediatl
        # for comparing 2 dates this is ok

        if (actual_bar_info['date'] > date_value_last_bar):
            date_value_last_bar = actual_bar_info['date']
           
            # new bar, so read last x bars
            bars = MT.Get_last_x_bars_from_now(instrument=instrument, timeframe=MT.get_timeframe_value(timeframe), nbrofbars=number_of_bars)
            
            # convert to dataframe
            df = pd.DataFrame(bars)
            df.rename(columns = {'tick_volume':'volume'}, inplace = True)
            df['date'] = pd.to_datetime(df['date'], unit='s')
            
            
            

            
            # conditions nfp result vs forecast
            if (nfp actual vs est ) :           # buy condition
                
                buy_OK = MT.Open_order(instrument=instrument,
                                        ordertype='buy',
                                        volume = volume,
                                        openprice=0.0,
                                        slippage = slippage,
                                        magicnumber = magicnumber,
                                        stoploss=0.0,
                                        takeprofit=0.0,
                                        comment='strategy_1')  

                if (buy_OK > 0):
                    log.debug('Buy trade opened')
                    # check if not a sell position is active, if yes close this sell position 
                    for position in positions_df.itertuples():
                        if (position.instrument== instrument and position.position_type== 'sell' and position.magic_number == magicnumber):
                            # close
                            close_OK = MT.Close_position_by_ticket(ticket=position.ticket) 
                            log.debug('closed sell trade due to cross and opening buy trade') 
            
            if (nfp actual vs est ):           # sell condition
                
                sell_OK = MT.Open_order(instrument=instrument,
                                        ordertype='sell',
                                        volume = volume,
                                        openprice=0.0,
                                        slippage = slippage,
                                        magicnumber = magicnumber,
                                        stoploss=0.0,
                                        takeprofit=0.0,
                                        comment='strategy_1')  

                if (sell_OK > 0):
                    log.debug('Sell trade opened')
                    # check if not a buy position is active, if yes close this buy position 
                    for position in positions_df.itertuples():
                        if (position.instrument == instrument and position.position_type == 'buy' and position.magic_number == magicnumber):
                            # close
                            close_OK = MT.Close_position_by_ticket(ticket=position.ticket)
                            log.debug('closed buy trade due to cross and opening sell trade')

        # wait 2 seconds
        time.sleep(2)

        # check if still connected to MT terminal
        still_connected = MT.Check_connection()
        if (still_connected == False):
            forever = False
            print('Loop stopped')
            log.debug('Loop stopped')
