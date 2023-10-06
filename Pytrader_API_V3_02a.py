# Pytrader API for MT4 and MT5
# Version V3_01

import socket
import numpy as np
import pandas as pd
from datetime import datetime
import pytz
import io

TZ_SERVER = 'Europe/Tallinn' # EET
TZ_LOCAL  = 'Europe/Budapest'
TZ_UTC    = 'UTC'

ERROR_DICT = {}
ERROR_DICT['00001'] = 'Undefined check connection error'

ERROR_DICT['00101'] = 'IP address error'
ERROR_DICT['00102'] = 'Port number error'
ERROR_DICT['00103'] = 'Connection error with license EA'
ERROR_DICT['00104'] = 'Undefined answer from license EA'

ERROR_DICT['00301'] = 'Unknown instrument for broker'
ERROR_DICT['00302'] = 'Instrument not in demo'
ERROR_DICT['00304'] = 'Unknown instrument for broker'

ERROR_DICT['01101'] = 'Undefined check terminal connection error'

ERROR_DICT['01201'] = 'Undefined check MT type error'

ERROR_DICT['00401'] = 'Instrument not in demo'
ERROR_DICT['00402'] = 'Instrument not exists for broker'

ERROR_DICT['00501'] = 'No instrument defined/configured'

ERROR_DICT['02001'] = 'Instrument not in demo'
ERROR_DICT['02004'] = 'Unknown instrument for broker'
ERROR_DICT['02003'] = 'Unknown instrument for broker'

ERROR_DICT['02101'] = 'Instrument not in demo'
ERROR_DICT['02102'] = 'No ticks'
ERROR_DICT['02103'] = 'Not imlemented in MT4'

ERROR_DICT['04101'] = 'Instrument not in demo'
ERROR_DICT['04102'] = 'Wrong/unknown time frame'
ERROR_DICT['04103'] = 'No records'
ERROR_DICT['04104'] = 'Undefined error'
ERROR_DICT['04105'] = 'Unknown instrument for broker'


ERROR_DICT['04201'] = 'Instrument not in demo'
ERROR_DICT['04202'] = 'Wrong/unknown time frame'
ERROR_DICT['04203'] = 'No records' 
ERROR_DICT['04204'] = 'Unknown instrument for broker'

ERROR_DICT['04501'] = 'Instrument not in demo'
ERROR_DICT['04502'] = 'Wrong/unknown time frame'
ERROR_DICT['04503'] = 'No records'
ERROR_DICT['04504'] = 'Missing market instrument'

ERROR_DICT['06201'] = 'Wrong time window'
ERROR_DICT['06401'] = 'Wrong time window'

ERROR_DICT['07001'] = 'Trading not allowed, check MT terminal settings' 
ERROR_DICT['07002'] = 'Instrument not in demo' 
ERROR_DICT['07003'] = 'Instrument not in market watch' 
ERROR_DICT['07004'] = 'Instrument not known for broker'
ERROR_DICT['07005'] = 'Unknown order type' 
ERROR_DICT['07006'] = 'Wrong SL value' 
ERROR_DICT['07007'] = 'Wrong TP value'
ERROR_DICT['07008'] = 'Wrong volume value'
ERROR_DICT['07009'] = 'Error opening market order'
ERROR_DICT['07010'] = 'Error opening pending order'
ERROR_DICT['07011'] = 'Unknown instrument for broker'

ERROR_DICT['07101'] = 'Trading not allowed'
ERROR_DICT['07102'] = 'Position not found/error'

ERROR_DICT['07201'] = 'Trading not allowed'
ERROR_DICT['07202'] = 'Position not found/error'
ERROR_DICT['07203'] = 'Wrong volume'
ERROR_DICT['07204'] = 'Error in partial close'

ERROR_DICT['07301'] = 'Trading not allowed'
ERROR_DICT['07302'] = 'Error in delete'

