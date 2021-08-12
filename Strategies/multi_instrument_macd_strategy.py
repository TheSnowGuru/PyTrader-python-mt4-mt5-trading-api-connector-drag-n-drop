'''
This script is ment as example how to use the Pytrader_API in live trading.
The logic is a simple MACD cross.

5 instruments are checked in a loop. It are the 5 free/demo instruments of the pytrader_API
'''



import time
import pandas as pd
from pandas import DataFrame



from utils.Pytrader_API_V1_06a import Pytrader_API
from utils.LogHelper import Logger                              # for logging events


def MACD(
        ohlc: DataFrame,
        period_fast: int = 12,
        period_slow: int = 26,
        signal: int = 9,
        column: str = "close",
        adjust: bool = True,
    ) -> DataFrame:
        
        """
        MACD, MACD Signal and MACD difference.

        """

        EMA_fast = pd.Series(
            ohlc[column].ewm(ignore_na=False, span=period_fast, adjust=adjust).mean(),
            name="EMA_fast",
        )
        EMA_slow = pd.Series(
            ohlc[column].ewm(ignore_na=False, span=period_slow, adjust=adjust).mean(),
            name="EMA_slow",
        )
        MACD = pd.Series(EMA_fast - EMA_slow, name="MACD")
        MACD_signal = pd.Series(
            MACD.ewm(ignore_na=False, span=signal, adjust=adjust).mean(), name="MACD_SIGNAL"
        )

        return pd.concat([MACD, MACD_signal], axis=1)

# logger configuration
log = Logger()
log.configure(logfile='macd_strategy_1.log')

instruments = ['AUDCHF', 'NZDCHF', 'EURUSD',  'GBPNZD', 'USDCAD']

# settings
timeframe = 'M5'

server_IP = '127.0.0.1'
server_port = 1110
SL_in_pips = 10
TP_in_pips = 5
volume = 0.01
slippage = 3
magicnumber = 999
nbr_of_bars = 200

multipliers = {}
multiplier = 10000.0
_multiplier = 10000.0
date_values_last_bar = {}

# set multipliers for the instruments
for _instrument in instruments:
    if _instrument.find('JPY') >= 0:
        multipliers[_instrument] = multiplier / 100.0
        date_values_last_bar[_instrument] = 0
    else:
        multipliers[_instrument] = multiplier
        date_values_last_bar[_instrument] = 0

#   Create simple lookup table, for the demo api only the following instruments can be traded
brokerInstrumentsLookup = {
    'EURUSD': 'EURUSD',
    'AUDCHF': 'AUDCHF',
    'NZDCHF': 'NZDCHF',
    'GBPNZD': 'GBPNZD',
    'USDCAD': 'USDCAD'}

# Define pytrader API
MT = Pytrader_API()

# connect to MT4/5 terminal (EA)
connection = MT.Connect(server_IP, server_port, brokerInstrumentsLookup)

forever = True
if (connection == True):
    log.debug('Strategy started')
    while(forever):

        # retrieve open positions
        positions_df = MT.Get_all_open_positions()

        # loop/iterate for the instruments
        for instrument in instruments:

            _multiplier = multipliers[instrument]

            # if active positions check for closing, if SL and/or TP are defined.
            # using hidden SL/TP
            # first need actual bar info
            actual_bar_info = MT.Get_actual_bar_info(instrument=instrument, timeframe=MT.get_timeframe_value(timeframe))
            # iterate through positions and check for sl or tp
            if (len(positions_df) > 0):
                for position in positions_df.itertuples():
                    if (position.instrument == instrument and position.position_type == 'buy' and TP_in_pips > 0.0 and position.magic_number == magicnumber):
                        tp = position.open_price + TP_in_pips / _multiplier
                        if (actual_bar_info['close'] > tp):
                            # close the position
                            MT.Close_position_by_ticket(ticket=position.ticket)
                            log.debug('trade with ticket ' + str(position.ticket) + ' closed in profit')
                    if (position.instrument == instrument and position.position_type == 'buy' and SL_in_pips > 0.0 and position.magic_number == magicnumber):
                        sl = position.open_price - SL_in_pips / _multiplier
                        if (actual_bar_info['close'] < sl):
                            # close the position
                            MT.Close_position_by_ticket(ticket=position.ticket) 
                            log.debug('trade with ticket ' + str(position.ticket) + ' closed in loss')                   
                    if (position.instrument == instrument and position.position_type == 'sell' and TP_in_pips > 0.0 and position.magic_number == magicnumber):
                        tp = position.open_price - TP_in_pips / _multiplier
                        if (actual_bar_info['close'] < tp):
                            # close the position
                            MT.Close_position_by_ticket(ticket=position.ticket)
                            log.debug('trade with ticket ' + str(position.ticket) + ' closed in profit')
                    if (position.instrument == instrument and position.position_type == 'sell' and SL_in_pips > 0.0 and position.magic_number == magicnumber):
                        sl = position.open_price + SL_in_pips / _multiplier
                        if (actual_bar_info['close'] > sl):
                            # close the position
                            MT.Close_position_by_ticket(ticket=position.ticket)
                            log.debug('trade with ticket ' + str(position.ticket) + ' closed in loss')

            # only if we have a new bar, we want to check the conditions for opening a trade/position
            # at start check will be done immediatly
            # date values are in seconds from 1970 onwards.
            # for comparing 2 dates this is ok

            if (actual_bar_info['date'] > date_values_last_bar[instrument]):
                date_values_last_bar[instrument] = actual_bar_info['date']
                # new bar, so read last x bars
                bars = MT.Get_last_x_bars_from_now(instrument=instrument, timeframe=MT.get_timeframe_value(timeframe), nbrofbars=nbr_of_bars)
                # convert to dataframe
                df = pd.DataFrame(bars)
                df.rename(columns = {'tick_volume':'volume'}, inplace = True)
                df['date'] = pd.to_datetime(df['date'], unit='s')

                macd = MACD(df)

                index = len(macd) - 2
                if (macd['MACD'][index] > macd['MACD_SIGNAL'][index] and macd['MACD'][index-1] < macd['MACD_SIGNAL'][index-1]):           # buy condition
                    buy_OK = MT.Open_order(instrument=instrument,
                                        ordertype='buy',
                                        volume = volume,
                                        openprice=0.0,
                                        slippage = slippage,
                                        magicnumber = magicnumber,
                                        stoploss=0.0,
                                        takeprofit=0.0,
                                        comment='macd strategy_1') 
                    if (buy_OK > 0):
                        log.debug('Buy trade opened')
                        # check if not a sell position is active, if yes close this sell position 
                        for position in positions_df.itertuples():
                            if (position.instrument== instrument and position.position_type== 'sell' and position.magic_number == magicnumber):
                                # close
                                close_OK = MT.Close_position_by_ticket(ticket=position.ticket) 
                                log.debug('closed sell trade due to cross and opening buy trade') 
        
                if (macd['MACD'][index] < macd['MACD_SIGNAL'][index] and macd['MACD'][index-1] > macd['MACD_SIGNAL'][index-1]):           # sell condition
                
                    sell_OK = MT.Open_order(instrument=instrument,
                                            ordertype='sell',
                                            volume = volume,
                                            openprice=0.0,
                                            slippage = slippage,
                                            magicnumber = magicnumber,
                                            stoploss=0.0,
                                            takeprofit=0.0,
                                            comment='macd strategy_1')  

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