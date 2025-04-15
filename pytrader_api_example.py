"""
    PyTrader api - script example for easy connection with Metatrader5 EA
	This is an example file with all calling functions to metatrader terminal and get it back to your script
    For closing/deleting trades, ticket numbers must be known.
    Also opening orders openprice, sl and tp must be appropriate

"""

import numpy as np
import pandas as pd
import configparser
from datetime import datetime
import pytz
from utils.api.Pytrader_API_V4_01 import Pytrader_API



# instantiation
MT = Pytrader_API()

# There are diffferent ways to connect to the MT connector.

# Option #1: if the EA is on same computer
# you need a list with universal instrument names(you use in the python application) and the broker
# specific instrument names.
# by this you can make your python application broker independent

#   Optional way of building the list
brokerInstrumentsLookup = {
    'EURUSD': 'EURUSD',
    'GBPNZD': 'GBPNZD',
    'GOLD': 'XAUUSD',
    'DAX': 'GER30'}

# Option #2: a different way is by working with a configuration file shown below.
# example is added
# example script for reading the configuration file and building the list

def config_instruments(config, section):
    """
    This function reads in a configuration file and returns a dictionary with the lookup table
    for the instrument names.

    Parameters:
    config (configparser object): The configuration file object
    section (str): The name of the section in the configuration file

    Returns:
    dict: A dictionary with the broker specific instrument names as keys and the universal instrument names as values
    """
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            option = option.upper()
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except BaseException:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


# Read in config
# The file name of the configuration file
CONFIG_FILE = "Instrument.conf"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
brokerInstrumentsLookup = config_instruments(config, "ICMarkets")

# Connection line of code
# (documentation reference 2)
# Connected: boolean
# Establish connection to the MetaTrader terminal
# Connected: boolean indicating connection success

Connected = MT.Connect(
    server='172.26.176.1',  # IP address of the MetaTrader server
    port=1133,  # Port number for the connection
    instrument_lookup=brokerInstrumentsLookup,  # Mapping of broker instruments
    authorization_code='None'
)
print(Connected)  # Output the connection status

# this will give extra information in case of troubles/feedback
MT.debug = True

# setting the debug characteristic of the MT connector to false, default is false
MT.debug = False

# set timeout, time out in seconds for socket communication
# for retrieving long bar history or slow systems you can set an other connection time out
MT.Set_timeout(timeout_in_seconds=120)


# IsAlive - you can always check if the connection is still OK
# IsAlive = boolean
# Output the connection status
IsAlive = MT.connected
print(IsAlive)


# check connection, renew connection check
# KeepAliveCheck = boolean
# there is socket communication
CheckAlive = MT.Check_connection()
print(CheckAlive)

# check connection, only parameter check
# no physical socket connection check
# connection_check = bool
# this parameter is update after every command with EA communication
connection_check = MT.connected
print(connection_check)

# check if MT4/5 terminal has connection with Broker
# broker_connection = bool
broker_connection = MT.Check_terminal_server_connection()
print(broker_connection)

# check terminal type MT4 or MT5
# terminal_type = 'MT4' or 'MT5'
terminal_type = MT.Check_terminal_type()
print(terminal_type)    


# get static account information
# static_account_info = dict
static_account_info = MT.Get_static_account_info()
print(static_account_info)


# get dynamic account information
# dynamic_account_info = dict
dynamic_account_info = MT.Get_dynamic_account_info()
print(dynamic_account_info)

# check license type, demo or licensed
license_type = MT.Check_license()
print(license_type)

# check trading allowed for a specific instrument
trading_allowed = MT.Check_trading_allowed(instrument = "EURUSD")
print(trading_allowed)


# set bar date ascending / descending
# True = row[0] is the oldest bar
# False = row[0] is the latest bar
bar_date_descending = MT.Set_bar_date_asc_desc(asc_desc=True)
print(bar_date_descending)

# get the parameters of an instrument
# instrument_info = dict
instrument_info = MT.Get_instrument_info(instrument = "EURUSD")
print(instrument_info)

# check of instrument is in marketwatch of MT terminal
# marketwatch_check = tuple
marketwatch_check = MT.Check_instrument(instrument = "EURUSD")
print(marketwatch_check)

# get all instruments in MT terminal market watch
# instruments = list
instruments = MT.Get_instruments()
print(instruments)


# get a list of broker instrument names, filtered by brokerInstrumentLookup
# broker_instruments = list
broker_instruments = MT.Get_broker_instrument_names()
print(broker_instruments)

# get broker server time
# ServerTime = datetime
ServerTime = MT.Get_broker_server_time()
print(ServerTime)

# get last instrument tick info
# tick_info = dict
tick_info = MT.Get_last_tick_info(instrument = "EURUSD")
print(tick_info)

# get last x ticks of an instrument
# ticks = np.array , only working for MT5 
ticks = MT.Get_last_x_ticks_from_now(instrument = "EURUSD", nbrofticks = 10)
print(ticks)


