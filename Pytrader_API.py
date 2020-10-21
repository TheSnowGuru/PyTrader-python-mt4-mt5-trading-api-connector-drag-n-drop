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



import socket
import numpy as np
from collections import namedtuple
import pandas as pd
import configparser
import MetaTrader5 as mt5
import math
from datetime import datetime


class Pytrader_API:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_error: int = 0
        self.socket_error_message: str = ''
        self.order_return_message: str = ''
        self.order_error: int = 0
        self.connected: bool = False
        self.timeout: bool = False
        self.command_OK: bool = False
        self.command_return_error: str = ''
        self.debug: bool = False
        self.version: str = '1.02'
        self.max_bars: int = 5000
        self.max_ticks: int = 5000
        self.timeout_value: int = 60
        self.instrument_conversion_list: dict = {}
        self.instrument_name_broker: str = ''
        self.instrument_name_universal: str = ''
        self.sock.setblocking(1)
        self.date_from: datetime = '2000/01/01, 00:00:00'
        self.date_to: datetime = datetime.now()

    def Set_timeout(self,
                    timeout_in_seconds: int = 60
                    ):
        self.timeout_value = timeout_in_seconds
        self.sock.settimeout(self.timeout_value)
        self.sock.setblocking(1)
        return

    def __del__(self):
        self.sock.close()

    def Disconnect(self):
        self.sock.close()
        return True

    def Connect(self,
                server: str = '',
                port: int = 2345,
                instrument_lookup: dict = []):
        self.port = port
        self.server = server
        self.instrument_conversion_list = instrument_lookup

        if (len(self.instrument_conversion_list) == 0):
            print('Broker Instrument list not available or empty')
            self.socket_error_message = 'Broker Instrument list not available'
            return False

        try:
            self.sock.connect((self.server, self.port))
            try:
                data_received = self.sock.recv(1000000)
                self.connected = True
                self.socket_error = 0
                self.socket_error_message = ''
                return True
            except socket.error as msg:
                self.socket_error = 100
                self.socket_error_message = 'Could not connect to server.'
                self.connected = False
                return False
        except socket.error as msg:
            print(
                "Couldnt connect with the socket-server: %self.sock\n terminating program" %
                msg)
            self.connected = False
            self.socket_error = 101
            self.socket_error_message = 'Could not connect to server.'
            return False

    def Check_connection(self):
        self.command = 'F000#0#'
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        if (ok == False):
            self.command_OK = False
            return False

        x = dataString.split('#')

        if x[1] == 'OK':
            self.timeout = True
            self.command_OK = True
            return True
        else:
            self.timeout = False
            self.command_OK = True
            return False

    def Get_static_account_info(self):
        self.command_return_error = ''
        ok, dataString = self.send_command('F001#0#')
        if (ok == False):
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F001':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        returnDict = {}
        del x[0:2]
        x.pop(-1)

        returnDict['name'] = str(x[0])
        returnDict['login'] = str(x[1])
        returnDict['currency'] = str(x[2])
        returnDict['type'] = str(x[3])
        returnDict['leverage'] = int(x[4])
        returnDict['trade_allowed'] = bool(x[5])
        returnDict['limit_orders'] = int(x[6])
        returnDict['margin_call'] = float(x[7])
        returnDict['margin_close'] = float(x[8])

        self.command_OK = True
        return returnDict

    def Get_dynamic_account_info(self):
        self.command_return_error = ''
        ok, dataString = self.send_command('F002#0#')
        if (ok == False):
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F002':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        returnDict = {}
        del x[0:2]
        x.pop(-1)

        returnDict['balance'] = float(x[0])
        returnDict['equity'] = float(x[1])
        returnDict['profit'] = float(x[2])
        returnDict['margin'] = float(x[3])
        returnDict['margin_level'] = float(x[4])
        returnDict['margin_free'] = float(x[5])

        self.command_OK = True
        return returnDict

    def Get_instrument_info(self,
                            instrument: str = 'EURUSD'):
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.command = 'F003#1#' + \
            self.get_broker_instrument_name(self.instrument_name_universal) + '#'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F003':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        returnDict = {}
        del x[0:2]
        x.pop(-1)

        returnDict['instrument'] = str(self.instrument_name_universal)
        returnDict['digits'] = int(x[0])
        returnDict['max_lotsize'] = float(x[1])
        returnDict['min_lotsize'] = float(x[2])
        returnDict['lot_step'] = float(x[3])
        returnDict['point'] = float(x[4])
        returnDict['tick_size'] = float(x[5])
        returnDict['tick_value'] = float(x[6])

        self.command_OK = True
        return returnDict

    def Check_instrument(self,
                         instrument: str = 'EURUSD'):
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.command = 'F004#1#' + \
            self.get_broker_instrument_name(self.instrument_name_universal) + ':'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F004':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return False

        return True

    def Get_broker_server_time(self):
        self.command_return_error = ''
        self.command = 'F005#0#'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F005':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        del x[0:2]
        x.pop(-1)
        y = x[0].split('-')
        d = datetime(int(y[0]), int(y[1]), int(y[2]),
                     int(y[3]), int(y[4]), int(y[5]))
        return d

    def Get_last_tick_info(self,
                           instrument: str = 'EURUSD'):
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        ok, dataString = self.send_command(
            'F020#1#' + self.get_broker_instrument_name(self.instrument_name_universal))

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F020':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        returnDict = {}
        del x[0:2]
        x.pop(-1)

        returnDict['instrument'] = str(self.instrument_name_universal)
        returnDict['date'] = int(x[0])
        returnDict['ask'] = float(x[1])
        returnDict['bid'] = float(x[2])
        returnDict['last'] = float(x[3])
        returnDict['volume'] = int(x[4])

        self.command_OK = True
        return returnDict

    def Get_last_x_ticks_from_now(self,
                                  instrument: str = 'EURUSD',
                                  nbrofticks: int = 2000):
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.nbrofticks = nbrofticks

        dt = np.dtype([('date', np.int64), ('ask', np.float64), ('bid',
                                                                 np.float64), ('last', np.float64), ('volume', np.int32)])
        ticks = np.empty(nbrofticks, dtype=dt)

        if (self.nbrofticks > self.max_ticks):
            iloop = self.nbrofticks / self.max_ticks
            iloop = math.floor(iloop)
            itail = int(self.nbrofticks - iloop * self.max_ticks)
            #print('iloop: ' + str(iloop))
            #print('itail: ' + str(itail))

            for index in range(0, iloop):
                self.command = 'F021#3#' + self.get_broker_instrument_name(
                    self.instrument_name_universal) + '#' + str(index * self.max_ticks) + ':' + str(self.max_ticks) + '#'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('#')
                if str(x[0]) != 'F021':
                    self.command_return_error = str(x[2])
                    self.command_OK = False
                    return None

                del x[0:2]
                x.pop(-1)

                for value in range(0, len(x)):
                    y = x[value].split('$')

                    ticks[value + index * self.max_ticks][0] = int(y[0])
                    ticks[value + index * self.max_ticks][1] = float(y[1])
                    ticks[value + index * self.max_ticks][2] = float(y[2])
                    ticks[value + index * self.max_ticks][3] = float(y[3])
                    ticks[value + index * self.max_ticks][4] = int(y[4])

                if (len(x) < self.max_ticks):
                    ticks = np.sort(ticks)
                    self.command_OK = True
                    return ticks

            if (itail == 0):
                ticks = np.sort(ticks)
                self.command_OK = True
                return ticks

            if (itail > 0):
                self.command = 'F021#3#' + self.get_broker_instrument_name(
                    self.instrument_name_universal) + '#' + str(iloop * self.max_ticks) + '#' + str(itail) + '#'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('#')
                if str(x[0]) != 'F021':
                    self.command_return_error = str(x[2])
                    self.command_OK = False
                    return None

                del x[0:2]
                x.pop(-1)

                for value in range(0, len(x)):
                    y = x[value].split('$')

                    ticks[value + iloop * self.max_ticks][0] = int(y[0])
                    ticks[value + iloop * self.max_ticks][1] = float(y[1])
                    ticks[value + iloop * self.max_ticks][2] = float(y[2])
                    ticks[value + iloop * self.max_ticks][3] = float(y[3])
                    ticks[value + iloop * self.max_ticks][4] = int(y[4])

                self.command_OK = True
                ticks = np.sort(ticks)
                return ticks
        else:
            self.command = 'F021#3#' + self.get_broker_instrument_name(
                self.instrument_name_universal) + '#' + str(0) + '#' + str(self.nbrofticks) + '#'
            ok, dataString = self.send_command(self.command)

            if not ok:
                self.command_OK = False
                return None
            if self.debug:
                print(dataString)
                print('')
                print(len(dataString))

            x = dataString.split('#')
            if str(x[0]) != 'F021':
                self.command_return_error = str(x[2])
                self.command_OK = False
                return None

            del x[0:2]
            x.pop(-1)

            for value in range(0, len(x)):
                y = x[value].split('$')

                ticks[value][0] = int(y[0])
                ticks[value][1] = float(y[1])
                ticks[value][2] = float(y[2])
                ticks[value][3] = float(y[3])
                ticks[value][4] = int(y[4])

        self.command_OK = True
        return ticks

    def Get_actual_bar_info(self,
                            instrument: str = 'EURUSD',
                            timeframe: int = 16408):
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.command = 'F041#2#' + self.get_broker_instrument_name(
            self.instrument_name_universal) + '#' + str(timeframe) + '#'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F041':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        del x[0:2]
        x.pop(-1)
        returnDict = {}
        returnDict['instrument'] = str(self.instrument_name_universal)
        returnDict['date'] = int(x[0])
        returnDict['open'] = float(x[1])
        returnDict['high'] = float(x[2])
        returnDict['low'] = float(x[3])
        returnDict['close'] = float(x[4])
        returnDict['volume'] = int(x[5])

        self.command_OK = True
        return returnDict

    def Get_last_x_bars_from_now(self,
                                 instrument: str = 'EURUSD',
                                 timeframe: int = 16408,
                                 nbrofbars: int = 1000):
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.numberofbars = nbrofbars

        dt = np.dtype([('date', np.int64), ('open', np.float64), ('high', np.float64),
                       ('low', np.float64), ('close', np.float64), ('volume', np.int32)])
        rates = np.empty(self.numberofbars, dtype=dt)

        if (self.numberofbars > self.max_bars):
            iloop = self.numberofbars / self.max_bars
            iloop = math.floor(iloop)
            itail = int(self.numberofbars - iloop * self.max_bars)
            #print('iloop: ' + str(iloop))
            #print('itail: ' + str(itail))

            for index in range(0, iloop):
                self.command = 'F042#4#' + self.get_broker_instrument_name(self.instrument_name_universal) + '#' + str(
                    timeframe) + '#' + str(index * self.max_bars) + '#' + str(self.max_bars) + '#'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('#')
                if str(x[0]) != 'F042':
                    self.command_return_error = str(x[2])
                    self.command_OK = False
                    return None

                del x[0:2]
                x.pop(-1)

                for value in range(0, len(x)):
                    y = x[value].split('$')

                    rates[value + index * self.max_bars][0] = int(y[0])
                    rates[value + index * self.max_bars][1] = float(y[1])
                    rates[value + index * self.max_bars][2] = float(y[2])
                    rates[value + index * self.max_bars][3] = float(y[3])
                    rates[value + index * self.max_bars][4] = float(y[4])
                    rates[value + index * self.max_bars][5] = int(y[5])

                if (len(x) < self.max_bars):
                    rates = np.sort(rates)
                    self.command_OK = True
                    return rates

            if (itail == 0):
                rates = np.sort(rates)
                self.command_OK = True
                return rates

            if (itail > 0):
                self.command = 'F042#4#' + self.get_broker_instrument_name(
                    self.instrument_name_universal) + '#' + str(timeframe) + '#' + str(
                    iloop * self.max_bars) + '#' + str(itail) + '#'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('#')
                if str(x[0]) != 'F042':
                    self.command_return_error = str(x[2])
                    self.command_OK = False
                    return None

                del x[0:2]
                x.pop(-1)

                for value in range(0, len(x)):
                    y = x[value].split('$')

                    rates[value + iloop * self.max_bars][0] = int(y[0])
                    rates[value + iloop * self.max_bars][1] = float(y[1])
                    rates[value + iloop * self.max_bars][2] = float(y[2])
                    rates[value + iloop * self.max_bars][3] = float(y[3])
                    rates[value + iloop * self.max_bars][4] = float(y[4])
                    rates[value + iloop * self.max_bars][5] = int(y[5])

                self.command_OK = True
                rates = np.sort(rates)
                return rates
        else:
            self.command = 'F042#4#' + self.get_broker_instrument_name(self.instrument_name_universal) + '#' + str(
                timeframe) + '#' + str(0) + '#' + str(self.numberofbars) + '#'

            ok, dataString = self.send_command(self.command)
            if not ok:
                self.command_OK = False
                return None
            if self.debug:
                print(dataString)
                print('')
                print(len(dataString))

            x = dataString.split('#')
            if str(x[0]) != 'F042':
                self.command_return_error = str(x[2])
                self.command_OK = False
                return None

            del x[0:2]
            x.pop(-1)

            for value in range(0, len(x)):
                y = x[value].split('$')

                rates[value][0] = int(y[0])
                rates[value][1] = float(y[1])
                rates[value][2] = float(y[2])
                rates[value][3] = float(y[3])
                rates[value][4] = float(y[4])
                rates[value][5] = int(y[5])

        self.command_OK = True
        return rates

    def Get_all_orders(self):
        self.command = 'F060#0#'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        orders = self.create_empty_DataFrame(self.columnsOpenOrders, 'id')
        x = dataString.split('#')
        if str(x[0]) != 'F060':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        del x[0:2]
        x.pop(-1)

        for value in range(0, len(x)):
            y = x[value].split('$')

            rowOrders = pd.Series(
                {
                    'ticket': int(
                        y[0]), 'instrument': self.get_universal_instrument_name(
                        str(
                            y[1])), 'order_type': str(
                        y[2]), 'magic_number': int(
                            y[3]), 'volume': float(
                                y[4]), 'open_price': float(
                                    y[5]), 'stop_loss': float(
                                        y[6]), 'take_profit': float(
                                            y[7]), 'comment': str(
                                                y[8])})
            orders = orders.append(rowOrders, ignore_index=True)

        self.command_OK = True
        return orders

    def Get_all_open_positions(self):
        self.command_return_error = ''
        self.command = 'F061#0#'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        positions = self.create_empty_DataFrame(
            self.columnsOpenPositions, 'id')
        x = dataString.split('#')
        if (str(x[0]) != 'F061'):
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        del x[0:2]
        x.pop(-1)

        for value in range(0, len(x)):
            y = x[value].split('$')

            rowPositions = pd.Series(
                {
                    'ticket': int(
                        y[0]), 'instrument': self.get_universal_instrument_name(
                        (y[1])), 'position_type': str(
                        y[2]), 'magic_number': int(
                        y[3]), 'volume': float(
                            y[4]), 'open_price': float(
                                y[5]), 'open_time': int(
                                    y[6]), 'stop_loss': float(
                                        y[7]), 'take_profit': float(
                                            y[8]), 'comment': str(
                                                y[9]), 'profit': float(
                                                    y[10]), 'swap': float(
                                                        y[11]), 'commission': float(
                                                            y[12])})
            positions = positions.append(rowPositions, ignore_index=True)

        self.command_OK = True
        return positions

    def Get_all_closed_positions(self,
                                 date_from: datetime = '2000-01-01 00:00:00',
                                 date_to: datetime = datetime.now()):
        self.command_return_error = ''
        self.date_from = date_from
        self.date_to = date_to
        self.command = 'F062#2#' + self.date_from.strftime(
            '%Y/%m/%d/%H/%M/%S') + '#' + self.date_to.strftime('%Y/%m/%d/%H/%M/%S') + '#'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        closed_positions = self.create_empty_DataFrame(
            self.columnsClosedPositions, 'id')
        x = dataString.split('#')
        if str(x[0]) != 'F062':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        del x[0:2]
        x.pop(-1)
        for value in range(0, len(x)):
            y = x[value].split('$')
            rowClosedPositions = pd.Series(
                {
                    'position_ticket': int(
                        y[0]), 'instrument': self.get_universal_instrument_name(
                        str(
                            y[1])), 'order_ticket': int(
                        y[2]), 'position_type': str(
                            y[3]), 'magic_number': int(
                                y[4]), 'volume': float(
                                    y[5]), 'open_price': float(
                                        y[6]), 'open_time': int(
                                            y[7]), 'close_price': float(
                                                y[8]), 'close_time': int(
                                                    y[9]), 'comment': str(
                                                        y[10]), 'profit': float(
                                                            y[11]), 'swap': float(
                                                                y[12]), 'commission': float(
                                                                    y[13])})
            closed_positions = closed_positions.append(
                rowClosedPositions, ignore_index=True)

        return closed_positions

    def Open_order(self,
                   instrument: str = '',
                   ordertype: str = 'buy',
                   volume: float = 0.01,
                   openprice: float = 0.0,
                   slippage: int = 5,
                   magicnumber: int = 0,
                   stoploss: float = 0.0,
                   takeprofit: float = 0.0,
                   comment: str = ''
                   ):
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        # check the command for ':' character
        # ':'not allowed, used as delimiter
        comment.replace('#', '')
        comment.replace('$', '')
        comment.replace('!', '')
        self.command = 'F070#8#' + self.get_broker_instrument_name(self.instrument_name_universal) + '#' + ordertype + '#' + str(volume) + '#' + str(
            openprice) + '#' + str(slippage) + '#' + str(magicnumber) + '#' + str(stoploss) + '#' + str(takeprofit) + '#' + str(comment) + '#'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return int(-1)

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F070':
            self.command_return_error = str(x[2])
            self.command_OK = False
            self.order_return_message = str(x[2])
            self.order_error = int(x[3])
            return int(-1)

        self.command_OK = True
        self.order_return_message = str(x[3])
        return int(x[2])

    def Close_position_by_ticket(self,
                                 ticket: int = 0):
        self.command_return_error = ''
        self.command = 'F071#1#' + str(ticket) + '#'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F071':
            self.command_return_error = str(x[2])
            self.command_OK = False
            self.order_return_message = str(x[2])
            self.order_error = int(x[3])
            return False

        return True

    def Close_position_partial_by_ticket(self,
                                         ticket: int = 0,
                                         volume_to_close: float = 0.01):
        self.command_return_error = ''
        self.command = 'F072#2#' + \
            str(ticket) + '#' + str(volume_to_close) + '#'

        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F072':
            self.command_return_error = str(x[2])
            self.command_OK = False
            self.order_return_message = str(x[2])
            self.order_error = int(x[3])
            return False

        return True

    def Delete_order_by_ticket(self,
                               ticket: int = 0):
        self.command_return_error = ''
        self.command = 'F073#1#' + str(ticket) + '#'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F073':
            self.command_return_error = str(x[2])
            self.command_OK = False
            self.order_return_message = str(x[2])
            self.order_error = int(x[3])
            return False

        return True

    def Set_sl_and_tp_for_position(self,
                                   ticket: int = 0,
                                   stoploss: float = 0.0,
                                   takeprofit: float = 0.0):
        self.command_return_error = ''
        self.command = 'F075#3#' + \
            str(ticket) + '#' + str(stoploss) + '#' + str(takeprofit) + '#'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F075':
            self.command_return_error = str(x[2])
            self.command_OK = False
            self.order_return_message = str(x[2])
            self.order_error = int(x[3])
            return False

        self.command_OK = True
        return True

    def Set_sl_and_tp_for_order(self,
                                ticket: int = 0,
                                stoploss: float = 0.0,
                                takeprofit: float = 0.0):
        self.command_return_error = ''
        self.command = 'F076#3#' + \
            str(position_ticket) + '#' + str(stoploss) + '#' + str(takeprofit) + '#'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F076':
            self.command_return_error = str(x[2])
            self.command_OK = False
            self.order_return_message = str(x[2])
            self.order_error = int(x[3])
            return False

        self.command_OK = True
        return True

    def send_command(self,
                     command):
        self.command = command + "!"
        self.timeout = False
        self.sock.send(bytes(self.command, "utf-8"))
        try:
            data_received = ''
            while True:
                data_received = data_received + self.sock.recv(500000).decode()
                if data_received.endswith('!'):
                    break
            return True, data_received
        except socket.timeout as msg:
            self.timeout = True
            print(msg)
            return False, None

    def get_timeframe_value(self,
                            timeframe: str = 'D1'):

        self.tf = mt5.TIMEFRAME_D1
        timeframe.upper()
        if timeframe == 'MN1':
            self.tf = mt5.TIMEFRAME_MN1
        if timeframe == 'W1':
            self.tf = mt5.TIMEFRAME_W1
        if timeframe == 'D1':
            self.tf = mt5.TIMEFRAME_D1
        if timeframe == 'H12':
            self.tf = mt5.TIMEFRAME_H12
        if timeframe == 'H8':
            self.tf = mt5.TIMEFRAME_H8
        if timeframe == 'H6':
            self.tf = mt5.TIMEFRAME_H6
        if timeframe == 'H4':
            self.tf = mt5.TIMEFRAME_H4
        if timeframe == 'H3':
            self.tf = mt5.TIMEFRAME_H3
        if timeframe == 'H2':
            self.tf = mt5.TIMEFRAME_H2
        if timeframe == 'H1':
            self.tf = mt5.TIMEFRAME_H1
        if timeframe == 'M30':
            self.tf = mt5.TIMEFRAME_M30
        if timeframe == 'M20':
            self.tf = mt5.TIMEFRAME_M20
        if timeframe == 'M15':
            self.tf = mt5.TIMEFRAME_M15
        if timeframe == 'M12':
            self.tf = mt5.TIMEFRAME_M12
        if timeframe == 'M10':
            self.tf = mt5.TIMEFRAME_M10
        if timeframe == 'M6':
            self.tf = mt5.TIMEFRAME_M6
        if timeframe == 'M5':
            self.tf = mt5.TIMEFRAME_M5
        if timeframe == 'M4':
            self.tf = mt5.TIMEFRAME_M4
        if timeframe == 'M3':
            self.tf = mt5.TIMEFRAME_M3
        if timeframe == 'M2':
            self.tf = mt5.TIMEFRAME_M2
        if timeframe == 'M1':
            self.tf = mt5.TIMEFRAME_M1

        return self.tf

    def get_broker_instrument_name(self,
                                   instrumentname: str = ''):
        self.intrumentname = instrumentname
        try:
            # str result =
            # (string)self.instrument_conversion_list.get(str(instrumentname))
            return self.instrument_conversion_list.get(str(instrumentname))
        except BaseException:
            return 'none'

    def get_universal_instrument_name(self,
                                      instrumentname: str = ''):
        self.instrumentname = instrumentname
        try:
            for item in self.instrument_conversion_list:
                key = str(item)
                value = self.instrument_conversion_list.get(item)
                if (value == instrumentname):
                    return str(key)
        except BaseException:
            return 'none'
        return 'none'

    def create_empty_DataFrame(self,
                               columns, index_col):
        index_type = next((t for name, t in columns if name == index_col))
        df = pd.DataFrame({name: pd.Series(dtype=t) for name,
                           t in columns if name != index_col},
                          index=pd.Index([],
                                         dtype=index_type))
        cols = [name for name, _ in columns]
        cols.remove(index_col)
        return df[cols]

    columnsOpenOrders = [
        ('id', int),
        ('ticket', int),
        ('instrument', str),
        ('order_type', str),
        ('magic_number', int),
        ('volume', float),
        ('open_price', float),
        ('stop_loss', float),
        ('take_profit', float),
        ('comment', str)]

    columnsOpenPositions = [
        ('id', int),
        ('ticket', int),
        ('instrument', str),
        ('position_type', str),
        ('magic_number', int),
        ('volume', float),
        ('open_price', float),
        ('open_time', int),
        ('stop_loss', float),
        ('take_profit', float),
        ('comment', str),
        ('profit', float),
        ('swap', float),
        ('commission', float)]

    columnsClosedPositions = [
        ('id', int),
        ('position_ticket', int),
        ('instrument', str),
        ('order_ticket', int),
        ('position_type', str),
        ('magic_number', int),
        ('volume', float),
        ('open_price', float),
        ('open_time', int),
        ('close_price', float),
        ('close_time', float),
        ('comment', str),
        ('profit', float),
        ('swap', float),
        ('commission', float)]
, float),
        ('open_price', float),
        ('open_time', int),
        ('close_price', float),
        ('close_time', float),
        ('comment', str),
        ('profit', float),
        ('swap', float),
        ('commission', float)]
