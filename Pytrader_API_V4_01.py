
    

# Pytrader API for MT4 and MT5
# Version V3_02

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
ERROR_DICT['02002'] = 'Unknown instrument for broker'
ERROR_DICT['02003'] = 'Unknown instrument for broker'
ERROR_DICT['02004'] = 'Time out error'

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
ERROR_DICT['07009'] = 'Error opening / placing order'
ERROR_DICT['07011'] = 'Netting account, no opposite orders allowed'

ERROR_DICT['07101'] = 'Trading not allowed'
ERROR_DICT['07102'] = 'Position not found'

ERROR_DICT['07201'] = 'Trading not allowed'
ERROR_DICT['07202'] = 'Position not found'
ERROR_DICT['07203'] = 'Wrong volume'
ERROR_DICT['07204'] = 'Error in partial close'

ERROR_DICT['07301'] = 'Trading not allowed'
ERROR_DICT['07302'] = 'Error in delete'

ERROR_DICT['07401'] = 'Trading not allowed, check MT terminal settings'
ERROR_DICT['07402'] = 'Error check number'
ERROR_DICT['07403'] = 'Position not found'
ERROR_DICT['07404'] = 'Opposite position not found'
ERROR_DICT['07405'] = 'Both position of same type'

ERROR_DICT['07501'] = 'Trading not allowed'
ERROR_DICT['07502'] = 'Position not found' 
ERROR_DICT['07503'] = 'Invalid SL value'
ERROR_DICT['07504'] = 'Invalid TP value'
ERROR_DICT['07505'] = 'Probably SL or TP new value equals old value'

ERROR_DICT['07601'] = 'Trading not allowed'
ERROR_DICT['07602'] = 'Order not found' 
ERROR_DICT['07603'] = 'Invalid SL value'
ERROR_DICT['07604'] = 'Invalid TP value'
ERROR_DICT['07605'] = 'Probably SL or TP new value equals old value'

ERROR_DICT['07701'] = 'Trading not allowed'
ERROR_DICT['07702'] = 'Position not open' 
ERROR_DICT['07703'] = 'Error in modify'

ERROR_DICT['07801'] = 'Trading not allowed'
ERROR_DICT['07802'] = 'Position not open' 
ERROR_DICT['07803'] = 'Error in modify'

