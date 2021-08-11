import socket
import numpy as np
import pandas as pd
from datetime import datetime
import pytz

import io

TZ_SERVER = 'Europe/Tallinn' # EET
TZ_LOCAL  = 'Europe/Budapest'
TZ_UTC    = 'UTC'



class Pytrader_API:             
  
    def __init__(self):
        self.socket_error: int = 0
        self.socket_error_message: str = ''
        self.order_return_message: str = ''
        self.order_error: int = 0
        self.connected: bool = False
        self.timeout: bool = False
        self.command_OK: bool = False
        self.command_return_error: str = ''
        self.debug: bool = False
        self.version: str = '1.06'
        self.max_bars: int = 5000
        self.max_ticks: int = 5000
        self.timeout_value: int = 60
        self.instrument_conversion_list: dict = {}
        self.instrument_name_broker: str = ''
        self.instrument_name_universal: str = ''
        self.date_from: datetime = '2000/01/01, 00:00:00'
        self.date_to: datetime = datetime.now()
        self.instrument: str = ''
        self.invert_array = False

    def Set_timeout(self,
                    timeout_in_seconds: int = 60
                    ):
        """
        Set time out value for socket communication with MT4 or MT5 EA/Bot.

        Args:
            timeout_in_seconds: the time out value
        Returns:
            None
        """
        self.timeout_value = timeout_in_seconds
        self.sock.settimeout(self.timeout_value)
        self.sock.setblocking(1)
        return

    def Disconnect(self):
        """
        Closes the socket connection to a MT4 or MT5 EA bot.

        Args:
            None
        Returns:
            bool: True or False
        """

        self.sock.close()
        return True

    def Connect(self,
                server: str = '',
                port: int = 2345,
                instrument_lookup: dict = []) -> bool:
        """
        Connects to a MT4 or MT5 EA/Bot.

        Args:
            server: Server IP address, like -> '127.0.0.1', '192.168.5.1'
            port: port number
            instrument_lookup: dictionairy with general instrument names and broker intrument names
        Returns:
            bool: True or False
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)
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

    def Check_connection(self) -> bool:
        """
        Checks if connection with MT terminal/Ea bot is still active.
        Args:
            None
        Returns:
            bool: True or False
        """

        self.command = 'F000#0#'
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        try:
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
        except:
            self.command_return_error = 'Unexpected socket communication error'
            self.command_OK = False
            return False

    @property
    def IsConnected(self) -> bool:
        """Returns connection status.
        Returns:
            bool: True or False
        """
        return self.connected

    def Set_bar_date_asc_dec(self,
                                asc_dec: bool = False) -> bool:
        """
        Sets first row of array as first bar or as last bar
        Args:
            asc_dec:    True = row[0] is oldest bar
                        False = row[0] is latest bar
        Returns:
            bool: True or False
        """ 
        self.invert_array = asc_dec
        return True

    def Get_static_account_info(self) -> dict:
        """
        Retrieves static account information.

        Returns: Dictionary with:
            Account name,
            Account number,
            Account currency,
            Account type,
            Account leverage,
            Account trading allowed,
            Account maximum number of pending orders,
            Account margin call percentage,
            Account close open trades margin percentage
        """
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

    def Get_dynamic_account_info(self) -> dict:
        """
        Retrieves dynamic account information.

        Returns: Dictionary with:
            Account balance,
            Account equity,
            Account profit,
            Account margin,
            Account margin level,
            Account margin free
        """
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

    def Get_PnL(self,
                    date_from: datetime = datetime(2021, 3, 1, tzinfo = pytz.timezone("Etc/UTC")),
                    date_to: datetime = datetime.now()) -> pd.DataFrame:
        '''    
        Retrieves profit loss info.

        Args:
            date_from: start date
            date_to: end date
        Returns: Dictionary with:
            realized_profit             profit of all closed positions
            unrealized_profit           profit of all open positions
            buy_profit                  profit of closed buy positions
            sell_profit                 profit of closed sell positions
            positions_in_profit         number of profit positions
            positions in loss           number of loss positions
            volume_in_profit            total volume of positions in profit
            volume_in_loss              total volume of positions in loss
        '''
        total_profit = 0.0
        buy_profit = 0.0
        sell_profit = 0.0
        trades_in_loss = 0
        trades_in_profit = 0
        volume_in_loss = 0.0
        volume_in_profit = 0.0
        commission_in_loss = 0.0
        commission_in_profit = 0.0
        swap_in_loss = 0.0
        swap_in_profit = 0.0
        unrealized_profit = 0.0

        
        # retrieve closed positions
        closed_positions = self.Get_closed_positions_within_window(date_from, date_to)
        if type(closed_positions) == pd.DataFrame:
            for position in closed_positions.itertuples():
                profit = position.profit + position.commission + position.swap
                total_profit = total_profit + profit
                if (profit > 0.0):
                    trades_in_profit = trades_in_profit + 1
                    volume_in_profit = volume_in_profit + position.volume
                    commission_in_profit = commission_in_profit + position.commission
                    swap_in_profit = swap_in_profit + position.swap                
                else:
                    trades_in_loss = trades_in_loss + 1
                    volume_in_loss = volume_in_loss + position.volume
                    commission_in_loss = commission_in_loss + position.commission
                    swap_in_loss = swap_in_loss + position.swap
                if (position.position_type == 'sell'):
                        sell_profit = sell_profit + profit
                if (position.position_type == 'buy'):
                        buy_profit = buy_profit + profit

            # retrieve dynamic account info
            dynamic_info = self.Get_dynamic_account_info()
            unrealized_profit = dynamic_info['equity'] - dynamic_info['balance']
            result = {}
            result['realized_profit'] = total_profit
            result['unrealized_profit'] = unrealized_profit
            result['buy_profit'] = buy_profit
            result['sell_profit'] = sell_profit
            result['positions_in_profit'] = trades_in_profit
            result['positions_in_loss'] = trades_in_loss
            result['volume_in_profit'] = volume_in_profit
            result['volume_in_loss'] = volume_in_loss

            return result
        else:
            return None

    def Get_instrument_info(self,
                            instrument: str = 'EURUSD') -> dict:
        """
        Retrieves instrument information.

        Args:
            instrument: instrument name
        Returns: Dictionary with:
            instrument,
            digits,
            max_lotsize,
            min_lotsize,
            lot_step,
            point,
            tick_size,
            tick_value
            swap_long
            swap_short
        """

        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none' or self.instrument == None):
            self.command_return_error = 'Instrument not in broker list'
            self.command_OK = False
            return None


        self.command = 'F003#1#' + self.instrument + '#'

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
        returnDict['swap_long'] = float(x[7])
        returnDict['swap_short'] = float(x[8])

        self.command_OK = True
        return returnDict

    def Check_instrument(self,
                         instrument: str = 'EURUSD') -> str:
        """
        Check if instrument known / market watch at broker.

        Args:
            instrument: instrument name
        Returns:
            bool: True or False
        """
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none'):
            self.command_return_error = 'Instrument not in list'
            self.command_OK = False
            return None

        self.command = 'F004#1#' + self.instrument + '#'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return False, 'Error'

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F004':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return False, str(x[2])

        return True, str(x[2])

    def Get_instruments(self) ->list:
        """
        Retrieves broker market instruments list.

        Args:
            None
        Returns:
            List: All market symbols as universal instrument names
        """
        self.command_return_error = ''

        self.command = 'F007#1#'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        # analyze the answer
        return_list = []
        x = dataString.split('#')
        if x[0] != 'F007':
            self.command_return_error = 'Undefined error'
            self.command_OK = False
            return return_list
        
        del x[0:2]
        x.pop(-1)
        for item in range(0, len(x)):
            _instrument = str(x[item])
            instrument = self.get_universal_instrument_name(_instrument)
            if (instrument != None):
                return_list.append(instrument)
        return return_list
       
    def Get_broker_server_time(self) -> datetime:
        """
        Retrieves broker server time.

        Args:
            None
        Returns:
            datetime: Boker time
        """
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
                           instrument: str = 'EURUSD') -> dict:
        """
        Retrieves instrument last tick data.

        Args:
            instrument: instrument name
        Returns: Dictionary with:
            instrument name,
            date,
            ask,
            bid,
            last volume,
            volume
            spread
        """
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none'):
            self.command_return_error = 'Instrument not in list'
            self.command_OK = False
            return None
        ok, dataString = self.send_command('F020#1#' + self.instrument)

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
        returnDict['spread'] = int(x[5])

        self.command_OK = True
        return returnDict

    def Get_last_x_ticks_from_now(self,
                                  instrument: str = 'EURUSD',
                                  nbrofticks: int = 2000) -> np.array:
        """
        Retrieves last x ticks from an instrument.

        Args:
            instrument: instrument name
            nbrofticks: number of ticks to retriev
        Returns: numpy array with:
            date,
            ask,
            bid,
            last volume,
            volume
        """
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none'):
            self.command_return_error = 'Instrument not in list'
            self.command_OK = False
            return None
        
        self.nbrofticks = nbrofticks

        dt = np.dtype([('date', np.int64), ('ask', np.float64), ('bid', np.float64), ('last', np.float64), ('volume', np.int32)])
        #ticks = np.empty(nbrofticks, dtype=dt)
        ticks = np.zeros(nbrofticks, dtype=dt)

        if (self.nbrofticks > self.max_ticks):
            iloop = self.numberofbars // self.max_bars
            itail = self.numberofbars % self.max_bars
            #iloop = self.nbrofticks / self.max_ticks
            #iloop = math.floor(iloop)
            #itail = int(self.nbrofticks - iloop * self.max_ticks)

            for index in range(0, iloop):
                self.command = 'F021#3#' + self.instrument + '#' + str(index * self.max_ticks) + ':' + str(self.max_ticks) + '#'
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
                    #ticks = np.sort(ticks)
                    ticks = np.sort(ticks[ticks[:]['date']!=0])
                    self.command_OK = True
                    return ticks

            if (itail == 0):
                #ticks = np.sort(ticks)
                ticks = np.sort(ticks[ticks[:]['date']!=0])
                self.command_OK = True
                return ticks

            if (itail > 0):
                self.command = 'F021#3#' + self.instrument + '#' + str(iloop * self.max_ticks) + '#' + str(itail) + '#'
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
                #ticks = np.sort(ticks)
                ticks = np.sort(ticks[ticks[:]['date']!=0])
                return ticks
        else:
            self.command = 'F021#3#' + self.instrument + '#' + str(0) + '#' + str(self.nbrofticks) + '#'
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
        #return ticks
        return ticks[:len(x)]

    def Get_actual_bar_info(self,
                            instrument: str = 'EURUSD',
                            timeframe: int = 16408) -> dict:
        """
        Retrieves instrument last actual data.
        

        Args:
            instrument: instrument name
            timeframe: time frame like H1, H4
        Returns: Dictionary with:
            instrument name,
            date,
            open,
            high,
            low,
            close,
            volume,
        """
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none'):
            self.command_return_error = 'Instrument not in list'
            self.command_OK = False
            return None
        self.command = 'F041#2#' + self.instrument + '#' + str(timeframe) + '#'
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

    def Get_specific_bar(self,
                                instrument_list: list = ['EURUSD', 'GBPUSD'],
                                specific_bar_index: int = 1,
                                timeframe: int = 16408) -> dict:
        """
        Retrieves instrument data(d, o, h, l, c, v) of one bar(index) for the instruments in the list.

        Args:
            instrument: instrument name
            specific_bar_index: the specific bar (0 = actual bar)
            timeframe: time frame like H1, H4
        Returns: Dictionary with:       {instrument:{instrument data}}
            instrument name,
            [date,
            open,
            high,
            low,
            close,
            volume]
        """
        self.command_return_error = ''
        # compose MT5 command string
        self.command = 'F045#3#'
        for index in range (0, len(instrument_list), 1):
            _instr = self.get_broker_instrument_name(instrument_list[index].upper())
            self.command = self.command + _instr + '$'
        
        self.command = self.command + '#' + str(specific_bar_index) + '#' + str(timeframe) + '#'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F045':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        del x[0:2]
        x.pop(-1)
        result = {}
        
        for value in range(0, len(x)):
            y = x[value].split('$')
            symbol_result = {}
            symbol = str(y[0])
            symbol_result['date'] = int(y[1])
            symbol_result['open'] = float(y[2])
            symbol_result['high'] = float(y[3])
            symbol_result['low'] = float(y[4])
            symbol_result['close'] = float(y[5])
            symbol_result['volume'] = float(y[6])
            result[symbol] = symbol_result
        
        return result

    def Get_last_x_bars_from_now(self,
                                 instrument: str = 'EURUSD',
                                 timeframe: int = 16408,
                                 nbrofbars: int = 1000) -> np.array:
        """
        Retrieves last x bars from a MT4 or MT5 EA bot.

        Args:
            instrument: name of instrument like EURUSD
            timeframe: timeframe like 'H4'
            nbrofbars: Number of bars to retrieve
        Returns: numpy array with:
            date,
            open,
            high,
            low,
            close,
            volume
        """
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none'):
            self.command_return_error = 'Instrument not in list'
            self.command_OK = False
            return None
        self.numberofbars = nbrofbars

        dt = np.dtype([('date', np.int64), ('open', np.float64), ('high', np.float64),
                       ('low', np.float64), ('close', np.float64), ('volume', np.int32)])
        #rates = np.empty(self.numberofbars, dtype=dt)
        rates = np.zeros(self.numberofbars, dtype=dt)

        if (self.numberofbars > self.max_bars):
            #iloop = self.numberofbars / self.max_bars
            #iloop = math.floor(iloop)
            #itail = int(self.numberofbars - iloop * self.max_bars)
            iloop = self.numberofbars // self.max_bars
            itail = self.numberofbars % self.max_bars
            #print('iloop: ' + str(iloop))
            #print('itail: ' + str(itail))

            for index in range(0, iloop):
                self.command = 'F042#4#' + self.instrument + '#' + \
                        str(timeframe) + '#' + str(index * self.max_bars) + '#' + str(self.max_bars) + '#'
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
                    #rates = np.sort(rates)
                    rates = np.sort(rates[rates[:]['date']!=0])
                    self.command_OK = True
                    return rates

            if (itail == 0):
                #rates = np.sort(rates)
                rates = np.sort(rates[rates[:]['date']!=0])
                self.command_OK = True
                if (self.invert_array == True):
                    rates = rates = np.sort(rates[rates[:]['date']!=0])
                return rates

            if (itail > 0):
                self.command = 'F042#4#' + self.instrument + '#' + str(timeframe) + '#' + str(
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
                #rates = np.sort(rates)
                rates = np.sort(rates[rates[:]['date']!=0])
                if (self.invert_array == True):
                    rates = rates = np.sort(rates[rates[:]['date']!=0])
                return rates
        else:
            self.command = 'F042#4#' + str(self.instrument) + '#' + \
                    str(timeframe) + '#' + str(0) + '#' + str(self.numberofbars) + '#'
            #print(self.command)
            ok, dataString = self.send_command(self.command)
            if not ok:
                self.command_OK = False
                print('not ok')
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
        if (self.invert_array == True):
            rates = rates = np.sort(rates[rates[:]['date']!=0])
        #return rates
        return rates[:len(x)]

    def Get_all_deleted_orders(self) -> pd.DataFrame:
        """
        Retrieves all deleted pending orders.
        
        Args:

        Returns:
            data array(panda) with all position information:
            ticket,
            instrument,
            order_type,
            magic_number,
            volume,
            open_price,
            open_time,
            stop_loss,
            take_profit,
            delete_price,
            delete_time,
            comment
        """

        # reset parameters
        self.command_return_error = ''

        # get all pending orders
        ok, resp = self.send_command("F065#0#")

        if self.debug:
            print(resp)

        if ok==True and resp[0:5]=="F065#" and resp[-1]=="!":
            nbr = resp[resp.index('#',3)+1:resp.index('#',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('#',5)+1:-1]), sep='$', lineterminator='#',
                                header=None,
                                names=np.array(self.columnsDeletedOrders[1:])[:,0],
                                dtype=self.columnsDeletedOrders[1:]
                ).fillna('')
                # no time conversion
                # df.open_time = pd.to_datetime(df.open_time, unit='s').dt.tz_localize(TZ_SERVER).dt.tz_convert(TZ_UTC)
                # sort by open_time ascending
                df.sort_values(by=['open_time'], ascending= True,inplace=True)
                return df
            else:
                # return empty dataframe
                return self.create_empty_DataFrame(
                        self.columnsDeletedOrders, 'id')
        else:
            # error
            if not ok:
                self.command_OK = False
                return None
            else:
                x = resp.split('#')
                self.command_return_error = str(x[2])
                self.command_OK = False
                return None 

    def Get_deleted_orders_within_window(self,
                                 date_from: datetime = datetime(2021, 3, 25, tzinfo = pytz.timezone("Etc/UTC")),
                                 date_to: datetime = datetime.now()) -> pd.DataFrame:

        """ 
        Retrieves all deleted pending orders within time window.
        Open and close time of order must be within the time window

        Args:
            date_from: date to start retrieving orders from
            date_to: date to stop retrieving to
        Returns:
            data array(panda) with all position information:
            ticket,
            instrument,
            order_type,
            magic_number,
            volume,
            open_price,
            open_time,
            stop_loss,
            take_profit,
            delete_price,
            delete_time,
            comment
        """


        # reset/set parameters
        self.command_return_error = ''
        self.date_from = date_from
        self.date_to = date_to

        # get all pending orders
        self.command = 'F064#2#' + self.date_from.strftime(
            '%Y/%m/%d/%H/%M/%S') + '#' + self.date_to.strftime('%Y/%m/%d/%H/%M/%S') + '#'
        ok, resp = self.send_command(self.command)

        if self.debug:
            print(resp)

        if ok==True and resp[0:5]=="F064#" and resp[-1]=="!":
            nbr = resp[resp.index('#',3)+1:resp.index('#',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('#',5)+1:-1]), sep='$', lineterminator='#',
                                header=None,
                                names=np.array(self.columnsDeletedOrders[1:])[:,0],
                                dtype=self.columnsDeletedOrders[1:]
                ).fillna('')
                # no time conversion
                # df.open_time = pd.to_datetime(df.open_time, unit='s').dt.tz_localize(TZ_SERVER).dt.tz_convert(TZ_UTC)
                # sort by open_time ascending
                df.sort_values(by=['open_time'], ascending= True,inplace=True)
                return df
            else:
                # return empty dataframe
                return self.create_empty_DataFrame(
                        self.columnsDeletedOrders, 'id')
        else:
            # error
            if not ok:
                self.command_OK = False
                return None
            else:
                x = resp.split('#')
                self.command_return_error = str(x[2])
                self.command_OK = False
                return None 

    def Get_all_orders(self) -> pd.DataFrame:
        
        """
        Retrieves all pending orders.
        
        Args:

        Returns:
            data array(panda) with all order information:
            ticket,
            instrument,
            order_type,
            magic number,
            volume/lotsize,
            open price,
            open_time,
            stop_loss,
            take_profit,
            comment
        """

        # reset parameters
        self.command_return_error = ''

        # get all pending orders
        ok, resp = self.send_command("F060#0#")

        if self.debug:
            print(resp)
        
        if ok==True and resp[0:5]=="F060#" and resp[-1]=="!":
            nbr = resp[resp.index('#',3)+1:resp.index('#',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('#',5)+1:-1]), sep='$', lineterminator='#',
                                header=None,
                                names=np.array(self.columnsOpenOrders[1:])[:,0],
                                dtype=self.columnsOpenOrders[1:]
                ).fillna('')
                # no time conversion
                # df.open_time = pd.to_datetime(df.open_time, unit='s').dt.tz_localize(TZ_SERVER).dt.tz_convert(TZ_UTC)
                # sort by open_time ascending
                df.sort_values(by=['open_time'], ascending= True,inplace=True)
                return df
            else:
                # return empty dataframe
                return self.create_empty_DataFrame(
                        self.columnsOpenOrders, 'id')
        else:
            # error
            if not ok:
                self.command_OK = False
                return None
            else:
                x = resp.split('#')
                self.command_return_error = str(x[2])
                self.command_OK = False
                return None 
    
    def Get_all_open_positions(self) -> pd.DataFrame:

        """
        Retrieves all open positions, market orders for MT4.

        Args:
            none

        Returns:
            data array(panda) with all position information:
            ticket,
            instrument,
            order_ticket, for MT5 deal ticket, for MT4 order ticket
            position_type,
            magic_number,
            volume/lotsize,
            open_price,
            open_time,
            stopp_loss,
            take_profit,
            comment,
            profit,
            swap,
            commission
        """
        # reset parameters
        self.command_return_error = ''

        # get all open positions
        ok, resp = self.send_command("F061#0#")

        if self.debug:
            print(resp)

        if ok==True and resp[0:5]=="F061#" and resp[-1]=="!":

            nbr = resp[resp.index('#',3)+1:resp.index('#',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('#',5)+1:-1]), sep='$', lineterminator='#',
                                header=None,
                                names=np.array(self.columnsOpenPositions[1:])[:,0],
                                dtype=self.columnsOpenPositions[1:]
                ).fillna('')
                # no time conversion
                # df.open_time = pd.to_datetime(df.open_time, unit='s').dt.tz_localize(TZ_SERVER).dt.tz_convert(TZ_UTC)
                # sort by open_time ascending
                df.sort_values(by=['open_time'], ascending= True,inplace=True)
                return df
            else:
                # return empty dataframe
                return self.create_empty_DataFrame(
                        self.columnsOpenPositions, 'id') 
        else:
            # error
            if not ok:
                self.command_OK = False
                return None
            else:
                x = resp.split('#')
                self.command_return_error = str(x[2])
                self.command_OK = False
                return None  

    def Get_closed_positions_within_window(self,
                                 date_from: datetime = datetime(2021, 3, 20, tzinfo = pytz.timezone("Etc/UTC")),
                                 date_to: datetime = datetime.now()) -> pd.DataFrame:
        
        """ 
        Retrieves all closed positions/orders within time window.
        Open and close time must be within the time window

        Args:
            date_from: date to start retrieving orders from
            date_to: date to stop retrieving to
        Returns:
            data array(panda) with all position information:
            ticket,
            instrument,
            order_ticket,
            position_type,
            magic_number,
            volume,
            open_price,
            open_time,
            stop_loss,
            take_profit,
            close_price,
            close_time,
            comment,
            profit,
            swap,
            commission
        """
        self.command_return_error = ''
        self.date_from = date_from
        self.date_to = date_to
        self.command = 'F062#2#' + self.date_from.strftime(
            '%Y/%m/%d/%H/%M/%S') + '#' + self.date_to.strftime('%Y/%m/%d/%H/%M/%S') + '#'
        
        
        ok, resp = self.send_command(self.command)

        if self.debug:
            print(resp)

        if not ok:
            self.command_OK = False
            return None

        if ok==True and resp[0:5]=="F062#" and resp[-1]=="!":
            nbr = resp[resp.index('#',3)+1:resp.index('#',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('#',5)+1:-1]), sep='$', lineterminator='#',
                                header=None,
                                names=np.array(self.columnsClosedPositions[1:])[:,0],
                                dtype=self.columnsClosedPositions[1:]
                ).fillna('')
                # no time conversion
                # df.open_time = pd.to_datetime(df.open_time, unit='s').dt.tz_localize(TZ_SERVER).dt.tz_convert(TZ_UTC)
                # sort by open_time ascending
                df.sort_values(by=['open_time'], ascending= True,inplace=True)
                return df
            else:
                # return empty dataframe
                return self.create_empty_DataFrame(
                        self.columnsClosedPositions, 'id') 
        else:
            # error
            if not ok:
                self.command_OK = False
                return None
            else:
                x = resp.split('#')
                self.command_return_error = str(x[2])
                self.command_OK = False
                return None     

    def Get_all_closed_positions(self) -> pd.DataFrame:
        """ 
            Retrieves all closed positions/orders.
            For MT4 all must be visible in the history tab of the MT4 terminal

        Args:
            
        Returns:
            data array(panda) with all position information:
            ticket,
            instrument,
            order_ticket,
            position_type,
            magic_number,
            volume,
            open_price,
            open_time,
            stop_loss,
            take_profit,
            close_price,
            close_time,
            comment,
            profit,
            swap,
            commission
        """
        self.command_return_error = ''

        self.command = 'F063#0#'
        ok, resp = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(resp)

        if ok==True and resp[0:5]=="F063#" and resp[-1]=="!":
            nbr = resp[resp.index('#',3)+1:resp.index('#',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('#',5)+1:-1]), sep='$', lineterminator='#',
                                header=None,
                                names=np.array(self.columnsClosedPositions[1:])[:,0],
                                dtype=self.columnsClosedPositions[1:]
                ).fillna('')
                # no time conversion
                # df.open_time = pd.to_datetime(df.open_time, unit='s').dt.tz_localize(TZ_SERVER).dt.tz_convert(TZ_UTC)
                # sort by open_time ascending
                df.sort_values(by=['open_time'], ascending= True,inplace=True)
                return df
            else:
                # return empty dataframe
                return self.create_empty_DataFrame(
                        self.columnsClosedPositions, 'id') 
        else:
            # error
            if not ok:
                self.command_OK = False
                return None
            else:
                x = resp.split('#')
                self.command_return_error = str(x[2])
                self.command_OK = False
                return None

    def Open_order(self,
                   instrument: str = '',
                   ordertype: str = 'buy',
                   volume: float = 0.01,
                   openprice: float = 0.0,
                   slippage: int = 5,
                   magicnumber: int = 0,
                   stoploss: float = 0.0,
                   takeprofit: float = 0.0,
                   comment: str = '',
                   market: bool = False
                   ) -> int:
        """
        Open an order.

        Args:
            instrument: instrument
            ordertype: type of order, buy, sell, buy stop, sell stop, buy limit, sell limit
            volume: order volume/lot size
            open price: open price for order, 0.0 for market orders
            slippage: allowed slippage
            magicnumber: magic number for this order
            stoploss: order stop loss price, actual price, so not relative to open price
            takeprofit: order take profit, actual price, so not relative to open price
            comment: order comment
        Returns:
            int: ticket number. If -1, open order failed
        """

        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        # check the command for '#' , '$', '!' character
        # these are not allowed, used as delimiters
        comment.replace('#', '')
        comment.replace('$', '')
        comment.replace('!', '')
        broker_instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (broker_instrument == None):
            self.command_return_error = 'Instrument not known, check brookerlookuptable'
            self.command_OK = False
            self.order_return_message = 'Instrument not known, check brookerlookuptable'
            return int(-1)
        
        self.command = 'F070#10#' + self.get_broker_instrument_name(self.instrument_name_universal) + '#' + ordertype + '#' + str(volume) + '#' + \
            str(openprice) + '#' + str(slippage) + '#' + str(magicnumber) + '#' + str(stoploss) + '#' + str(takeprofit) + '#' + str(comment) + '#' + str(market) + '#'
        #print(self.command)
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
                                 ticket: int = 0) -> bool:
        """
        Close a position.

        Args:
            ticket: ticket of position to close

        Returns:
            bool: True or False
        """
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
                                         volume_to_close: float = 0.01) -> bool:
        """
        Close a position partial.

        Args:
            ticket: ticket of position to close
            volume_to_close: volume part to close, must be small then order volume
        Returns:
            bool: True or False
        """
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
                               ticket: int = 0) -> bool:
        """
        Delete an order.

        Args:
            ticket: ticket of order(pending) to delete

        Returns:
            bool: True or False
        """
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
                                   takeprofit: float = 0.0) -> bool:
        """
        Change stop loss and take profit for a position.

        Args:
            ticket: ticket of position to change
            stoploss; new stop loss value, must be actual price value
            takeprofit: new take profit value, must be actual price value

        Returns:
            bool: True or False
        """
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
                                takeprofit: float = 0.0) -> bool:
        """
        Change stop loss and take profit for an order.

        Args:
            ticket: ticket of order to change
            stoploss; new stop loss value, must be actual price value
            takeprofit: new take profit value, must be actual price value

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F076#3#' + \
            str(ticket) + '#' + str(stoploss) + '#' + str(takeprofit) + '#'
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

    def Reset_sl_and_tp_for_position(self,
                                ticket: int = 0) -> bool:
        """
        Reset stop loss and take profit for a position.

        Args:
            ticket: ticket of position to change

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F077#1#' + str(ticket) + '#' 
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F077':
            self.command_return_error = str(x[2])
            self.command_OK = False
            self.order_return_message = str(x[2])
            self.order_error = int(x[3])
            return False

        self.command_OK = True
        return True

    def Reset_sl_and_tp_for_order(self,
                                ticket: int = 0) -> bool:
        """
        Reset stop loss and take profit for an order.

        Args:
            ticket: ticket of order to change


        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F078#1#' + str(ticket) + '#'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F078':
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
        #print(self.command)
        #print(self.socket)
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
            self.command_return_error = 'Unexpected socket communication error'
            print(msg)
            return False, None

    def get_timeframe_value(self,
                            timeframe: str = 'D1') -> int:

        self.tf = 16408  # mt5.TIMEFRAME_D1
        timeframe.upper()
        if timeframe == 'MN1':
            self.tf = 49153  # mt5.TIMEFRAME_MN1
        if timeframe == 'W1':
            self.tf = 32769  # mt5.TIMEFRAME_W1
        if timeframe == 'D1':
            self.tf = 16408  # mt5.TIMEFRAME_D1
        if timeframe == 'H12':
            self.tf = 16396  # mt5.TIMEFRAME_H12
        if timeframe == 'H8':
            self.tf = 16392  # mt5.TIMEFRAME_H8
        if timeframe == 'H6':
            self.tf = 16390  # mt5.TIMEFRAME_H6
        if timeframe == 'H4':
            self.tf = 16388  # mt5.TIMEFRAME_H4
        if timeframe == 'H3':
            self.tf = 16387  # mt5.TIMEFRAME_H3
        if timeframe == 'H2':
            self.tf = 16386  # mt5.TIMEFRAME_H2
        if timeframe == 'H1':
            self.tf = 16385  # mt5.TIMEFRAME_H1
        if timeframe == 'M30':
            self.tf = 30  # mt5.TIMEFRAME_M30
        if timeframe == 'M20':
            self.tf = 20  # mt5.TIMEFRAME_M20
        if timeframe == 'M15':
            self.tf = 15  # mt5.TIMEFRAME_M15
        if timeframe == 'M12':
            self.tf = 12  # mt5.TIMEFRAME_M12
        if timeframe == 'M10':
            self.tf = 10  # mt5.TIMEFRAME_M10
        if timeframe == 'M6':
            self.tf = 6  # mt5.TIMEFRAME_M6
        if timeframe == 'M5':
            self.tf = 5  # mt5.TIMEFRAME_M5
        if timeframe == 'M4':
            self.tf = 4  # mt5.TIMEFRAME_M4
        if timeframe == 'M3':
            self.tf = 3  # mt5.TIMEFRAME_M3
        if timeframe == 'M2':
            self.tf = 2  # mt5.TIMEFRAME_M2
        if timeframe == 'M1':
            self.tf = 1  # mt5.TIMEFRAME_M1

        return self.tf

    def get_broker_instrument_name(self,
                                   instrumentname: str = '') -> str:
        self.intrumentname = instrumentname
        try:
            # str result =
            # (string)self.instrument_conversion_list.get(str(instrumentname))
            return self.instrument_conversion_list.get(str(instrumentname))
        except BaseException:
            return 'none'

    def get_universal_instrument_name(self,
                                      instrumentname: str = '') -> str:
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
                               columns, index_col) -> pd.DataFrame:
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
        ('open_time', int),
        ('stop_loss', float),
        ('take_profit', float),
        ('comment', str)]

    columnsDeletedOrders = [
        ('id', int),
        ('ticket', int),
        ('instrument', str),
        ('order_type', str),
        ('magic_number', int),
        ('volume', float),
        ('open_price', float),
        ('open_time', int),
        ('stop_loss', float),
        ('take_profit', float),
        ('delete_price', float),
        ('delete_time', int),
        ('comment', str)]

    columnsOpenPositions = [
        ('id', int),
        ('ticket', int),
        ('instrument', str),
        ('order_ticket', int),
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
        ('ticket', int),
        ('instrument', str),
        ('order_ticket', int),
        ('position_type', str),
        ('magic_number', int),
        ('volume', float),
        ('open_price', float),
        ('open_time', int),
        ('stop_loss', float),
        ('take_profit', float),
        ('close_price', float),
        ('close_time', int),
        ('comment', str),
        ('profit', float),
        ('swap', float),
        ('commission', float)]