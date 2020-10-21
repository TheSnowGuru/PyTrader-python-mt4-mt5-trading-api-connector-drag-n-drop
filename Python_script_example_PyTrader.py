'''THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND
NON-INFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR ANYONE
DISTRIBUTING THE SOFTWARE BE LIABLE FOR ANY DAMAGES OR OTHER LIABILITY,
WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

# Bitcoin Cash (BCH)   qpz32c4lg7x7lnk9jg6qg7s4uavdce89myax5v5nuk
# Ether (ETH) -        0x843d3DEC2A4705BD4f45F674F641cE2D0022c9FB
# Litecoin (LTC) -     Lfk5y4F7KZa9oRxpazETwjQnHszEPvqPvu
# Bitcoin (BTC) -      34L8qWiQyKr8k4TnHDacfjbaSqQASbBtTd

# contact :- github@jamessawyer.co.uk



"""
    PyTrader api - script example for easy connection with Metatrader4 EA & Metatrader5 EA
	This is an example file with all calling functions to metatrader terminal and get it back to your script
    For closing/deleting trades, ticket numbers must be known.
    Also opening orders openprice, sl and tp must be appropriate

"""


import socket
import numpy as np
import pandas as pd
import configparser
from datetime import datetime
import pytz
from utils.Pytrader_API import Pytrader_API

# Intialization
# documentation reference 1
MT = Pytrader_API()

# There are diffferent ways to connect to the MT connector.


#   Option #1: if the EA is on same computer
#   you need a list with universal instrument names(you use in the python application) and the broker
#   specific instrument names.
#   by this you can make your python application broker independent

#   Optional way of building the list
brokerInstrumentsLookup = {
    'EURUSD': 'EURUSD',
    'GBPNZD': 'GBPNZD',
    'GOLD': 'XAUUSD',
    'DAX': 'GER30'}

#   Option #2: a different way is by working with a configuration file shown below.
#   example is added
#   example script for reading the configuration file and building the list


def config_instruments(config, section):
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
CONFIG_FILE = "Instrument.conf"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

brokerInstrumentsLookup = config_instruments(config, "ICM")
# or
# brokerInstrumentsLookup = config_instruments(config,'FXPIG')

# Connection line of code
# (documentation reference 2)
##  Connected: boolean
Connected = MT.Connect(
    server='127.0.0.1',
    port=11111,
    instrument_lookup=brokerInstrumentsLookup)

# 2, EA is on other computer in same local network
# (documentation reference 2)
##  ok: boolean
#ok = MT.Connect(server='192.168.0.103', port=22222, instrument_lookup=brokerInstrumentsLookup)


# setting the debug characteristic of the MT connector to false, default is false
# this will give extra information in case of troubles/feedback
MT.debug = False

# IsAlive - you can always check if the connection is still OK
##  IsAlive = boolean
IsAlive = MT.connected
print(IsAlive)


# check connection, renew connection check
# (documentation  reference 3)
##  KeepAliveCheck = boolean
KeepAliveCheck = MT.Check_connection()

# Change the time out, for retrieving long bar history or slow systems you can set an other connection time out
# (documentation reference 4)
MT.Set_timeout(timeout_in_seconds=120)

# Retrieve broker server time
# (documentation reference 5)
##  ServerTime = datetime
ServerTime = MT.Get_broker_server_time()

print(ServerTime)
print('')

# Get static account information
# (documentation reference 6)
##  StaticInfo = dictionairy
StaticInfo = MT.Get_static_account_info()
for prop in StaticInfo:
    print("  {}={}".format(prop, result[prop]))
print('')

# Get dynamic account information
# (documentation reference 7)
##  DynamicInfo = dictionairy
DynamicInfo = MT.Get_dynamic_account_info()
for prop in DynamicInfo:
    print("  {}={}".format(prop, result[prop]))
print('')

# Get instrument information
# (documentation reference 8)
# InstrumentInfo = dictionairy, if instrument not known at broker the
# value 'None' will be returned
InstrumentInfo = MT.Get_instrument_info(instrument='EURUSD')
for prop in InstrumentInfo:
    print("  {}={}".format(prop, result[prop]))
print('')


# Get last tick information
# (documentation reference 9)
##  LastTick = dictionary
LastTick = MT.Get_last_tick_info(instrument='GBPNZD')
print('')
for prop in LastTicket:
    print("  {}={}".format(prop, result[prop]))
print('')

# For Live/Paper trading
# The above function can be used for live streaming of data

# Get actual bar information
# (documentation reference 10)
##  ActualBar = dictionary
ActualBar = MT.Get_actual_bar_info(
    instrument='EURUSD',
    timeframe=MT.Get_timeframe_value('H4'))
for prop in ActualBar:
    print("  {}={}".format(prop, result[prop]))
print('')

# For Live/Paper trading
# The above function can be used for live streaming of data


# Get last x ticks from now, working for MT5 Only.
# if MT terminal does not have this in history it may take some time to download
# MT terminal needs first to retrieve from broker
# the max amount of ticks is broker dependent
# socket time out is set to 60 seconds as default, if needed change time out
# (documentation reference 11)
# LastTicks = data frame
LastTicks = MT.Get_last_x_ticks_from_now(instrument='EURUSD', nbrofticks=500)
ticks = pd.DataFrame(LastTickets)
print(ticks.head())
print('')

# Get last x bars from MT terminal
# if MT terminal does not have this in history it may take some time to download
# MT terminal needs first to retrieve from broker
# the max amount of bars is broker dependent
# socket time out is set to 60 seconds
# (documentation reference 12)
# LastBars = data frame
LastBars = MT.Get_last_x_bars_from_now(
    instrument='EURUSD',
    timeframe=MT.Get_timeframe_value('M1'),
    nbrofbars=1000)


# Open a new order (market or pending)
# (documentation reference 13)
# Send a new order, in this case pending order :
# NewOrder = int, order ticket
NewOrder = MT.Open_order(
    instrument='EURUSD',
    ordertype='buy_stop',
    volume=0.01,
    openprice=1.136,
    slippage=10,
    magicnumber=2000,
    stoploss=1.12,
    takeprofit=1.14,
    comment='Test')
if (NewOrder == -1):  # opening order failed
    print(MT.order_error)
    print(MT.order_return_message)

# Send a new order, in this case market order
NewOrder = MT.Open_order(
    instrument='EURUSD',
    ordertype='buy',
    volume=0.01,
    openprice=0.0,
    slippage=10,
    magicnumber=2000,
    stoploss=0.0,
    takeprofit=0.0,
    comment='Test')
if (NewOrder == -1):  # opening order failed
    print(MT.order_error)
    print(MT.order_return)

# set/change stopploss and takeprofit for position
# (documentation reference 14)
##  ChangePosition = boolean
ChangePosition = MT.Set_sl_and_tp_for_position(
    ticket=53136604, stoploss=0.0, takeprofit=1.11001)
if (ChangePosition == False):  # setting sl/tp failed for position
    print(MT.order_error)
    print(MT.order_return_message)

# Set stopploss and takeprofit for order (pendings)
# (documentation reference 15)
##  ChangeOrder = boolean
ChangeOrder = MT.Set_sl_and_tp_for_order(
    ticket=53136804, stoploss=0.0, takeprofit=1.12001)
if (changeOrder == False):  # setting sl/tp failed for order
    print(MT.order_error)
    print(MT.order_return_message)

# Get all orders (pendings)
# (documentation reference 16)
# AllOrders = data frame
AllOrders = MT.Get_all_orders()
print('')
print(allOrders)

# Get all (open) positions
# (documentation reference 17)
# AllPositions = data frame
AllPositions = MT.Get_all_open_positions()
print('')
print(allPositions)

# Get all closed position in a specified time period
# (documentation reference 18)
# AllClosedPositions = data frame
print('')
print('closed positions')
timezone = pytz.timezone("Etc/UTC")
AllClosedPositions = MT.Get_all_closed_positions(
    date_from=datetime(2020, 3, 3, tzinfo=timezone), date_to=datetime.now())
print(AllClosedPositions)

# Close position by ticket
# (documentation reference 19)
##  ClosePosition = boolean
ClosePosition = MT.Close_position_by_ticket(ticket=597318718)

# close position partly
# documentation reference 20
PartialClose = MT.Close_position_partial_by_ticket(
    ticket=367014000, volume_to_close=0.01)
if (PartialClose == False):
    print(MT.order_return_message)

# Delete order by ticket
# (documentation reference 20)
##  DeleteOrder = boolean
DeleteOrder = MT.Delete_order_by_ticket(ticket=49988037)

# result check
if (DeleteOrder == False):
    print(MT.order_error)
    print(MT.order_return_message)
