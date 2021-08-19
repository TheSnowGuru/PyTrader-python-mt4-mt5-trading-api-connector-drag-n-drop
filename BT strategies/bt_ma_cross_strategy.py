import pandas as pd
import time
from utils.Pytrader_BT_API_V1_01 import Pytrader_BT_API
from utils.Pytrader_API_V1_06a import Pytrader_API
from utils.LogHelper import Logger

# for not using talib
def calculate_simple_moving_average(series: pd.Series, n: int=20) -> pd.Series:
    """Calculates the simple moving average"""
    return series.rolling(n).mean()

# add a logger for keeping track of what happens
log = Logger()
log.configure(logfile='bt_ma_cross_strategy.log')

# instruments to be used, if more then 1 instrument the instruments have to be synchronised.
# this means data filoes need to have same amount of bars and the dates have to be exactly same.
# otherwise the calculated bars will run out of order/time
_instrument_list = ['EURUSD']

# definition of the timeframes that we be used
# limit to what is for your stategy, no need to take care of timeframes not used.
# this will spoil capacity
timeframe_list = ['M1', 'M15', 'H1']

# broker instrument lookup list, just for compatibility
brokerInstrumentsLookup = {
    'EURUSD': 'EURUSD',
    'GBPNZD': 'GBPNZD',
    'GOLD': 'XAUUSD',
    'DAX': 'GER30'}

# instantiaton
MT_Back = Pytrader_BT_API()

# instatiation
MT = Pytrader_API()

# connect to the back tester
BT_connected = MT_Back.Connect(
    server='127.0.0.1',
    port=10014,
    instrument_lookup=brokerInstrumentsLookup)

if (BT_connected):
    log.debug('Connected to back tester.')
else:
    log.debug('Connecting to back tester failed')
    # In principle stop the script

# check for license, EURUSD is also in demo. So no problem
license = MT_Back.Check_license(server = '127.0.0.1', port = 5555)
if (license == True):
    log.debug('Backtester runs in license.')
else:
    log.debug('Backtester runs in demo.')


# reset of backtester, at start not needed, just to show for how to use
ok = MT_Back.Reset_backtester()
if (ok == False):
    log.debug('Error in resetting the back tester')
    log.debug(MT_Back.command_return_error)

# set the comma or dot annotation.
# depending on your country / region reals are written with a dot or a comma
ok = MT_Back.Set_comma_or_dot(mode='comma')

# the back tester has no account at start, so we have to set a value
# margin call is not used at the moment
ok = MT_Back.Set_account_parameters(balance = 1000.0, max_pendings = 50, margin_call= 50.0)

# set the directory of the M1 data files, In this directory the back trader will look for the M1 data files
ok = MT_Back.Set_data_directory(data_directory='C:\\Temp\\Bar_files')
if (ok == False):
    log.debug('Error in setting data directory')
    log.debug(MT_Back.command_return_error)

# set the instruments to trade, this will take a while depending on the number of instruments and the size of the datafiles
# Only if M1 datafiles are synchronized more the one instrument should be defined
ok = MT_Back.Set_instrument_list(instrument_list=_instrument_list)
if (ok == False):
    log.debug('Error in setting instruments and/or reading the datafiles')
    log.debug(MT_Back.command_return_error)


# at start there will be no history for bars witha period > M1.
# depending 0n your stategy the back tester has to move formwars x M1 bars to build all the needed bars for the used time frames
ok = MT_Back.Set_index_for_start(15000)

# set instrument parameters like max lotsize, min lotsize, ............(needed for trading)
# for getting these parameters make connection with MT4/5 terminal and get then from there.
# you can of course also define them yourselve

# first we  connect to a MT4/5 terminal
Connected = MT.Connect(
    server='127.0.0.1',
    port=1122,
    instrument_lookup=brokerInstrumentsLookup)

# retrieve the instrument info and set in the back tester
for _instrument in _instrument_list:
    _info = MT.Get_instrument_info(instrument = _instrument)
    print (_info)
    ok = MT_Back.Set_instrument_parameters(instrument=_info['instrument'], digits=_info['digits'], \
                                    max_lotsize=_info['max_lotsize'], min_lotsize=_info['min_lotsize'], \
                                    lot_stepsize=_info['lot_step'], point=_info['point'], tick_size=_info['tick_size'], tick_value=_info['tick_value'], \
                                    swap_long=_info['swap_long'], swap_short=_info['swap_short'] )
MT.Disconnect()

# set the time frames
ok = MT_Back.Set_timeframes(timeframe_list=timeframe_list)

# set spread and commission
ok = MT_Back.Set_spread_and_commission_in_pips(instrument='EURUSD', low_spread_in_pips=0.4, high_spread_in_pips=1.2, commission_in_pips=0.4)

# if we want to know how many M1 bars the backtester has in history and the dates of the first and last bar
# we can call this function
BT_info = MT_Back.Get_datafactory_info(instrument='EURUSD')
print(BT_info)

# settings for strategy
timeframe = 'M15'
instrument = 'EURUSD'
SL_in_pips = 20
TP_in_pips = 10

volume = 0.01
slippage = 5
magicnumber = 1000
multiplier = 10000                                              # multiplier for calculating SL and TP, for JPY pairs should have the value of 100, 5 digits broker
if instrument.find('JPY') >= 0:
    multiplier = 100.0  
sma_period_1 = 9
sma_period_2 = 16
date_value_last_bar = 0 
number_of_bars = 100 