ERROR_DICT['07901'] = 'Trading not allowed'
ERROR_DICT['07902'] = 'Instrument not in demo'
ERROR_DICT['07903'] = 'Order not found' 
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
        """
        Initialize the Pytrader_API object.

        Attributes:
            socket_error (int): the error code for socket errors
            socket_error_message (str): the error message for socket errors
            order_return_message (str): the return message for orders
            order_error (int): the error code for order errors
            connected (bool): if the socket connection is established
            timeout (bool): if the socket connection timed out
            command_OK (bool): if the last command was OK
            command_return_error (str): the error message for the last command
            debug (bool): if debug mode is on
            version (str): the version of the API
            max_bars (int): the maximum number of bars that can be retrieved
            max_ticks (int): the maximum number of ticks that can be retrieved
            timeout_value (int): the time out value for socket communication
            instrument_conversion_list (dict): a dictionary with the instrument conversion list
            instrument_name_broker (str): the name of the instrument in the broker
            instrument_name_universal (str): the name of the instrument in the universal API
            date_from (datetime): the start date for retrieving data
            date_to (datetime): the end date for retrieving data
            instrument (str): the name of the instrument
            license (str): the license type
            invert_array (bool): if the array should be inverted
            authorization_code (str): the authorization code
        """
        self.socket_error: int = 0
        self.socket_error_message: str = ''
        self.order_return_message: str = ''
        self.order_error: int = 0
        self.connected: bool = False
        self.timeout: bool = False
        self.command_OK: bool = False
        self.command_return_error: str = ''
        self.debug: bool = False
        self.version: str = 'V4.01ca'
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
        Sets the timeout value for socket communication with an MT4 or MT5 EA/Bot.

        Args:
            timeout_in_seconds (int): The timeout duration in seconds.

        Returns:
            None
        """
        # Store the timeout value
        self.timeout_value = timeout_in_seconds
        
        # Set the socket's timeout to the specified value
        self.sock.settimeout(self.timeout_value)
        
        # Set the socket to blocking mode
        self.sock.setblocking(1)
        
        return

    def Disconnect(self):
        """
        Closes the socket connection to a MT4 or MT5 EA bot.

        This method closes the socket connection to a MT4 or MT5 EA bot.
        After this method is called, the socket connection is closed and the
        connection status is set to False.

        Args:
            None

        Returns:
            bool: True if the connection is closed, False otherwise
        """

        # Close the socket connection
        self.sock.close()
        
        # Set the connection status to False
        self.connected = False
        
        # Return True if the connection is closed
        return True

    def Connect(self,
                server: str = '',
                port: int = 2345,
                instrument_lookup: dict = [],
                authorization_code: str = 'None') -> bool:
        """
        Connects to a MT4 or MT5 EA/Bot.

        This method connects to a MT4 or MT5 EA/Bot. The connection is
        established by creating a socket object and connecting to the
        specified server and port. The method returns True if the
        connection is established, False otherwise.

        Args:
            server (str): The server IP address, like -> '127.0.0.1', '192.168.5.1'
            port (int): The port number
            instrument_lookup (dict): A dictionairy with general instrument names and broker intrument names
            authorization_code (str): The authorization code, this can be used as extra security. The code has also to be set in the EA's
        Returns:
            bool: True or False
        """
        # Create a socket object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set the socket to blocking mode
        self.sock.setblocking(1)

        # Store the port number
        self.port = port

        # Store the server IP address
        self.server = server

        # Store the instrument conversion list
        self.instrument_conversion_list = instrument_lookup

        # Store the authorization code
        self.authorization_code = authorization_code

        # Check if the instrument conversion list is empty
        if (len(self.instrument_conversion_list) == 0):
            print('Broker Instrument list not available or empty')
            self.socket_error_message = 'Broker Instrument list not available'
            return False

        try:
            # Connect to the server
            self.sock.connect((self.server, self.port))

            try:
                # Receive data from the server
                data_received = self.sock.recv(1000000)

                # Set the connection status to True
                self.connected = True

                # Set the socket error to 0
                self.socket_error = 0

                # Set the socket error message to empty
                self.socket_error_message = ''

                # Return True if the connection is established
                return True
            except socket.error as msg:
                # Set the socket error to 100 if the connection could not be established
                self.socket_error = 100

                # Set the socket error message
                self.socket_error_message = 'Could not connect to server.'

                # Set the connection status to False
                self.connected = False

                # Return False if the connection could not be established
                return False
        except socket.error as msg:
            # Print an error message if the connection could not be established
            print(
                "Couldnt connect with the socket-server: %self.sock\n terminating program" %
                msg)
            # Set the connection status to False
            self.connected = False

            # Set the socket error to 101
            self.socket_error = 101

            # Set the socket error message
            self.socket_error_message = 'Could not connect to server.'

            # Return False if the connection could not be established
            return False

    def Check_connection(self) -> bool:
        """
        Checks if connection with MT terminal/Ea bot is still active.
        This function can be used to check if the connection with the EA is still active.
        Args:
            None
        Returns:
            bool: True if connection is active, False otherwise
        """

        # Set the command to check if the connection with the MT terminal/Ea bot is still active
        self.command = 'F000^1^'

        # Initialize the command return error
        self.command_return_error = ''

        # Send the command to the EA
        ok, dataString = self.send_command(self.command)

        try:
            # Check if the command is OK
            if (ok == False):
                # If the command is not OK, set the command_OK to False and return False
                self.command_OK = False
                return False

            # Split the data received into parts
            x = dataString.split('^')

            # Check if the connection is active
            if x[1] == 'OK':
                # If the connection is active, set the timeout to False, set the command_OK to True and return True
                self.timeout = False
                self.command_OK = True
                return True
            else:
                # If the connection is not active, set the timeout to True, set the error message and return False
                self.timeout = True
                self.command_return_error = ERROR_DICT['99900']
                self.command_OK = True
                return False
        except:
            # If an error occurs, set the error message, set the command_OK to False and return False
            self.command_return_error = ERROR_DICT['00001']
            self.command_OK = False
            return False
    
    def Check_terminal_server_connection(self) -> bool:
        """
        Checks if MT4/5 terminal connected to broker.
        This function checks if the MT4/5 terminal is connected to the broker.
        Args:
            None
        Returns:
            bool: True if connected, False otherwise
        """

        # Set the command to check if the terminal is connected to the broker
        self.command = 'F011^1^'

        # Initialize the command return error
        self.command_return_error = ''

        # Send the command to the EA
        ok, dataString = self.send_command(self.command)

        try:
            # Check if the command is OK
            if (ok == False):
                # If the command is not OK, set the command_OK to False and return False
                self.command_OK = False
                return False

            # Split the data received into parts
            x = dataString.split('^')

            # Check if the terminal is connected to the broker
            if x[2] == 'OK':
                # If the terminal is connected, set the timeout to False and return True
                self.timeout = False
                self.command_OK = True
                return True
            else:
                # If the terminal is not connected, set the timeout to False, set the error message and return False
                self.timeout = False
                self.command_return_error = ERROR_DICT['99900']
                self.command_OK = True
                return False
        except:
            # If an error occurs, set the error message and return False
            self.command_return_error = ERROR_DICT['01101']
            self.command_OK = False
            return False
        
    def Check_terminal_type(self) -> str:
        """
        Checks for MT4 or MT5 terminal.
        This function will check whether the terminal is MT4 or MT5.
        Args:
            None
        Returns:
            string: if function for MT4 terminal answer would be 'MT4', for MT5 terminal 'MT5'
        """

        # Set the command to check the terminal type
        self.command = 'F012^1^'

        # Initialize the command return error
        self.command_return_error = ''

        # Send the command to the EA
        ok, dataString = self.send_command(self.command)

        try:
            # Check if the command is OK
            if (ok == False):
                # If the command is not OK, set the command_OK to False and return False
                self.command_OK = False
                return False

            # Split the data received into parts
            x = dataString.split('^')

            # Check if the terminal is MT4 or MT5
            if x[3] == 'MT4':
                # If the terminal is MT4, set the timeout to False and return 'MT4'
                self.timeout = False
                self.command_OK = True
                return 'MT4'
            elif x[3] == 'MT5':
                # If the terminal is MT5, set the timeout to False and return 'MT5'
                self.timeout = False
                self.command_OK = True
                return 'MT5'
            else:
                # If the terminal type is unknown, set the timeout to False, set the error message and return False
                self.timeout = False
                self.command_return_error = ERROR_DICT['99900']
                self.command_OK = True
                return False
        except:
            # If an error occurs, set the error message and return False
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
        Retrieves static account information from MetaTrader 5.

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

        If the command fails, returns None.
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

        # Create a dictionary to store the information
        returnDict = {}
        del x[0:2]
        x.pop(-1)

        # Add the information to the dictionary
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
        # Reset the command return error
        self.command_return_error = ''

        # Send the command
        ok, dataString = self.send_command('F002^1^')
        if (ok == False):
            # If the command fails, set the command_OK flag to False
            self.command_OK = False
            return None

        if self.debug:
            # Print the data string if in debug mode
            print(dataString)

        # Split the data string
        x = dataString.split('^')
        if x[0] != 'F002':
            # If the command fails, set the command return error
            self.command_return_error = ERROR_DICT['99900']
            self.command_OK = False
            return None

        # Create a dictionary to store the information
        returnDict = {}

        # Delete the first two elements of the list and the last element
        del x[0:2]
        x.pop(-1)

        # Add the information to the dictionary
        returnDict['balance'] = float(x[0])
        returnDict['equity'] = float(x[1])
        returnDict['profit'] = float(x[2])
        returnDict['margin'] = float(x[3])
        returnDict['margin_level'] = float(x[4])
        returnDict['margin_free'] = float(x[5])

        # Set the command_OK flag to True
        self.command_OK = True

        # Return the dictionary
        return returnDict

    def Check_license(self) -> bool:
        """
        Checks for a valid license.

        This function sends a command to check the license status and returns
        whether the license is valid or if it's a demo.

        Returns:
            bool: True if licensed, False if Demo.
        """
        # Set initial license status to 'Demo'
        self.license = 'Demo'

        # Create the command to check the license
        self.command = 'F006^1^'

        # Initialize the command return error
        self.command_return_error = ''

        # Send the command to check the license
        ok, dataString = self.send_command(self.command)

        # If the command fails, set command_OK to False and return None
        if not ok:
            self.command_OK = False
            return None

        # Print the data string if in debug mode
        if self.debug:
            print(dataString)

        # Split the data string into components
        x = dataString.split('^')

        # Verify the command response
        if x[0] != 'F006':
            # Set error message and command_OK flag if response is incorrect
            self.command_return_error = ERROR_DICT['99901']
            self.command_OK = False
            return None        

        # Update license status based on response
        self.license = str(x[3])

        # Return False if license is 'Demo', otherwise return True
        if self.license == 'Demo':
            return False
        
        return True

    def Check_trading_allowed(self,
                                instrument: str = 'EURUSD') -> bool:
        """
            Check for trading allowed for specified symbol.
            Args:
                instrument: Instrument to check

            Returns:
                bool: True or False. True=allowed, False=not allowed
        """
        # Get the broker instrument name
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)

        # Create the command to check for trading allowed
        self.command = 'F008^2^' + self.instrument + '^'

        # Initialize the command return error
        self.command_return_error = ''

        # Send the command to check for trading allowed
        ok, dataString = self.send_command(self.command)

        # If the command fails, set command_OK to False and return None
        if not ok:
            self.command_OK = False
            return None

        # Print the data string if in debug mode
        if self.debug:
            print(dataString)

        # Split the data string into components
        x = dataString.split('^')

        # Verify the command response
        if x[0] != 'F008':
            # Set error message and command_OK flag if response is incorrect
            self.command_return_error = ERROR_DICT['99901']
            self.command_OK = False
            return None        

        # Return False if trading is not allowed, otherwise return True
        if (str(x[2]) == 'NOK'):
            return False
       
        return True

    def Set_bar_date_asc_desc(self,
                                asc_desc: bool = False) -> bool:
        """
            Sets first row of array as first bar or as last bar

            In MT4/5 element[0] of an array is normally the actual bar/candle.
            Depending on the math you want to apply, this has to be the opposite.

            Args:
                asc_dec:    True = row[0] is oldest bar
                            False = row[0] is latest bar

            Returns:
                bool: True or False
        """

        # Set the invert_array attribute to the passed value
        self.invert_array = asc_desc

        # Return True to indicate success
        return True

    def Get_PnL(self,
                    date_from: datetime = datetime(2021, 3, 1, tzinfo = pytz.timezone("Etc/UTC")),
                    date_to: datetime = datetime.now()) -> pd.DataFrame:
        """
        Retrieves profit loss info.

        Args:
            date_from (datetime): start date
            date_to (datetime): end date

        Returns:
            pd.DataFrame: DataFrame with:
                realized_profit             profit of all closed positions
                unrealized_profit           profit of all open positions
                buy_profit                  profit of closed buy positions
                sell_profit                 profit of closed sell positions
                positions_in_profit         number of profit positions
                positions in loss           number of loss positions
                volume_in_profit            total volume of positions in profit
                volume_in_loss              total volume of positions in loss
        """
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

            return pd.DataFrame([result])
        else:
            return pd.DataFrame()

    def Get_instrument_info(self,
                            instrument: str = 'EURUSD') -> dict:
        """
        Retrieves instrument information.

        Args:
            instrument (str): instrument name

        Returns:
            dict: Dictionary with:
                instrument (str): instrument name
                digits (int): number of decimal places
                max_lotsize (float): maximum lot size
                min_lotsize (float): minimum lot size
                lot_step (float): step size for lot size
                point (float): point value
                tick_size (float): tick size
                tick_value (float): tick value
                swap_long (float): swap value for long positions
                swap_short (float): swap value for short positions
                stop_level (int): stop level for SL and TP distance
                contract_size (float): contract size
        """

        # Initialize the command return error
        self.command_return_error = ''

        # Convert the instrument name to uppercase and get the broker instrument name
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)

        # Check if the instrument is in the broker list
        if (self.instrument == 'none' or self.instrument is None):
            self.command_return_error = 'Instrument not in broker list'
            self.command_OK = False
            return None

        # Create the command to retrieve instrument info
        self.command = 'F003^2^' + self.instrument + '^'

        # Send the command and get the response
        ok, dataString = self.send_command(self.command)

        # If the command fails, set command_OK to False and return None
        if not ok:
            self.command_OK = False
            return None

        # Print the data string if in debug mode
        if self.debug:
            print(dataString)

        # Split the data string into components
        x = dataString.split('^')

        # Verify the command response
        if x[0] != 'F003':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return None

        # Create a dictionary to store the results
        returnDict = {}
        del x[0:2]  # Remove command identifier and redundant info
        x.pop(-1)   # Remove trailing empty element

        # Populate the dictionary with instrument information
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
        returnDict['contract_size'] = float(x[10])

        # Set the command_OK flag to True
        self.command_OK = True

        # Return the dictionary with instrument information
        return returnDict

    def Check_instrument(self,
                         instrument: str = 'EURUSD') -> str:
        """
        Check if instrument known / market watch at broker.

        Args:
            instrument: instrument name
        Returns:
            tuple: (bool, str)
        """
        # Set the instrument name to the universal name
        self.instrument_name_universal = instrument.upper()

        # Map the instrument name to the broker instrument name
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)

        # If the instrument is not in the broker list
        if (self.instrument == 'none' or self.instrument == None):
            # Set the error message
            self.command_return_error = 'Instrument not in list'
            # Set the command status to False
            self.command_OK = False
            # Return False and the error message
            return False, 'Instrument not in list'

        # Build the command string
        self.command = 'F004^2^' + self.instrument + '^'

        # Send the command and get the response
        ok, dataString = self.send_command(self.command)

        # If something went wrong
        if not ok:
            # Set the command status to False
            self.command_OK = False
            # Return False and the error message
            return False, 'Error'

        # If the debug flag is set
        if self.debug:
            # Print the response string
            print(dataString)

        # Split the response string into a list
        x = dataString.split('^')
        # If the command was not successful
        if x[0] != 'F004':
            # Set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            # Set the command status to False
            self.command_OK = False
            # Return False and the error message
            return False, str(x[2])

        # Everything went well
        # Return True and the result
        return True, str(x[2])

    def Get_instruments(self) ->list:
        """
        Retrieves broker market instruments list, filtered by instrument list.

        Args:
            None
        Returns:
            List: All market symbols as universal instrument names
        """
        self.command_return_error = ''

        # Build the command string
        self.command = 'F007^2^'
        # Send the command and get the response
        ok, dataString = self.send_command(self.command)
        # If something went wrong
        if not ok:
            # Set the command status to False
            self.command_OK = False
            # Return None
            return None

        # If the debug flag is set
        if self.debug:
            # Print the response string
            print(dataString)

        return_list = []

        # Split the response string into a list
        x = dataString.split('^')
        # If the command was not successful
        if x[0] != 'F007':
            # Set the error message
            self.command_return_error = ERROR_DICT[x[3]]
            # Set the command status to False
            self.command_OK = False
            # Return None
            return return_list
        
        # Remove the first two items, which are the command and the result
        del x[0:2]
        # Remove the last item, which is the end of the string
        x.pop(-1)
        
        # Loop through the list
        for item in range(0, len(x)):
            # Get the instrument name
            _instrument = str(x[item])
            # Get the universal instrument name
            instrument = self.get_universal_instrument_name(_instrument)
            # If the universal instrument name is valid
            if (instrument != None):
                # Add it to the list
                return_list.append(instrument)
        # Return the list
        return return_list

    def Get_broker_instrument_names(self) -> list:
        """
        Retrieves broker instrument names in Market Watch, so not the universal names.

        Returns:
            List: All market symbols as broker instrument names in Market Watch
        """
        self.command_return_error = ''

        return_list = []

        # Build the command string
        self.command = 'F007^2^'
        # Send the command and get the response
        ok, dataString = self.send_command(self.command)
        # If the command failed
        if not ok:
            # Set the command status to False
            self.command_OK = False
            # Return None
            return None

        # If the debug flag is set
        if self.debug:
            # Print the response string
            print(dataString)

        # Split the response string into a list
        x = dataString.split('^')
        # If the command was not successful
        if x[0] != 'F007':
            # Set the error message
            self.command_return_error = ERROR_DICT[x[3]]
            # Set the command status to False
            self.command_OK = False
            # Return None
            return return_list
        
        # Remove the first two items, which are the command and the result
        del x[0:2]
        # Remove the last item, which is the end of the string
        x.pop(-1)
        # Loop through the list
        for item in range(0, len(x)):
            # Get the instrument name
            _instrument = str(x[item])
            # Add it to the list
            return_list.append(_instrument)
        # Return the list
        return return_list
       
    def Get_broker_server_time(self) -> datetime:
        """
        Retrieves broker server time.

        Args:
            None
        Returns:
            datetime: Broker time
        """
        # Reset/set parameters
        self.command_return_error = ''
        self.command = 'F005^1^'
        ok, dataString = self.send_command(self.command)

        if not ok:
            # If the command failed, return None
            self.command_OK = False
            return None

        # Print the response
        if self.debug:
            print(dataString)

        # Split the response into a list of strings
        x = dataString.split('^')
        if x[0] != 'F005':
            # If the response is not valid, return None
            self.command_return_error = ERROR_DICT[x[3]]
            self.command_OK = False
            return None

        # Remove the first two elements of the list
        del x[0:2]
        # Remove the last element of the list
        x.pop(-1)
        # Split the first element of the list into a list of strings
        y = x[0].split('-')
        # Create a datetime object from the list of strings
        d = datetime(int(y[0]), int(y[1]), int(y[2]),
                     int(y[3]), int(y[4]), int(y[5]))
        # Return the datetime object
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
        # Reset/set parameters
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none' or self.instrument == None):
            # If the instrument is not in the broker's list, return None
            self.command_return_error = 'Instrument not in broker list'
            self.command_OK = False
            return None
        ok, dataString = self.send_command('F020^2^' + self.instrument + '^')

        if not ok:
            # If the command failed, return None
            self.command_OK = False
            return None

        if self.debug:
            # Print the response
            print(dataString)

        # Split the response into a list of strings
        x = dataString.split('^')
        if x[0] != 'F020':
            # If the response is not valid, return None
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return None

        # Create a dictionary to store the tick data
        returnDict = {}
        # Remove the first two elements of the list
        del x[0:2]
        # Remove the last element of the list
        x.pop(-1)

        # Populate the dictionary with the tick data
        returnDict['instrument'] = str(self.instrument_name_universal)
        returnDict['date'] = int(x[0])
        returnDict['ask'] = float(x[1])
        returnDict['bid'] = float(x[2])
        returnDict['last'] = float(x[3])
        returnDict['volume'] = int(x[4])
        returnDict['spread'] = float(x[5])
        returnDict['date_in_ms'] = int(x[6])

        # Set the command status to True
        self.command_OK = True
        # Return the dictionary
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
        if (self.nbrofticks > self.max_ticks):
            self.nbrofticks = self.max_ticks

        dt = np.dtype([('date', np.int64), ('ask', np.float64), ('bid', np.float64), ('last', np.float64), ('volume', np.int32)])

        ticks = np.zeros(nbrofticks, dtype=dt)

        # If the number of ticks to retrieve is greater than the maximum number of ticks
        # that can be retrieved in one call (self.max_ticks), then loop to retrieve all of them
        if (self.nbrofticks > self.max_ticks):
            iloop = self.nbrofticks // self.max_ticks
            itail = self.nbrofticks % self.max_ticks

            # Loop to retrieve all of the ticks
            for index in range(0, iloop):
                # Create the command to retrieve the next set of ticks
                self.command = 'F021^4^' + self.instrument + '^' + str(index * self.max_ticks) + '^' + str(self.max_ticks) + '^'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                # Split the response into a list of strings
                x = dataString.split('^')
                if str(x[0]) != 'F021':
                    self.command_return_error = ERROR_DICT[str(x[3])]
                    self.command_OK = False
                    return None

                # Remove the first two elements of the list
                del x[0:2]
                # Remove the last element of the list
                x.pop(-1)

                # Loop through the list of strings
                for value in range(0, len(x)):
                    # Split each string into a list of strings
                    y = x[value].split('$')

                    # Populate the ticks array with the values
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

            # If there is a remainder, then retrieve the remaining ticks
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
            # If the number of ticks to retrieve is less than or equal to the maximum number of ticks
            # that can be retrieved in one call (self.max_ticks), then retrieve all of them
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
        return ticks

    def Get_actual_bar_info(self,
                            instrument: str = 'EURUSD',
                            timeframe: int = 16408) -> dict:
        """
        Retrieves instrument last actual data.

        Args:
            instrument (str): instrument name
            timeframe (int): time frame like H1, H4 converted into integer value

        Returns:
            dict: Dictionary with:
                instrument name (str),
                date (int),
                open (float),
                high (float),
                low (float),
                close (float),
                volume (int),
        """
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none'  or self.instrument == None):
            # If the instrument is not in the list of broker instruments
            self.command_return_error = 'Instrument not in broker list'
            self.command_OK = False
            return None
        self.command = 'F041^3^' + self.instrument + '^' + str(timeframe) + '^'
        ok, dataString = self.send_command(self.command)

        if not ok:
            # If the command was not successful
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('^')
        if str(x[0]) != 'F041':
            # If the command was not successful
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
        Retrieves instrument data (date, open, high, low, close, volume) of a specific bar
        for the given instruments.

        Args:
            instrument_list (list): List of instrument names.
            specific_bar_index (int): Index of the specific bar (0 = actual bar).
            timeframe (int): Timeframe like H1, H4.

        Returns:
            dict: Dictionary with instrument data for each instrument.
        """
        self.command_return_error = ''
        
        # Compose MT5 command string
        self.command = 'F045^3^'
        for index in range(len(instrument_list)):
            _instr = self.get_broker_instrument_name(instrument_list[index].upper())
            
            # Check if instrument is in broker list
            if _instr in ('none', None):
                self.command_return_error = 'Instrument not in broker list'
                self.command_OK = False
                return None
            
            self.command += _instr + '$'
        
        # Append specific bar index and timeframe to the command
        self.command += f'^{specific_bar_index}^{timeframe}^'
        
        # Send command and get response
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return None
        
        if self.debug:
            print(dataString)
        
        # Parse the response
        x = dataString.split('^')
        if x[0] != 'F045':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None
        
        del x[0:2]
        x.pop(-1)
        
        # Construct the result dictionary
        result = {}
        for value in range(len(x)):
            y = x[value].split('$')
            symbol_result = {
                'date': int(y[1]),
                'open': float(y[2]),
                'high': float(y[3]),
                'low': float(y[4]),
                'close': float(y[5]),
                'volume': float(y[6])
            }
            symbol = str(y[0])
            result[symbol] = symbol_result
        
        return result

    def Get_last_x_bars_from_now(self,
                                 instrument: str = 'EURUSD',
                                 timeframe: int = 16408,
                                 nbrofbars: int = 1000) -> np.array:
        """
        Retrieves the last x bars from a MT4 or MT5 EA bot.

        Args:
            instrument (str): Name of the instrument like EURUSD.
            timeframe (int): Timeframe like 'H4'.
            nbrofbars (int): Number of bars to retrieve.

        Returns:
            np.array: Numpy array with:
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

        # Check if the instrument is valid
        if self.instrument in ('none', None):
            self.command_return_error = 'Instrument not in broker list'
            self.command_OK = False
            return None

        self.numberofbars = nbrofbars

        # Define the data type for the rates array
        dt = np.dtype([('date', np.int64), ('open', np.float64), ('high', np.float64),
                       ('low', np.float64), ('close', np.float64), ('volume', np.int32)])

        # Initialize the rates array
        rates = np.zeros(self.numberofbars, dtype=dt)

        # If the number of bars to retrieve is greater than the maximum number of bars
        if self.numberofbars > self.max_bars:
            iloop = self.numberofbars // self.max_bars
            itail = self.numberofbars % self.max_bars

            # Loop to retrieve all of the bars
            for index in range(iloop):
                # Create the command to retrieve the next set of bars
                self.command = f'F042^5^{self.instrument}^{timeframe}^{index * self.max_bars}^{self.max_bars}^'
                ok, dataString = self.send_command(self.command)

                if not ok:
                    self.command_OK = False
                    return None

                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                # Split the response into a list of strings
                x = dataString.split('^')
                if x[0] != 'F042':
                    self.command_return_error = ERROR_DICT[str(x[3])]
                    self.command_OK = False
                    return None

                # Remove the first two elements and the last element of the list
                del x[0:2]
                x.pop(-1)

                # Loop through the list of strings
                for value in range(len(x)):
                    # Split each string into a list of strings
                    y = x[value].split('$')

                    # Populate the rates array with the values
                    rates[value + index * self.max_bars] = (int(y[0]), float(y[1]), float(y[2]),
                                                            float(y[3]), float(y[4]), int(y[5]))

                if len(x) < self.max_bars:
                    rates = np.sort(rates[rates[:]['date'] != 0])
                    self.command_OK = True
                    if self.invert_array:
                        rates = np.flipud(rates)
                    return rates

            if itail == 0:
                rates = np.sort(rates[rates[:]['date'] != 0])
                self.command_OK = True
                if self.invert_array:
                    rates = np.flipud(rates)
                return rates

            if itail > 0:
                # Create the command to retrieve the remaining bars
                self.command = f'F042^5^{self.instrument}^{timeframe}^{iloop * self.max_bars}^{itail}^'
                ok, dataString = self.send_command(self.command)

                if not ok:
                    self.command_OK = False
                    return None

                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                # Split the response into a list of strings
                x = dataString.split('^')
                if x[0] != 'F042':
                    self.command_return_error = ERROR_DICT[str(x[3])]
                    self.command_OK = False
                    return None

                # Remove the first two elements and the last element of the list
                del x[0:2]
                x.pop(-1)

                # Loop through the list of strings for remaining data
                for value in range(len(x)):
                    y = x[value].split('$')
                    rates[value + iloop * self.max_bars] = (int(y[0]), float(y[1]), float(y[2]),
                                                            float(y[3]), float(y[4]), int(y[5]))

                self.command_OK = True
                rates = np.sort(rates[rates[:]['date'] != 0])
                if self.invert_array:
                    rates = np.flipud(rates)
                return rates

        else:
            # Create the command to retrieve the bars if number of bars is less than max_bars
            self.command = f'F042^5^{self.instrument}^{timeframe}^{0}^{self.numberofbars}^'
            ok, dataString = self.send_command(self.command)

            if not ok:
                self.command_OK = False
                return None

            if self.debug:
                print(dataString)
                print('')
                print(len(dataString))

            # Split the response into a list of strings
            x = dataString.split('^')
            if x[0] != 'F042':
                self.command_return_error = ERROR_DICT[str(x[3])]
                self.command_OK = False
                return None

            # Remove the first two elements and the last element of the list
            del x[0:2]
            x.pop(-1)

            # Loop through the list of strings
            for value in range(len(x)):
                y = x[value].split('$')
                rates[value] = (int(y[0]), float(y[1]), float(y[2]), float(y[3]), float(y[4]), int(y[5]))

        self.command_OK = True
        rates = np.sort(rates[rates[:]['date'] != 0])
        if self.invert_array:
            rates = np.flipud(rates)
        return rates[:len(x)]

    # def Get_bars_from_date_to_date(self, 
    #                                 instrument: str = 'EURUSD',
    #                                 timeframe: int = 16408,
    #                                 date_from: datetime = datetime(2021, 3, 1, tzinfo = pytz.timezone("Etc/UTC")),
    #                                 date_to: datetime = datetime.now()) -> np.array:
    #     """
    #     Retrieves an array of bars from a specific date to another date.

    #     Args:
    #         instrument: name of instrument like EURUSD
    #         timeframe: time frame like H1, H4
    #         date_from: start date
    #         date_to: end date

    #     Returns: numpy array with:
    #         date,
    #         open,
    #         high,
    #         low,
    #         close,
    #         volume
    #     """
    #     self.command_return_error = ''
    #     self.instrument_name_universal = instrument.upper()
    #     self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
    #     if (self.instrument == 'none'  or self.instrument == None):
    #         self.command_return_error = 'Instrument not in broker list'
    #         self.command_OK = False
    #         return None
    #     self.date_from = date_from
    #     self.date_to = date_to

    #     if (date_from >= date_to):
    #         self.command_return_error = 'From date is after to date'
    #         self.command_OK = False
    #         return None
               

    #     # Create the data type for the array
    #     dt = np.dtype([('date', np.int64), ('open', np.float64), ('high', np.float64),
    #                    ('low', np.float64), ('close', np.float64), ('volume', np.int32)])

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

        if not ok:
            self.command_OK = False
            return None

        # create empty DataFrame with columns
        deleted_orders = self.create_empty_DataFrame(
            self.columnsDeletedOrders, 'id')
        
        # split the response into a list of strings
        x = resp.split('^')

        # check if the response is correct
        if (str(x[0]) != 'F065'):
            self.command_return_error = ERROR_DICT['99901']
            self.command_OK = False
            return None

        # remove the first two elements and the last element of the list
        del x[0:2]
        x.pop(-1)

        # loop through the list of strings
        for value in range(0, len(x)):
            # split the string into a list of strings
            y = x[value].split('$')

            # create a dictionary with the columns and the values
            rowOrder = {
                    'ticket': int( y[0]), 
                    'instrument': self.get_universal_instrument_name( (y[1])),  # convert broker instrument name to universal instrument name
                    'order_type': str( y[2]),
                    'magic_number': int(y[3]), 
                    'volume': float( y[4]), 
                    'open_price': float( y[5]), 
                    'open_time': int(y[6]),
                    'stop_loss': float( y[7]), 
                    'take_profit': float( y[8]), 
                    'delete_price': float(y[9]), 
                    'delete_time': int( y[10]), 
                    'comment': str( y[11])
            }

            # create a DataFrame with one row
            df_add = pd.DataFrame([rowOrder])

            # concatenate the DataFrame with the existing DataFrame
            deleted_orders = pd.concat([deleted_orders, df_add], ignore_index=True)

        # sort the DataFrame by open_time ascending
        deleted_orders.sort_values(by=['open_time'], ascending= True,inplace=True)

        # set the command_OK to True
        self.command_OK = True

        # return the DataFrame
        return deleted_orders

    def Get_deleted_orders_within_window(self,
                                         date_from: datetime = datetime(2021, 3, 25, tzinfo=pytz.timezone("Etc/UTC")),
                                         date_to: datetime = datetime.now()) -> pd.DataFrame:
        """ 
        Retrieves all deleted pending orders within a specified time window.
        The open and close time of the order must be within the time window.

        Args:
            date_from (datetime): Date to start retrieving orders from.
            date_to (datetime): Date to stop retrieving orders to.

        Returns:
            pd.DataFrame: DataFrame containing all position information:
                - ticket
                - instrument
                - order_type
                - magic_number
                - volume
                - open_price
                - open_time
                - stop_loss
                - take_profit
                - delete_price
                - delete_time
                - comment
        """
        
        # Reset/set parameters
        self.command_return_error = ''
        self.date_from = date_from
        self.date_to = date_to

        # Construct the command to get all pending orders within the date range
        self.command = 'F064^3^' + self.date_from.strftime('%Y/%m/%d/%H/%M/%S') + '^' + self.date_to.strftime('%Y/%m/%d/%H/%M/%S') + '^'
        ok, resp = self.send_command(self.command)

        # Debugging: print the response if debug mode is on
        if self.debug:
            print(resp)

        # If command fails, set the command_ok flag to False and return None
        if not ok:
            self.command_OK = False
            return None

        # Create an empty DataFrame to store deleted orders
        deleted_orders = self.create_empty_DataFrame(self.columnsDeletedOrders, 'id')
        
        # Split the response to process the data
        x = resp.split('^')
        
        # Verify the response format
        if str(x[0]) != 'F064':
            self.command_return_error = ERROR_DICT['99901']
            self.command_OK = False
            return None

        # Remove unnecessary parts of the response
        del x[0:2]
        x.pop(-1)

        # Process each entry in the response
        for value in range(len(x)):
            y = x[value].split('$')

            # Create a dictionary for each order
            rowOrder = {
                    'ticket': int( y[0]), 
                    'instrument': self.get_universal_instrument_name( (y[1])),  
                    'order_type': str( y[2]),
                    'magic_number': int(y[3]), 
                    'volume': float( y[4]), 
                    'open_price': float( y[5]), 
                    'open_time': int(y[6]),
                    'stop_loss': float( y[7]), 
                    'take_profit': float( y[8]), 
                    'delete_price': float(y[9]), 
                    'delete_time': int( y[10]), 
                    'comment': str( y[11])
            }

            # Convert the dictionary to DataFrame and append to the main DataFrame
            df_add = pd.DataFrame([rowOrder])
            deleted_orders = pd.concat([deleted_orders, df_add], ignore_index=True)

        # Sort the DataFrame by open_time in ascending order
        deleted_orders.sort_values(by=['open_time'], ascending=True, inplace=True)

        # Set the command_OK flag to True indicating successful operation
        self.command_OK = True

        # Return the DataFrame containing deleted orders
        return deleted_orders

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

        # Reset parameters
        self.command_return_error = ''

        # Get all pending orders
        ok, resp = self.send_command("F060^1^")

        # Print the response for debugging purposes
        if self.debug:
            print(resp)

        # Check if the response is OK
        if not ok:
            self.command_OK = False
            return None

        # Create an empty DataFrame with the correct columns
        orders = self.create_empty_DataFrame(self.columnsOpenOrders, 'id')

        # Split the response into a list of strings
        x = resp.split('^')

        # Check if the response is correct
        if str(x[0]) != 'F060':
            self.command_return_error = ERROR_DICT['99901']
            self.command_OK = False
            return None

        # Remove the first two entries and the last entry from the list
        del x[0:2]
        x.pop(-1)

        # Process each entry in the list
        for value in range(0, len(x)):
            # Split each entry into a list of strings
            y = x[value].split('$')

            # Create a dictionary for each order
            rowOrder = {
                'ticket': int(y[0]),
                'instrument': self.get_universal_instrument_name(str(y[1])),
                'order_type': str(y[2]),
                'magic_number': int(y[3]),
                'volume': float(y[4]),
                'open_price': float(y[5]),
                'open_time': int(y[6]),
                'stop_loss': float(y[7]),
                'take_profit': float(y[8]),
                'comment': str(y[9])
            }

            # Convert the dictionary to DataFrame and append to the main DataFrame
            df_add = pd.DataFrame([rowOrder])
            orders = pd.concat([orders, df_add], ignore_index=True)

        # Sort the DataFrame by open_time in ascending order
        orders.sort_values(by=['open_time'], ascending=True, inplace=True)

        # Set the command_OK flag to True indicating successful operation
        self.command_OK = True

        # Return the DataFrame containing all orders
        return orders
        
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
        # Reset parameters
        self.command_return_error = ''
        self.command = 'F061^1^'

        # Get all open positions
        ok, resp = self.send_command(self.command)

        if self.debug:
            print(resp)

        if not ok:
            self.command_OK = False
            return None

        # Create an empty DataFrame for open positions
        positions = self.create_empty_DataFrame(
            self.columnsOpenPositions, 'id')

        # Split the response into a list of strings
        x = resp.split('^')

        # Check if the response header is valid
        if str(x[0]) != 'F061':
            self.command_return_error = ERROR_DICT['99901']
            self.command_OK = False
            return None

        # Remove the first two entries and the last entry from the list
        del x[0:2]
        x.pop(-1)

        # Process each entry in the list
        for value in range(0, len(x)):
            # Split each entry into a list of strings
            y = x[value].split('$')

            # Create a dictionary for each order
            rowPosition = {
                'ticket': int(y[0]),  # Unique identifier of the position
                'instrument': self.get_universal_instrument_name(y[1]),  # Universal instrument name
                'order_ticket': int(y[2]),  # Unique identifier of the order
                'position_type': str(y[3]),  # Type of position
                'magic_number': int(y[4]),  # Magic number of the order
                'volume': float(y[5]),  # Volume of the position
                'open_price': float(y[6]),  # Open price of the position
                'open_time': int(y[7]),  # Open time of the position
                'stop_loss': float(y[8]),  # Stop loss price
                'take_profit': float(y[9]),  # Take profit price
                'comment': str(y[10]),  # Comment of the order
                'profit': float(y[11]),  # Profit of the position
                'swap': float(y[12]),  # Swap
                'commission': float(y[13])  # Commission
            }

            # Convert the dictionary to DataFrame and append to the main DataFrame
            df_add = pd.DataFrame([rowPosition])

            positions = pd.concat([positions, df_add], ignore_index=True)
        
        # Sort the DataFrame by open_time in ascending order
        positions.sort_values(by=['open_time'], ascending= True,inplace=True)

        # Set the command_OK flag to True indicating successful operation
        self.command_OK = True

        # Return the DataFrame containing all open positions
        return positions

    def Get_closed_positions_within_window(self,
                                           date_from: datetime = datetime(2021, 3, 20, tzinfo=pytz.timezone("Etc/UTC")),
                                           date_to: datetime = datetime.now()) -> pd.DataFrame:
        """ 
        Retrieves all closed positions/orders within a specified time window.
        Both open and close times must fall within the time window.

        Args:
            date_from (datetime): Starting date for retrieving orders.
            date_to (datetime): Ending date for retrieving orders.

        Returns:
            pd.DataFrame: DataFrame containing closed positions with columns:
                - position_ticket
                - instrument
                - order_ticket
                - position_type
                - magic_number
                - volume
                - open_price
                - open_time
                - stop loss
                - take profit
                - close_price
                - close_time
                - comment
                - profit
                - swap
                - commission
        """
        # Initialize command error and date range
        self.command_return_error = ''
        self.date_from = date_from
        self.date_to = date_to

        # Construct command string to fetch closed positions within the date range
        self.command = 'F062^3^' + self.date_from.strftime('%Y/%m/%d/%H/%M/%S') + '^' + self.date_to.strftime('%Y/%m/%d/%H/%M/%S') + '^'

        # Send the command and capture the response
        ok, resp = self.send_command(self.command)

        # Print response if debug mode is enabled
        if self.debug:
            print(resp)

        # If command fails, set flag and return None
        if not ok:
            self.command_OK = False
            return None

        # Create an empty DataFrame to store closed positions
        closed_positions = self.create_empty_DataFrame(self.columnsClosedPositions, 'id')

        # Split the response string into components
        x = resp.split('^')

        # Validate response header
        if str(x[0]) != 'F062':
            self.command_return_error = ERROR_DICT['99901']
            self.command_OK = False
            return None

        # Clean the response list by removing header and footer
        del x[0:2]
        x.pop(-1)

        # Process each entry in the response
        for value in range(0, len(x)):
            # Split each entry into its respective fields
            y = x[value].split('$')

            # Map fields to a dictionary representing a closed position
            rowClosedPosition = {
                'ticket': int(y[0]),
                'instrument': self.get_universal_instrument_name(str(y[1])),
                'order_ticket': int(y[2]),
                'position_type': str(y[3]),
                'magic_number': int(y[4]),
                'volume': float(y[5]),
                'open_price': float(y[6]),
                'open_time': int(y[7]),
                'stop_loss': float(y[8]),
                'take_profit': float(y[9]),
                'close_price': float(y[10]),
                'close_time': int(y[11]),
                'comment': str(y[12]),
                'profit': float(y[13]),
                'swap': float(y[14]),
                'commission': float(y[15])
            }

            # Convert dictionary to DataFrame row and append to main DataFrame
            df_add = pd.DataFrame([rowClosedPosition])
            closed_positions = pd.concat([closed_positions, df_add], ignore_index=True)

        # Sort the DataFrame by open_time in ascending order
        closed_positions.sort_values(by=['open_time'], ascending=True, inplace=True)

        # Set flag indicating successful command execution
        self.command_OK = True

        # Return the populated DataFrame
        return closed_positions

    def Get_all_closed_positions(self) -> pd.DataFrame:
        """ 
        Retrieves all closed positions/orders.
        For MT4, all must be visible in the history tab of the MT4 terminal.

        Returns:
            pd.DataFrame: DataFrame with all closed position information, including:
            - ticket
            - instrument
            - order_ticket
            - position_type
            - magic_number
            - volume
            - open_price
            - open_time
            - stop_loss
            - take_profit
            - close_price
            - close_time
            - comment
            - profit
            - swap
            - commission
        """
        # Initialize the command return error message
        self.command_return_error = ''

        # Set the command to retrieve closed positions
        self.command = 'F063^1^'
        ok, resp = self.send_command(self.command)
        
        # Print the response if debugging is enabled
        if self.debug:
            print(resp)

        # Check if the command execution was successful
        if not ok:
            self.command_OK = False
            return None

        # Create an empty DataFrame to store closed positions
        closed_positions = self.create_empty_DataFrame(
            self.columnsClosedPositions, 'id')
        
        # Split the response into a list of strings
        x = resp.split('^')
        
        # Verify the response header
        if str(x[0]) != 'F063':
            self.command_return_error = ERROR_DICT['99901']
            self.command_OK = False
            return None

        # Remove the first two elements and the last element from the list
        del x[0:2]
        x.pop(-1)

        # Process each entry in the response
        for value in range(0, len(x)):
            # Split each entry into its respective fields
            y = x[value].split('$')

            # Map fields to a dictionary representing a closed position
            rowClosedPosition = {
                'ticket': int(y[0]),
                'instrument': self.get_universal_instrument_name(str(y[1])),
                'order_ticket': int(y[2]),
                'position_type': str(y[3]),
                'magic_number': int(y[4]),
                'volume': float(y[5]),
                'open_price': float(y[6]),
                'open_time': int(y[7]),
                'stop_loss': float(y[8]),
                'take_profit': float(y[9]),
                'close_price': float(y[10]),
                'close_time': int(y[11]),
                'comment': str(y[12]),
                'profit': float(y[13]),
                'swap': float(y[14]),
                'commission': float(y[15])
            }

            # Convert dictionary to DataFrame row and append to main DataFrame
            df_add = pd.DataFrame([rowClosedPosition])
            closed_positions = pd.concat([closed_positions, df_add], ignore_index=True)

        # Sort the DataFrame by open_time in ascending order
        closed_positions.sort_values(by=['open_time'], ascending=True, inplace=True)

        # Set flag indicating successful command execution
        self.command_OK = True

        # Return the populated DataFrame
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
            market: true, must be in watch list
        Returns:
            int: ticket number. If -1, open order failed
        """

        # Set the command_return_error to an empty string
        self.command_return_error = ''

        # Get the universal instrument name
        self.instrument_name_universal = instrument.upper()

        # Check the command for '^' , '$', '!' character
        # These are not allowed, used as delimiters
        comment.replace('^', '')
        comment.replace('$', '')
        comment.replace('!', '')

        # Get the broker instrument name
        broker_instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none' or self.instrument == None):
            self.command_return_error = 'Instrument not known, check brookerlookuptable'
            self.command_OK = False
            self.order_return_message = 'Instrument not known, check brookerlookuptable'
            return int(-1)
        
        # Build the command string
        self.command = 'F070^11^' + self.get_broker_instrument_name(self.instrument_name_universal) + '^' + ordertype + '^' + str(volume) + '^' + \
            str(openprice) + '^' + str(slippage) + '^' + str(magicnumber) + '^' + str(stoploss) + '^' + str(takeprofit) + '^' + str(comment) + '^' + str(market) + '^'
        #print(self.command)
        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return int(-1)

        # If debug is true, print the response
        if self.debug:
            print(dataString)

        # Split the response into a list of strings
        x = dataString.split('^')
        if str(x[0]) != 'F070':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
            return int(-1)

        # Set the command_OK flag to True indicating successful operation
        self.command_OK = True

        # Return the ticket number
        if (int(x[1]) == 3):
            self.order_return_message = str(x[2])
            self.order_error = int(x[4])
            return int(x[3])

    def Close_position_by_ticket(self,
                                 ticket: int = 0) -> bool:
        """
        Close a position.

        This function will close a position by ticket.

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

        # If debug is True, print the response
        if self.debug:
            print(dataString)

        # Split the response into a list of strings
        x = dataString.split('^')
        if str(x[0]) != 'F071':
            # If command is not successful, set the error message
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

        This function will close a position partial by ticket.

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

        # If debug is True, print the response
        if self.debug:
            print(dataString)

        # Split the response into a list of strings
        x = dataString.split('^')
        if str(x[0]) != 'F072':
            # If command is not successful, set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            #self.order_error = ERROR_DICT[str(x[3])]
            return False

        return True

    def CloseBy_position_by_ticket(self,
                                 ticket: int = 0,
                                 ticket_opposite: int = 0) -> bool:
        """
        Close a position.

        This function will close a position by ticket.

        Args:
            ticket: ticket of position to close
            ticket_opposite: opposite ticket for closing

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F074^3^' + str(ticket) + '^' + str(ticket_opposite) + '^'
        ok, dataString = self.send_command(self.command)
        if not ok:
            # If the command is not successful, set the error message
            self.command_OK = False
            return False

        # If debug is True, print the response
        if self.debug:
            print(dataString)

        # Split the response into a list of strings
        x = dataString.split('^')
        if str(x[0]) != 'F074':
            # If the command is not successful, set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
            return False

        # If the command is successful, return True
        return True

    def Close_positions_async(self,
                              instrument: str = '***',
                              magic_number: int = -1) -> bool:
        """
        Close positions.

        This function will close positions by instrument and magic number, but not waiting for result.

        Args:
            instrument: close only positions with this instrument, default all (***)
            magic_number: close only positions with this magic number, default all (-1)

        Returns:
            bool: True or False
        """
        # Set the command string for closing a position
        if (instrument == '***'):
            self.command = 'F091^3^' + str(instrument) + '^' + str(magic_number) + '^'
        else:
            # Get the broker instrument name
            self.instrument_name_universal = instrument
            self.command = 'F091^3^' + str(self.get_broker_instrument_name(self.instrument_name_universal)) + '^' + str(magic_number) + '^'

        # Send the command to the broker
        ok, dataString = self.send_command(self.command)
        if not ok:
            # If the command is not successful, set the error message
            self.command_OK = False
            return False

        # If debug is True, print the response
        if self.debug:
            print(dataString)

        # Split the response into a list of strings
        x = dataString.split('^')
        if str(x[0]) != 'F091':
            # If the command is not successful, set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[3])
            return False

        # If the command is successful, return True
        return True
    
    def Delete_order_by_ticket(self,
                               ticket: int = 0) -> bool:
        """
        Delete an order.

        Delete an order by its ticket number.

        Args:
            ticket: ticket of order(pending) to delete

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F073^2^' + str(ticket) + '^'
        # Send the command to the broker
        ok, dataString = self.send_command(self.command)
        if not ok:
            # If the command is not successful, set the error message
            self.command_OK = False
            return False

        # If debug is True, print the response
        if self.debug:
            print(dataString)

        # Split the response into a list of strings
        x = dataString.split('^')
        if str(x[0]) != 'F073':
            # If the command is not successful, set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
            return False

        # If the command is successful, return True
        return True

    def Set_sl_and_tp_for_position(self,
                                   ticket: int = 0,
                                   stoploss: float = 0.0,
                                   takeprofit: float = 0.0) -> bool:
        """
        Change stop loss and take profit for a position.

        This function will change the stop loss and take profit for a position
        by its ticket number.

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
            # If the command is not successful, set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
            return False

        # If the command is successful, return True
        return True

    def Set_sl_and_tp_for_order(self,
                                ticket: int = 0,
                                stoploss: float = 0.0,
                                takeprofit: float = 0.0) -> bool:
        """
        Change stop loss and take profit for an order.

        This function will change the stop loss and take profit for an order
        by its ticket number.

        Args:
            ticket: ticket of order to change
            stoploss; new stop loss value, must be actual price value
            takeprofit: new take profit value, must be actual price value

        Returns:
            bool: True or False
        """
        # Clear the return error
        self.command_return_error = ''

        # Build the command string
        self.command = 'F076^4^' + \
            str(ticket) + '^' + str(stoploss) + '^' + str(takeprofit) + '^'

        # Send the command and get the response
        ok, dataString = self.send_command(self.command)
        if not ok:
            # If the command is not successful, set the error message
            self.command_OK = False
            return False

        # If debug is True, print the response
        if self.debug:
            print(dataString)

        # Split the response into a list of strings
        x = dataString.split('^')
        if str(x[0]) != 'F076':
            # If the command is not successful, set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
            return False

        # If the command is successful, return True
        self.command_OK = True
        return True

    def Reset_sl_and_tp_for_position(self,
                                ticket: int = 0) -> bool:
        """
        Reset stop loss and take profit for a position.

        Args:
            ticket: ticket of position to change

        Returns:
            bool: True if the reset was successful, False otherwise.
        """
        # Clear any previous command return error
        self.command_return_error = ''
        
        # Construct the command string with the given ticket
        self.command = 'F077^2^' + str(ticket) + '^' 
        
        # Send the command and retrieve the response
        ok, dataString = self.send_command(self.command)
        if not ok:
            # If sending the command failed, set command_OK to False and return False
            self.command_OK = False
            return False

        # Print the response if debugging is enabled
        if self.debug:
            print(dataString)

        # Split the response data string into components
        x = dataString.split('^')
        
        # Check if the command was successful
        if str(x[0]) != 'F077':
            # If not successful, retrieve and set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
            return False

        # If successful, set command_OK to True and return True
        self.command_OK = True
        return True

    def Reset_sl_and_tp_for_order(self,
                                ticket: int = 0) -> bool:
        """
        Reset stop loss and take profit for an order.

        Args:
            ticket: ticket of order to change

        Returns:
            bool: True if the reset was successful, False otherwise.
        """
        # Clear any previous command return error
        self.command_return_error = ''

        # Construct the command string with the given ticket
        self.command = 'F078^2^' + str(ticket) + '^'

        # Send the command and retrieve the response
        ok, dataString = self.send_command(self.command)
        if not ok:
            # If sending the command failed, set command_OK to False and return False
            self.command_OK = False
            return False

        # Print the response if debugging is enabled
        if self.debug:
            print(dataString)

        # Split the response data string into components
        x = dataString.split('^')

        # Check if the command was successful
        if str(x[0]) != 'F078':
            # If not successful, retrieve and set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
            return False

        # If successful, set command_OK to True and return True
        self.command_OK = True
        return True

    def Change_settings_for_pending_order(self,
                                ticket: int = 0,
                                price: float = -1.0,
                                stoploss: float = -1.0,
                                takeprofit: float = -1.0) -> bool:
        """
        Change settings for a pending order.

        This function will change the settings of a pending order by its ticket number.

        Args:
            ticket: ticket of order to change
            price: new price value, if value=-1.0 no change
            stoploss: new stop loss value, if value=-1.0 no change
            takeprofit: new take profit value, if value=-1.0 no change

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        # Build the command string
        self.command = 'F079^5^' + str(ticket) + '^' + str(price) + '^' + str(stoploss) + '^' + str(takeprofit) + '^'
        
        # Send the command and get the response
        ok, dataString = self.send_command(self.command)
        if not ok:
            # If the command is not successful, set the error message
            self.command_OK = False
            return False

        # Print the response if debugging is enabled
        if self.debug:
            print(dataString)
            
        # Split the response into a list of strings
        x = dataString.split('^')
        if str(x[0]) != 'F079':
            # If the command is not successful, set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            self.order_error = int(x[4])
            return False

        # If the command is successful, return True
        self.command_OK = True
        return True
                
    def Set_global_variable(self, global_name: str = '', global_value: float = 0.0) -> bool:
        """
        Set a global variable in the trading platform.

        Args:
            global_name (str): The name of the global variable.
            global_value (float): The value of the global variable.

        Returns:
            bool: True if the command was successful, False otherwise.
        """
        self.command_return_error = ''
        # Construct the command string
        self.command = 'F080^3^' + global_name + '^' + str(global_value) + '^'
        # Send the command and get the response
        ok, dataString = self.send_command(self.command)
        if not ok:
            # If the command is not successful, set the error message
            self.command_OK = False
            return False

        # Print the response if debugging is enabled
        if self.debug:
            print(dataString)

        # Split the response into a list of strings
        x = dataString.split('^')
        if str(x[0]) != 'F080':
            # If the command is not successful, set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            #self.order_error = int(x[4])
            return False

        # If the command is successful, return True
        self.command_OK = True
        return True
    
    def Get_global_variable(self, global_name: str = 'GlobalVariableName') -> float:
        """
        Get the value of a global variable.

        Args:
            global_name (str): The name of the global variable to retrieve.

        Returns:
            float: The value of the global variable if successful, otherwise False.
        """
        # Clear any previous command return error
        self.command_return_error = ''

        # Construct the command string with the global variable name
        self.command = 'F081^1^' + global_name + '^'

        # Send the command and retrieve the response
        ok, dataString = self.send_command(self.command)
        if not ok:
            # If sending the command failed, set command_OK to False and return False
            self.command_OK = False
            return False

        # Print the response if debugging is enabled
        if self.debug:
            print(dataString)

        # Split the response data string into components
        x = dataString.split('^')

        # Check if the command was successful
        if str(x[0]) != 'F081':
            # If not successful, retrieve and set the error message
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            return False

        # If successful, set command_OK to True and return the global variable value
        self.command_OK = True
        return float(x[3])
        
    def Get_logfile(self, date: datetime = datetime.now()) -> pd.DataFrame:
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
            
        # Check if the command was successful
        if ok==True and resp[0:5]=="F082^" and resp[-1]=="!":
            # Extract the number of records
            nbr = resp[resp.index('^',3)+1:resp.index('^',5)]
            if int(nbr) != 0:
                # Extract the records from the response
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
            # If not successful, retrieve and set the error message
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

        Switches autotrading on or off. If on_off is True, autotrading is enabled. If on_off is False, autotrading is disabled.

        Parameters
        ----------
        on_off : bool, optional
            True to enable autotrading, False to disable autotrading (default is True)

        Returns
        -------
        bool
            True if autotrading was successfully switched, False otherwise
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
        """
        Send a command to the EA/Bot.

        Sends a command to the EA/Bot and waits for the response. The command
        string is terminated with the authorization code and the '!' character.
        If the command is sent successfully, the method returns a tuple
        (True, dataString). If an error occurs, the method returns a tuple
        (False, None).

        Parameters
        ----------
        command : str
            The command to be sent to the EA/Bot

        Returns
        -------
        tuple
            A tuple (True, dataString) if the command was sent successfully,
            a tuple (False, None) otherwise
        """

        # reset values
        self.socket_error = 0
        self.socket_error_message = ''
        self.order_return_message = ''
        self.order_error = 0
        self.connected = False
        self.timeout = False
        self.command_OK = False
        self.command_return_error = ''

        self.command = command + self.authorization_code + "^" "!"
        
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
            self.connected = True
            return True, data_received
        except socket.timeout as msg:
            self.timeout = True
            self.IsConnected = False
            self.command_return_error = 'Unexpected socket communication error'
            print(msg)
            self.connected = False
            return False, None

    def get_timeframe_value(self,
                            timeframe: str = 'D1') -> int:
        """
        Convert a timeframe name to a value.

        The method takes a timeframe name as input and returns the corresponding
        value. The value is an integer that can be used in methods of the MT5
        library that require a timeframe value.

        Parameters
        ----------
        timeframe : str, optional
            The timeframe name (default is 'D1')

        Returns
        -------
        int
            The timeframe value

        Notes
        -----
        The values are taken from the MT5 library.
        """
        self.tf = 16408  # mt5.TIMEFRAME_D1
        timeframe.upper()
        if timeframe == 'MN1':
            self.tf = 49153  # mt5.TIMEFRAME_MN1
        elif timeframe == 'W1':
            self.tf = 32769  # mt5.TIMEFRAME_W1
        elif timeframe == 'D1':
            self.tf = 16408  # mt5.TIMEFRAME_D1
        elif timeframe == 'H12':
            self.tf = 16396  # mt5.TIMEFRAME_H12
        elif timeframe == 'H8':
            self.tf = 16392  # mt5.TIMEFRAME_H8
        elif timeframe == 'H6':
            self.tf = 16390  # mt5.TIMEFRAME_H6
        elif timeframe == 'H4':
            self.tf = 16388  # mt5.TIMEFRAME_H4
        elif timeframe == 'H3':
            self.tf = 16387  # mt5.TIMEFRAME_H3
        elif timeframe == 'H2':
            self.tf = 16386  # mt5.TIMEFRAME_H2
        elif timeframe == 'H1':
            self.tf = 16385  # mt5.TIMEFRAME_H1
        elif timeframe == 'M30':
            self.tf = 30  # mt5.TIMEFRAME_M30
        elif timeframe == 'M20':
            self.tf = 20  # mt5.TIMEFRAME_M20
        elif timeframe == 'M15':
            self.tf = 15  # mt5.TIMEFRAME_M15
        elif timeframe == 'M12':
            self.tf = 12  # mt5.TIMEFRAME_M12
        elif timeframe == 'M10':
            self.tf = 10  # mt5.TIMEFRAME_M10
        elif timeframe == 'M6':
            self.tf = 6  # mt5.TIMEFRAME_M6
        elif timeframe == 'M5':
            self.tf = 5  # mt5.TIMEFRAME_M5
        elif timeframe == 'M4':
            self.tf = 4  # mt5.TIMEFRAME_M4
        elif timeframe == 'M3':
            self.tf = 3  # mt5.TIMEFRAME_M3
        elif timeframe == 'M2':
            self.tf = 2  # mt5.TIMEFRAME_M2
        elif timeframe == 'M1':
            self.tf = 1  # mt5.TIMEFRAME_M1

        return self.tf

    def get_broker_instrument_name(self,
                                   instrumentname: str = '') -> str:
        """
        Retrieve the broker instrument name for a given universal instrument name.

        Args:
            instrumentname (str): The universal instrument name.

        Returns:
            str: The broker instrument name if found, otherwise 'none'.
        """
        # Store the input instrument name
        self.intrumentname = instrumentname
        try:
            # Retrieve the broker's instrument name from the conversion list
            return self.instrument_conversion_list.get(str(instrumentname))
        except BaseException:
            # Return 'none' if an error occurs
            return 'none'

    def get_universal_instrument_name(self,
                                      instrumentname: str = '') -> str:
        """
        Retrieve the universal instrument name for a given broker instrument name.

        Args:
            instrumentname (str): The broker instrument name.

        Returns:
            str: The universal instrument name if found, otherwise 'none'.
        """

        # Store the input instrument name
        self.instrumentname = instrumentname
        try:
            # Retrieve the universal instrument name from the conversion list
            for item in self.instrument_conversion_list:
                key = str(item)
                value = self.instrument_conversion_list.get(item)
                if (value == instrumentname):
                    return str(key)
        except BaseException:
            # Return 'none' if an error occurs
            return 'none'
        return 'none'

    def create_empty_DataFrame(self, columns, index_col) -> pd.DataFrame:
        """
        Create an empty DataFrame with specified columns and index column.

        Args:
            columns (list of tuples): A list of tuples where each tuple contains the column name and its data type.
            index_col (str): The name of the column to be used as the index.

        Returns:
            pd.DataFrame: An empty DataFrame with the specified columns and index.
        """
        # Determine the data type for the index column
        index_type = next((t for name, t in columns if name == index_col))

        # Create an empty DataFrame with specified column data types, excluding the index column
        df = pd.DataFrame({name: pd.Series(dtype=t) for name, t in columns if name != index_col},
                          index=pd.Index([], dtype=index_type))

        # Collect column names excluding the index column
        cols = [name for name, _ in columns]
        cols.remove(index_col)

        # Return the DataFrame with columns in the specified order
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
        ('instrument', float),
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
    