# get the actual bar information for given instrument and given timeframe
# bar_info = dict
bar_info = MT.Get_actual_bar_info(instrument = "AUDJPY", timeframe = 5)
print(bar_info)

# get the specific bar information for given instrument(s) and given timeframe
# specific_bars = dict{dict}
# be sure instruments are in market watch and history is available at MT terminal
list = ['EURUSD', 'NZDCHF']
specific_bars = MT.Get_specific_bar(instrument_list = list, specific_bar_index = 3, timeframe = 16408)
print(specific_bars)


# get the last x bars from now for given instrument and given timeframe
# last_bars = np.array()
last_bars = MT.Get_last_x_bars_from_now(instrument = "EURUSD", timeframe = 5, nbrofbars = 30)
print(last_bars)

# get all deleted orders
# deleted orders are pendings never executed
# for MT4 only orders in the terminal history can be retrieved
# deleted_orders = pd.dataframe
deleted_orders = MT.Get_all_deleted_orders()
print(deleted_orders)

# get all deleted orders within time window
# for MT4 only orders in the terminal history can be retrieved
# be aware your local time window can differ from broker time window
# deleted_orders = pd.dataframe
deleted_orders = MT.Get_deleted_orders_within_window()
print(deleted_orders)


# get all pending orders
# pending_orders = pd.dataframe
pending_orders = MT.Get_all_orders()
print(pending_orders)

# get all open positions / market orders
# open_positions = pd.dataframe
open_positions = MT.Get_all_open_positions()
print(open_positions)

# get all closed positions / market orders
# closed_positions = pd.dataframe
closed_positions = MT.Get_all_closed_positions()
print(closed_positions)

# get all closed positions / market orders within window
# again broker time and local time can differ
# closed_positions = pd.dataframe
closed_positions = MT.Get_closed_positions_within_window(date_from = datetime(2025, 2, 20, tzinfo=pytz.timezone("Etc/UTC")), date_to = datetime.now(tz=pytz.timezone("Etc/UTC")))
print(closed_positions)


# open an order, several type of orders are possible
# pending orders and market orders are possible
# naming for MT5 is different from MT4
# MT4 only orders are known
# MT5 we have orders, positions and deals. Deals are only tempory and often not seen.
# MT5 start with order, if accepted(deal) it is a position.
# MT5 pending orders stay pending until they are accepted(deal).


# open a market order.
# ticket= int
# ticket = MT.Open_order(instrument = 'GBPUSD', 
#         ordertype = 'buy', 
#         volume = 0.04, 
#         openprice = 0.0, 
#         slippage = 10, 
#         magicnumber = 0, 
#         stoploss = 0.0, # no stoploss set
#         takeprofit = 0.0, # no takeprofit set
#         comment = '', 
#         market = False)

# if (ticket > 0):
#     print(ticket)
# else:
#     print('Error')
#     print(MT.command_return_error)

# Open a pending order at a given price
# ticket= int
# ticket = MT.Open_order(instrument = 'EURUSD', 
#         ordertype = 'buy_limit', 
#         volume = 0.02, 
#         openprice = 1.10, 
#         slippage = 10, 
#         magicnumber = 200, 
#         stoploss = 0.0, # no stoploss set
#         takeprofit = 0.0, # no takeprofit set
#         comment = '', 
#         market = False)

# if (ticket > 0):
#     print(ticket)
# else:
#     print('Error')
#     print(MT.command_return_error)

# close a position by ticket

# # status = bool
# status = MT.Close_position_by_ticket(ticket = 973136610)
# print(status)

# # Close a position partial
# # status = bool
# status = MT.Close_position_partial_by_ticket(ticket = 973136610, volume_to_close = 0.01)
# print(status)

# # delete order by ticket
# # status = bool
# status = MT.Delete_order_by_ticket(ticket = 973360779)
# print(status)

# set/change stoploss and takeprofit for position
# ChangePosition = boolean
ChangePosition = MT.Set_sl_and_tp_for_position(
    ticket=995859293, stoploss=1.29, takeprofit=1.35)
print(ChangePosition)
if (ChangePosition == False):  # setting sl/tp failed for position
    print(MT.order_error)
    print(MT.order_return_message)

# reset SL and TP for a position
# ResetPosition = boolean
ResetPosition = MT.Reset_sl_and_tp_for_position(ticket=995859293)
print(ResetPosition)
if (ResetPosition == False):  # resetting sl/tp failed for position
    print(MT.order_error)
    print(MT.order_return_message)

# set / change stoploss and takeprofit for order
# ChangeOrder = boolean
ChangeOrder = MT.Set_sl_and_tp_for_order(
    ticket=995859688, stoploss=1.13, takeprofit=1.16)
print(ChangeOrder)
if   (ChangeOrder == False):  # setting sl/tp failed for order
    print(MT.order_error)
    print(MT.order_return_message)

disconnected = MT.Disconnect()
print(disconnected)