ERROR_DICT['07501'] = 'Trading not allowed'
ERROR_DICT['07502'] = 'Position not open' 
ERROR_DICT['07503'] = 'Error in modify'

ERROR_DICT['07601'] = 'Trading not allowed'
ERROR_DICT['07602'] = 'Position not open' 
ERROR_DICT['07603'] = 'Error in modify'

ERROR_DICT['07701'] = 'Trading not allowed'
ERROR_DICT['07702'] = 'Position not open' 
ERROR_DICT['07703'] = 'Error in modify'

ERROR_DICT['07801'] = 'Trading not allowed'
ERROR_DICT['07802'] = 'Position not open' 
ERROR_DICT['07803'] = 'Error in modify'

ERROR_DICT['07901'] = 'Trading not allowed'
ERROR_DICT['07902'] = 'Instrument not in demo'
ERROR_DICT['07903'] = 'Order does not exist' 
ERROR_DICT['07904'] = 'Wrong order type'
ERROR_DICT['07905'] = 'Wrong price'
ERROR_DICT['07906'] = 'Wrong TP value'
ERROR_DICT['07907'] = 'Wrong SL value'
ERROR_DICT['07908'] = 'Check error code'
ERROR_DICT['07909'] = 'Something wrong'

ERROR_DICT['08101'] = 'Unknown global variable'

ERROR_DICT['08201'] = 'Log file not existing'
ERROR_DICT['08202'] = 'Log file empty'
ERROR_DICT['08203'] = 'Error in reading log file'
ERROR_DICT['08204'] = 'Function not implemented'

ERROR_DICT['09101'] = 'Trading not allowed'
ERROR_DICT['09102'] = 'Unknown instrument for broker'
ERROR_DICT['09103'] = 'Function not implemented'

ERROR_DICT['99900'] = 'Wrong authorizaton code'

ERROR_DICT['99901'] = 'Undefined error'