# we let the strategy run for 10000 increments
increments_stop = 10000
increment_counter = 0
increments_step = 1

forever = True
if (BT_connected == True):
    log.debug('Strategy started')
    while(forever):

        # increment 1 M1 bar
        MT_Back.Go_x_increments_forwards(increments_step)
        increment_counter = increment_counter + 1
        # retrieve open positions
        positions_df = MT_Back.Get_all_open_positions()
        # if open positions, check for closing, if SL and/or TP are defined.
        # first need actual bar info
        actual_bar_info = MT_Back.Get_actual_bar_info(instrument=instrument, timeframe=MT_Back.get_timeframe_value(timeframe))
        if (len(positions_df) > 0):
            for position in positions_df.itertuples():

                if (position.instrument == instrument and position.position_type == 'buy' and TP_in_pips > 0.0 and position.magic_number == magicnumber):
                    tp = position.open_price + TP_in_pips / multiplier
                    if (actual_bar_info['close'] > tp):
                        # close the position
                        MT_Back.Close_position_by_ticket(ticket=position.ticket)
                        log.debug('trade with ticket ' + str(position.ticket) + ' closed in profit')
                        
                elif (position.instrument == instrument and position.position_type == 'buy' and SL_in_pips > 0.0 and position.magic_number == magicnumber):
                    sl = position.open_price - SL_in_pips / multiplier
                    if (actual_bar_info['close'] < sl):
                        # close the position
                        MT_Back.Close_position_by_ticket(ticket=position.ticket)
                        log.debug('trade with ticket ' + str(position.ticket) + ' closed in loss')
                
                elif (position.instrument == instrument and position.position_type == 'sell' and TP_in_pips > 0.0 and position.magic_number == magicnumber):
                    tp = position.open_price - TP_in_pips / multiplier
                    if (actual_bar_info['close'] < tp):
                        # close the position
                        MT_Back.Close_position_by_ticket(ticket=position.ticket)
                        log.debug('trade with ticket ' + str(position.ticket) + ' closed in profit')
                elif (position.instrument == instrument and position.position_type == 'sell' and SL_in_pips > 0.0 and position.magic_number == magicnumber):
                    sl = position.open_price + SL_in_pips / multiplier
                    if (actual_bar_info['close'] > sl):
                        # close the position
                        MT_Back.Close_position_by_ticket(ticket=position.ticket)
                        log.debug('trade with ticket ' + str(position.ticket) + ' closed in loss')

        # only if we have a new bar, we want to check the conditions for opening a trade/position
        # at start check will be done immediatly
        # date values are in seconds from 1970 onwards.
        # for comparing 2 dates this is ok

        if (actual_bar_info['date'] > date_value_last_bar):
            date_value_last_bar = actual_bar_info['date']
            # new bar, so read last x bars
            bars = MT_Back.Get_last_x_bars_from_now(instrument=instrument, timeframe=MT.get_timeframe_value(timeframe), nbrofbars=number_of_bars)
            # convert to dataframe
            df = pd.DataFrame(bars)
            df.rename(columns = {'tick_volume':'volume'}, inplace = True)
            df['date'] = pd.to_datetime(df['date'], unit='s')
            # add the 2x sma's to
            # using talib here or not
            #df.insert(0, column='sma_1', value=ta.SMA(df['close'], timeperiod=sma_period_1))
            #df.insert(0, column='sma_2', value=ta.SMA(df['close'], timeperiod=sma_period_2))
            df.insert(0, column='sma_1', value=calculate_simple_moving_average(df['close'], n = sma_period_1))
            df.insert(0, column='sma_2', value=calculate_simple_moving_average(df['close'], n = sma_period_2))

            index = len(df) - 2
            # conditions will be checked on bar [index] and [index-1]
            if (df['sma_1'][index] > df['sma_2'][index] and df['sma_1'][index-1] < df['sma_2'][index-1]):           # buy condition
                
                buy_OK = MT_Back.Open_order(instrument=instrument,
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
                            close_OK = MT_Back.Close_position_by_ticket(ticket=position.ticket) 
                            log.debug('closed sell trade due to cross and opening buy trade') 
            
            if (df['sma_1'][index] < df['sma_2'][index] and df['sma_1'][index-1] > df['sma_2'][index-1]):           # sell condition
                
                sell_OK = MT_Back.Open_order(instrument=instrument,
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
                            close_OK = MT_Back.Close_position_by_ticket(ticket=position.ticket)
                            log.debug('closed buy trade due to cross and opening sell trade')

        # wait 2 seconds
        #time.sleep(2)


        if (increment_counter > increments_stop):
            forever = False
            log.debug('Strategy stopped end of run')
            
            # check for closed positions
            closed_positions = MT_Back.Get_all_closed_positions()
            closed_positions['open_time'] = pd.to_datetime(closed_positions['open_time'], unit='s')
            closed_positions['close_time'] = pd.to_datetime(closed_positions['close_time'], unit='s')
            print(closed_positions)


        # check if still connected to MT terminal
        still_connected = MT_Back.Check_connection()
        if (still_connected == False):
            forever = False
            print('Loop stopped')
            log.debug('Strategy stopped due to error in connection')
            # check for closed positions
            closed_positions = MT_Back.Get_all_closed_positions()
            closed_positions['open_time'] = pd.to_datetime(closed_positions['open_time'], unit='s')
            closed_positions['close_time'] = pd.to_datetime(closed_positions['close_time'], unit='s')
            print(closed_positions)