ERROR_DICT['99999'] = 'Dummy'


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
        self.version: str = 'V3.02a'
        self.max_bars: int = 5000
        self.max_ticks: int = 5000
        self.timeout_value: int = 60
        self.instrument_conversion_list: dict = {}
        self.instrument_name_broker: str = ''
        self.instrument_name_universal: str = ''
        self.date_from: datetime = '2000/01/01, 00:00:00'
        self.date_to: datetime = datetime.now()
        self.instrument: str = ''
        self.license = 'Demo'
        self.invert_array = False
        self.authorization_code: str = 'None'

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
                instrument_lookup: dict = [],
                authorization_code: str = 'None') -> bool:
        """
        Connects to a MT4 or MT5 EA/Bot.

        Args:
            server: Server IP address, like -> '127.0.0.1', '192.168.5.1'
            port: port number
            instrument_lookup: dictionairy with general instrument names and broker intrument names
            authorization_code: authorization code, this can be used as extra security. The code has also to be set in the EA's
        Returns:
            bool: True or False
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)
        self.port = port
        self.server = server
        self.instrument_conversion_list = instrument_lookup
        self.authorization_code = authorization_code

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

        self.command = 'F000^1^'
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        try:
            if (ok == False):
                self.command_OK = False
                return False

            x = dataString.split('^')

            if x[1] == 'OK':
                self.timeout = True
                self.command_OK = True
                return True
            else:
                self.timeout = False
                self.command_return_error = ERROR_DICT['99900']
                self.command_OK = True
                return False
        except:
            self.command_return_error = ERROR_DICT['00001']
            self.command_OK = False
            return False
    
    def Check_terminal_server_connection(self) -> bool:
        """
        Checks if MT4/5 terminal connected to broker.
        Args:
            None
        Returns:
            bool: True or False
        """

        self.command = 'F011^1^'
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        try:
            if (ok == False):
                self.command_OK = False
                return False

            x = dataString.split('^')

            if x[2] == 'OK':
                self.timeout = False
                self.command_OK = True
                return True
            else:
                self.timeout = False
                self.command_return_error = ERROR_DICT['99900']
                self.command_OK = True
                return False
        except:
            self.command_return_error = ERROR_DICT['01101']
            self.command_OK = False
            return False
        
    def Check_terminal_type(self) -> str:
        """
        Checks for MT4 or MT5 terminal.
        Args:
            None
        Returns:
            string: if function for MT4 terminal answer would be 'MT4', for MT5 terminal 'MT5'
                    
        """

        self.command = 'F012^1^'
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        try:
            if (ok == False):
                self.command_OK = False
                return False

            x = dataString.split('^')

            if x[3] == 'MT4':
                self.timeout = False
                self.command_OK = True
                return 'MT4'
            elif x[3] == 'MT5':
                self.timeout = False
                self.command_OK = True
                return 'MT5'
            else:
                self.timeout = False
                self.command_return_error = ERROR_DICT['99900']
                self.command_OK = True
                return False
        except:
            self.command_return_error = ERROR_DICT['01201']
            self.command_OK = False
            return False

    @property
    def IsConnected(self) -> bool:
        """Returns connection status.
        Returns:
            bool: True or False
        """
        return self.connected

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
            Account company
        """
        self.command_return_error = ''

        ok, dataString = self.send_command('F001^1^')
        if (ok == False):
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if x[0] != 'F001':
            self.command_return_error = ERROR_DICT['99900']
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
        returnDict['company'] = str(x[9])

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

        ok, dataString = self.send_command('F002^1^')
        if (ok == False):
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if x[0] != 'F002':
            self.command_return_error = ERROR_DICT['99900']
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

    def Check_license(self) -> bool:

        """
            Check for license.

            Returns:
                bool: True or False. True=licensed, False=Demo
        """
        self.license = 'Demo'
        self.command = 'F006^1^'
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if x[0] != 'F006':
            self.command_return_error = ERROR_DICT['99901']
            self.command_OK = False
            return None        

        self.license = str(x[3])
        if (self.license == 'Demo'):
            return False
        
        return True

    def Check_trading_allowed(self,
                                instrument = 'EURUSD') -> bool:

        """
            Check for trading allowed for specified symbol.

            Returns:
                bool: True or False. True=allowed, False=not allowed
        """

        self.command = 'F008^2^' + instrument + '^'
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if x[0] != 'F008':
            self.command_return_error = ERROR_DICT['99901']
            self.command_OK = False
            return None        

        if (str(x[2]) == 'NOK'):
            return False
       
        return True

    def Set_bar_date_asc_desc(self,
                                asc_desc: bool = False) -> bool:
        """
            Sets first row of array as first bar or as last bar
            In MT4/5 element[0] of an array is normaliter actual bar/candle
            Depending on the math you want to apply, this has to be the opposite
            Args:
                asc_dec:    True = row[0] is oldest bar
                            False = row[0] is latest bar
            Returns:
                bool: True or False
        """ 
        self.invert_array = asc_desc
        return True

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
            return pd.DataFrame()

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
            stop_level for sl and tp distance
        """

        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none' or self.instrument == None):
            self.command_return_error = 'Instrument not in broker list'
            self.command_OK = False
            return None


        self.command = 'F003^2^' + self.instrument + '^'

        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if x[0] != 'F003':
            self.command_return_error = ERROR_DICT[str(x[3])]
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
        returnDict['stop_level'] = int(x[9])

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
        if (self.instrument == 'none' or self.instrument == None):
            self.command_return_error = 'Instrument not in list'
            self.command_OK = False
            return None

        self.command = 'F004^2^' + self.instrument + '^'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return False, 'Error'

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if x[0] != 'F004':
            self.command_return_error = ERROR_DICT[str(x[3])]
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

        self.command = 'F007^2^'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        # analyze the answer
        return_list = []
        x = dataString.split('^')
        if x[0] != 'F007':
            self.command_return_error = ERROR_DICT[x[3]]
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
        self.command = 'F005^1^'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if x[0] != 'F005':
            self.command_return_error = ERROR_DICT[x[3]]
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
            last deal price,
            volume
            spread, in points
            date_in_ms
        """
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none' or self.instrument == None):
            self.command_return_error = 'Instrument not in broker list'
            self.command_OK = False
            return None
        ok, dataString = self.send_command('F020^2^' + self.instrument + '^')

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if x[0] != 'F020':
            self.command_return_error = ERROR_DICT[str(x[3])]
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
        returnDict['spread'] = float(x[5])
        returnDict['date_in_ms'] = int(x[6])

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
        if (self.instrument == 'none' or self.instrument == None):
            self.command_return_error = 'Instrument not in broker list'
            self.command_OK = False
            return None
        
        self.nbrofticks = nbrofticks

        dt = np.dtype([('date', np.int64), ('ask', np.float64), ('bid', np.float64), ('last', np.float64), ('volume', np.int32)])

        ticks = np.zeros(nbrofticks, dtype=dt)

        if (self.nbrofticks > self.max_ticks):
            iloop = self.nbrofticks // self.max_ticks
            itail = self.nbrofticks % self.max_ticks

            for index in range(0, iloop):
                self.command = 'F021^4^' + self.instrument + '^' + str(index * self.max_ticks) + '^' + str(self.max_ticks) + '^'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('^')
                if str(x[0]) != 'F021':
                    self.command_return_error = ERROR_DICT[str(x[3])]
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
                    ticks = np.sort(ticks[ticks[:]['date']!=0])
                    self.command_OK = True
                    if (self.invert_array == True):
                        ticks = np.flipud(ticks)
                    return ticks

            if (itail == 0):
                ticks = np.sort(ticks[ticks[:]['date']!=0])
                self.command_OK = True
                return ticks

            if (itail > 0):
                self.command = 'F021^4^' + self.instrument + '^' + str(iloop * self.max_ticks) + '^' + str(itail) + '^'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('^')
                if str(x[0]) != 'F021':
                    self.command_return_error = ERROR_DICT[str(x[3])]
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
                ticks = np.sort(ticks[ticks[:]['date']!=0])
                if (self.invert_array == True):
                    ticks = np.flipud(ticks)
                return ticks
        else:
            self.command = 'F021^4^' + self.instrument + '^' + str(0) + '^' + str(self.nbrofticks) + '^'
            ok, dataString = self.send_command(self.command)

            if not ok:
                self.command_OK = False
                return None
            if self.debug:
                print(dataString)
                print('')
                print(len(dataString))

            x = dataString.split('^')
            if str(x[0]) != 'F021':
                self.command_return_error = ERROR_DICT[str(x[3])]
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
        ticks = np.sort(ticks[ticks[:]['date']!=0])
        if (self.invert_array == True):
            ticks = np.flipud(ticks)
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
        if (self.instrument == 'none'  or self.instrument == None):
            self.command_return_error = 'Instrument not in broker list'
            self.command_OK = False
            return None
        self.command = 'F041^3^' + self.instrument + '^' + str(timeframe) + '^'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F041':
            self.command_return_error = ERROR_DICT[str(x[3])]
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
        self.command = 'F045^3^'
        for index in range (0, len(instrument_list), 1):
            _instr = self.get_broker_instrument_name(instrument_list[index].upper())
            if (self.instrument == 'none'  or self.instrument == None):
                self.command_return_error = 'Instrument not in broker list'
                self.command_OK = False
                return None
            self.command = self.command + _instr + '$'
        
        self.command = self.command + '^' + str(specific_bar_index) + '^' + str(timeframe) + '^'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('^')
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
        if (self.instrument == 'none'  or self.instrument == None):
            self.command_return_error = 'Instrument not in broker list'
            self.command_OK = False
            return None
        self.numberofbars = nbrofbars

        dt = np.dtype([('date', np.int64), ('open', np.float64), ('high', np.float64),
                       ('low', np.float64), ('close', np.float64), ('volume', np.int32)])

        rates = np.zeros(self.numberofbars, dtype=dt)

        if (self.numberofbars > self.max_bars):
            iloop = self.numberofbars // self.max_bars
            itail = self.numberofbars % self.max_bars


            for index in range(0, iloop):
                self.command = 'F042^5^' + self.instrument + '^' + \
                        str(timeframe) + '^' + str(index * self.max_bars) + '^' + str(self.max_bars) + '^'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('^')
                if str(x[0]) != 'F042':
                    self.command_return_error = ERROR_DICT[str(x[3])]
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
                    if (self.invert_array == True):
                        rates = np.flipud(rates)
                    return rates

            if (itail == 0):
                #rates = np.sort(rates)
                rates = np.sort(rates[rates[:]['date']!=0])
                self.command_OK = True
                if (self.invert_array == True):
                    rates = np.flipud(rates)
                return rates

            if (itail > 0):
                self.command = 'F042^5^' + self.instrument + '^' + str(timeframe) + '^' + str(
                    iloop * self.max_bars) + '^' + str(itail) + '^'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('^')
                if str(x[0]) != 'F042':
                    self.command_return_error = ERROR_DICT[str(x[3])]
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
                    rates = np.flipud(rates)
                return rates
        else:
            self.command = 'F042^5^' + str(self.instrument) + '^' + \
                    str(timeframe) + '^' + str(0) + '^' + str(self.numberofbars) + '^'
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

            x = dataString.split('^')
            if str(x[0]) != 'F042':
                self.command_return_error = ERROR_DICT[str(x[3])]
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
        rates = np.sort(rates[rates[:]['date']!=0])
        if (self.invert_array == True):
            rates = np.flipud(rates)
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
        ok, resp = self.send_command("F065^1^")

        if self.debug:
            print(resp)

        if ok==True and resp[0:5]=="F065^" and resp[-1]=="!":
            nbr = resp[resp.index('^',3)+1:resp.index('^',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('^',5)+1:-1]), sep='$', lineterminator='^',
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
                x = resp.split('^')
                self.command_return_error = ERROR_DICT['99901']
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
        self.command = 'F064^3^' + self.date_from.strftime(
            '%Y/%m/%d/%H/%M/%S') + '^' + self.date_to.strftime('%Y/%m/%d/%H/%M/%S') + '^'
        ok, resp = self.send_command(self.command)

        if self.debug:
            print(resp)

        if ok==True and resp[0:5]=="F064^" and resp[-1]=="!":
            nbr = resp[resp.index('^',3)+1:resp.index('^',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('^',5)+1:-1]), sep='$', lineterminator='^',
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
                x = resp.split('^')
                self.command_return_error = ERROR_DICT[str(x[3])]
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
        ok, resp = self.send_command("F060^1^")

        if self.debug:
            print(resp)
        
        if ok==True and resp[0:5]=="F060^" and resp[-1]=="!":
            nbr = resp[resp.index('^',3)+1:resp.index('^',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('^',5)+1:-1]), sep='$', lineterminator='^',
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
                x = resp.split('^')
                self.command_return_error = ERROR_DICT['99901']
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
        self.command = 'F061^1^'

        # get all open positions
        ok, resp = self.send_command(self.command)

        if self.debug:
            print(resp)

        if ok==True and resp[0:5]=="F061^" and resp[-1]=="!":
            nbr = resp[resp.index('^',3)+1:resp.index('^',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('^',5)+1:-1]), sep='$', lineterminator='^',
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
                x = resp.split('^')
                self.command_return_error = ERROR_DICT['99901']
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
        self.command = 'F062^3^' + self.date_from.strftime(
            '%Y/%m/%d/%H/%M/%S') + '^' + self.date_to.strftime('%Y/%m/%d/%H/%M/%S') + '^'
        
        
        ok, resp = self.send_command(self.command)

        if self.debug:
            print(resp)

        if not ok:
            self.command_OK = False
            return None

        if ok==True and resp[0:5]=="F062^" and resp[-1]=="!":
            nbr = resp[resp.index('^',3)+1:resp.index('^',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('^',5)+1:-1]), sep='$', lineterminator='^',
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
                x = resp.split('^')
                self.command_return_error = ERROR_DICT['99901']
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

        self.command = 'F063^1^'
        ok, resp = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(resp)

        if ok==True and resp[0:5]=="F063^" and resp[-1]=="!":
            nbr = resp[resp.index('^',3)+1:resp.index('^',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('^',5)+1:-1]), sep='$', lineterminator='^',
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
                x = resp.split('^')
                self.command_return_error = ERROR_DICT['99901']
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
        # check the command for '^' , '$', '!' character
        # these are not allowed, used as delimiters
        comment.replace('^', '')
        comment.replace('$', '')
        comment.replace('!', '')
        broker_instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none' or self.instrument == None):
            self.command_return_error = 'Instrument not known, check brookerlookuptable'
            self.command_OK = False
            self.order_return_message = 'Instrument not known, check brookerlookuptable'
            return int(-1)
        
        self.command = 'F070^11^' + self.get_broker_instrument_name(self.instrument_name_universal) + '^' + ordertype + '^' + str(volume) + '^' + \
            str(openprice) + '^' + str(slippage) + '^' + str(magicnumber) + '^' + str(stoploss) + '^' + str(takeprofit) + '^' + str(comment) + '^' + str(market) + '^'
        #print(self.command)
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return int(-1)

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F070':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
            return int(-1)

        self.command_OK = True

        if (int(x[1]) == 3):
            self.order_return_message = str(x[2])
            return int(x[3])

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
        self.command = 'F071^2^' + str(ticket) + '^'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F071':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
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
        self.command = 'F072^3^' + \
            str(ticket) + '^' + str(volume_to_close) + '^'

        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F072':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            #self.order_error = ERROR_DICT[str(x[3])]
            return False

        return True

    def Close_positions_async(self,
                              instrument: str = '***',
                              magic_number: int = -1) -> bool:

        """
        Close a position.

        Args:
            instrument: close only positions with this instrument, default all (***)
            magic_number: close only positions with this magic number, default all (-1)

        Returns:
            bool: True or False
        """
        self.magicNumber = magic_number
        self.command_return_error = ''
        
        if (instrument == '***'):
            self.command = 'F091^3^' + str(instrument) + '^' + str(magic_number) + '^'
        else:
            self.instrument_name_universal = instrument
            self.command = 'F091^3^' + str(self.get_broker_instrument_name(self.instrument_name_universal)) + '^' + str(magic_number) + '^'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F091':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
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
        self.command = 'F073^2^' + str(ticket) + '^'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F073':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
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
        self.command = 'F075^4^' + \
            str(ticket) + '^' + str(stoploss) + '^' + str(takeprofit) + '^'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F075':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
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
        self.command = 'F076^4^' + \
            str(ticket) + '^' + str(stoploss) + '^' + str(takeprofit) + '^'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F076':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
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
        self.command = 'F077^2^' + str(ticket) + '^' 
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F077':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
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
        self.command = 'F078^2^' + str(ticket) + '^'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F078':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
            return False

        self.command_OK = True
        return True

    def Change_settings_for_pending_order(self,
                                ticket: int = 0,
                                price: float = -1.0,
                                stoploss: float = -1.0,
                                takeprofit: float = -1.0) -> bool:
        """
        Change settings for a pending order.
        
        Args:
            ticket: ticket of order to change
            price: new price value, if value=-1.0 no change
            stoploss: new stop loss value, if value=-1.0 no change
            takeprofit: new take profit value, if value=-1.0 no change
            
        Returns:
            bool: True or False
        
        """
        self.command_return_error = ''
        self.command = 'F079^5^' + str(ticket) + '^' + str(price) + '^' + str(stoploss) + '^' + str(takeprofit) + '^'
        
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)
            
        x = dataString.split('^')
        if str(x[0]) != 'F079':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
            return False

        self.command_OK = True
        return True
                
    def Set_global_variable(self, global_name: str = '', global_value: float = 0.0) -> bool:
        """
        Set global variable.

        Args:
            global_name: name of global variable
            global_value: value of global variable

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F080^3^' + global_name + '^' + str(global_value) + '^'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F080':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            #self.order_error = int(x[4])
            return False

        self.command_OK = True
        return True
    
    def Get_global_variable(self, global_name: str = 'GlobalVariableName') -> float:
        """
        Get global variable.

        Args:
            global_name: name of global variable

        Returns:
            value of global variable
        """
        
        self.command_return_error = ''
        self.command = 'F081^1^' + global_name  + '^'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False
        
        if self.debug:
            print(dataString)
            
        x = dataString.split('^')
        if str(x[0]) != 'F081':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            #self.order_error = int(x[4])
            return False

        self.command_OK = True
        return float(x[3])
        
    def Get_logfile(self, date: datetime = datetime.now()) -> pd.DataFrame():
        """
        Get logfile.

        Args:
            date: logfile date

        Returns:
            dataframe: logfile records
        """
        
        self.command_return_error = ''
        self.order_return_message = ''
        self.date_to = date
        self.command = 'F082^2^' + self.date_to.strftime('%Y/%m/%d/%H/%M/%S') + '^'
        ok, resp = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False
        
        if self.debug:
            print(resp)
            
        if ok==True and resp[0:5]=="F082^" and resp[-1]=="!":
            nbr = resp[resp.index('^',3)+1:resp.index('^',5)]
            if int(nbr) != 0:
                df = pd.read_table(io.StringIO(resp[resp.index('^',5)+1:-1]), sep='$', lineterminator='^',
                                header=None,
                                names=np.array(self.columnsLogInfo[1:])[:,0],
                                dtype=self.columnsLogInfo[1:]
                ).fillna('')
                # no time conversion

                return df
            else:
                # return empty dataframe
                return self.create_empty_DataFrame(
                        self.columnsLogInfo, 'id') 
            
        else:
            # error
            if not ok:
                self.command_OK = False
                return None
            else:
                x = resp.split('^')
                self.command_return_error = ERROR_DICT[str(x[3])]
                self.command_OK = False
                #self.order_return_message = ERROR_DICT[str(x[3])]
                #self.order_error = int(x[4])
                return None
    
    def Switch_autotrading_on_off(self, on_off: bool = True) -> bool:
        """
        Switch autotrading on or off.

        Args:
            on_off: True or False
        Returns:
            bool: True or False
        """
        
        self.command_return_error = ''
        if (on_off):
            self.command = 'F084^2^On^'
        else:
            self.command = 'F084^2^Off^'
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return False        
        x = dataString.split('^')
        if str(x[0]) != 'F084':
            return False
        else:
            return True	
    
    def send_command(self,
                     command):
        self.command = command + self.authorization_code + "^" "!"
        self.timeout = False
        #print(self.command)
        #print(self.socket)
        #self.sock.send(bytes(self.command, "utf-8"))
        try:
            self.sock.send(bytes(self.command, "utf-8"))
            data_received = ''
            while True:
                data_received = data_received + self.sock.recv(500000).decode()
                if data_received.endswith('!'):
                    break
            return True, data_received
        except socket.timeout as msg:
            self.timeout = True
            self.connected = False
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
    
    columnsLogInfo = [
        ('id', int),
        ('index', int),
        ('time', str),
        ('comment', str) ]
    


