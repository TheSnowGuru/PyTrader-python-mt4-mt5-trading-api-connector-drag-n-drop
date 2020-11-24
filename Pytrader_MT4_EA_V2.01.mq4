//+------------------------------------------------------------------+
//|                                         Pytrade_MT4_EA_V2.01.mq4 |
//|                           Copyright 2020, Deeptrade.ml / Branly. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2020, Deeptrade.ml / Branly."
#property link      "https://www.mql5.com"
#property version   "2.01"
#property description "Coded by Branly"
#property strict


#include <stdlib.mqh>
#include <WinUser32.mqh>

// --------------------------------------------------------------------
// Include socket library, asking for event handling
// --------------------------------------------------------------------
#define SOCKET_LIBRARY_USE_EVENTS
// -------------------------------------------------------------
// Winsock constants and structures
// -------------------------------------------------------------

#define SOCKET_HANDLE32       uint
#define SOCKET_HANDLE64       ulong
#define AF_INET               2
#define SOCK_STREAM           1
#define IPPROTO_TCP           6
#define INVALID_SOCKET32      0xFFFFFFFF
#define INVALID_SOCKET64      0xFFFFFFFFFFFFFFFF
#define SOCKET_ERROR          -1
#define INADDR_NONE           0xFFFFFFFF
#define FIONBIO               0x8004667E
#define WSAWOULDBLOCK         10035

struct sockaddr {
   short family;
   ushort port;
   uint address;
   ulong ignore;
};

struct linger {
   ushort onoff;
   ushort linger_seconds;
};

// -------------------------------------------------------------
// DLL imports
// -------------------------------------------------------------


#import "ws2_32.dll"
   // Imports for 32-bit environment
   SOCKET_HANDLE32 socket(int, int, int); // Artificially differs from 64-bit version based on 3rd parameter
   int connect(SOCKET_HANDLE32, sockaddr&, int);
   int closesocket(SOCKET_HANDLE32);
   int send(SOCKET_HANDLE32, uchar&[],int,int);
   int recv(SOCKET_HANDLE32, uchar&[], int, int);
   int ioctlsocket(SOCKET_HANDLE32, uint, uint&);
   int bind(SOCKET_HANDLE32, sockaddr&, int);
   int listen(SOCKET_HANDLE32, int);
   SOCKET_HANDLE32 accept(SOCKET_HANDLE32, int, int);
   int WSAAsyncSelect(SOCKET_HANDLE32, int, uint, int);
   int shutdown(SOCKET_HANDLE32, int);
   
   // Imports for 64-bit environment
   SOCKET_HANDLE64 socket(int, int, uint); // Artificially differs from 32-bit version based on 3rd parameter
   int connect(SOCKET_HANDLE64, sockaddr&, int);
   int closesocket(SOCKET_HANDLE64);
   int send(SOCKET_HANDLE64, uchar&[], int, int);
   int recv(SOCKET_HANDLE64, uchar&[], int, int);
   int ioctlsocket(SOCKET_HANDLE64, uint, uint&);
   int bind(SOCKET_HANDLE64, sockaddr&, int);
   int listen(SOCKET_HANDLE64, int);
   SOCKET_HANDLE64 accept(SOCKET_HANDLE64, int, int);
   int WSAAsyncSelect(SOCKET_HANDLE64, long, uint, int);
   int shutdown(SOCKET_HANDLE64, int);

   // gethostbyname() has to vary between 32/64-bit, because
   // it returns a memory pointer whose size will be either
   // 4 bytes or 8 bytes. In order to keep the compiler
   // happy, we therefore need versions which take 
   // artificially-different parameters on 32/64-bit
   uint gethostbyname(uchar&[]); // For 32-bit
   ulong gethostbyname(char&[]); // For 64-bit

   // Neutral; no difference between 32-bit and 64-bit
   uint inet_addr(uchar&[]);
   int WSAGetLastError();
   uint htonl(uint);
   ushort htons(ushort);
#import

// For navigating the Winsock hostent structure, with indescribably horrible
// variation between 32-bit and 64-bit
#import "kernel32.dll"
   void RtlMoveMemory(uint&, uint, int);
   void RtlMoveMemory(ushort&, uint, int);
   void RtlMoveMemory(ulong&, ulong, int);
   void RtlMoveMemory(ushort&, ulong, int);
#import

// -------------------------------------------------------------
// Forward definitions of classes
// -------------------------------------------------------------

class ClientSocket;
class ServerSocket;


// -------------------------------------------------------------
// Client socket class
// -------------------------------------------------------------

class ClientSocket
{
   private:
      // Need different socket handles for 32-bit and 64-bit environments
      SOCKET_HANDLE32 mSocket32;
      SOCKET_HANDLE64 mSocket64;
      
      // Other state variables
      bool mConnected;
      int mLastWSAError;
      string mPendingReceiveData; // Backlog of incoming data, if using a message-terminator in Receive()
      
      // Event handling
      bool mDoneEventHandling;
      void SetupSocketEventHandling();
      
   public:
      // Constructors for connecting to a server, either locally or remotely
      ClientSocket(ushort localport);
      ClientSocket(string HostnameOrIPAddress, ushort port);

      // Constructors used by ServerSocket() when accepting a client connection
      ClientSocket(ServerSocket* ForInternalUseOnly, SOCKET_HANDLE32 ForInternalUseOnly_clientsocket32);
      ClientSocket(ServerSocket* ForInternalUseOnly, SOCKET_HANDLE64 ForInternalUseOnly_clientsocket64);

      // Destructor
      ~ClientSocket();
      
      // Simple send and receive methods
      bool Send(string strMsg);
      bool Send(uchar & callerBuffer[], int startAt = 0, int szToSend = -1);
      string Receive(string MessageSeparator = "");
      int Receive(uchar & callerBuffer[]);
      
      // State information
      bool IsSocketConnected() {return mConnected;}
      int GetLastSocketError() {return mLastWSAError;}
      ulong GetSocketHandle() {return (mSocket32 ? mSocket32 : mSocket64);}
      
      // Buffer sizes, overwriteable once the class has been created
      int ReceiveBufferSize;
      int SendBufferSize;
};


// -------------------------------------------------------------
// Constructor for a simple connection to 127.0.0.1
// -------------------------------------------------------------
ClientSocket::ClientSocket(ushort localport)
{
   // Default buffer sizes
   ReceiveBufferSize = 10000;
   SendBufferSize = 999999999;
   
   // Need to create either a 32-bit or 64-bit socket handle
   mConnected = false;
   mLastWSAError = 0;
   if (TerminalInfoInteger(TERMINAL_X64)) {
      uint proto = IPPROTO_TCP;
      mSocket64 = socket(AF_INET, SOCK_STREAM, proto);
      if (mSocket64 == INVALID_SOCKET64) {
         mLastWSAError = WSAGetLastError();
         #ifdef SOCKET_LIBRARY_LOGGING
            Print("socket() failed, 64-bit, error: ", mLastWSAError);
         #endif
         return;
      }
   } else {
      int proto = IPPROTO_TCP;
      mSocket32 = socket(AF_INET, SOCK_STREAM, proto);
      if (mSocket32 == INVALID_SOCKET32) {
         mLastWSAError = WSAGetLastError();
         #ifdef SOCKET_LIBRARY_LOGGING
            Print("socket() failed, 32-bit, error: ", mLastWSAError);
         #endif
         return;
      }
   }
   
   // Fixed definition for connecting to 127.0.0.1, with variable port
   sockaddr server;
   server.family = AF_INET;
   server.port = htons(localport);
   server.address = 0x100007f; // 127.0.0.1
   
   // connect() call has to differ between 32-bit and 64-bit
   int res;
   if (TerminalInfoInteger(TERMINAL_X64)) {
      res = connect(mSocket64, server, sizeof(sockaddr));
   } else {
      res = connect(mSocket32, server, sizeof(sockaddr));
   }
   if (res == SOCKET_ERROR) {
      // Ooops
      mLastWSAError = WSAGetLastError();
      #ifdef SOCKET_LIBRARY_LOGGING
         Print("connect() to localhost failed, error: ", mLastWSAError);
      #endif
      return;
   } else {
      mConnected = true;   
      
      // Set up event handling. Can fail if called in OnInit() when
      // MT4/5 is still loading, because no window handle is available
      #ifdef SOCKET_LIBRARY_USE_EVENTS
         SetupSocketEventHandling();
      #endif
   }
}

// -------------------------------------------------------------
// Constructor for connection to a hostname or IP address
// -------------------------------------------------------------

ClientSocket::ClientSocket(string HostnameOrIPAddress, ushort port)
{
   // Default buffer sizes
   ReceiveBufferSize = 10000;
   SendBufferSize = 999999999;

   // Need to create either a 32-bit or 64-bit socket handle
   mConnected = false;
   mLastWSAError = 0;
   if (TerminalInfoInteger(TERMINAL_X64)) {
      uint proto = IPPROTO_TCP;
      mSocket64 = socket(AF_INET, SOCK_STREAM, proto);
      if (mSocket64 == INVALID_SOCKET64) {
         mLastWSAError = WSAGetLastError();
         #ifdef SOCKET_LIBRARY_LOGGING
            Print("socket() failed, 64-bit, error: ", mLastWSAError);
         #endif
         return;
      }
   } else {
      int proto = IPPROTO_TCP;
      mSocket32 = socket(AF_INET, SOCK_STREAM, proto);
      if (mSocket32 == INVALID_SOCKET32) {
         mLastWSAError = WSAGetLastError();
         #ifdef SOCKET_LIBRARY_LOGGING
            Print("socket() failed, 32-bit, error: ", mLastWSAError);
         #endif
         return;
      }
   }

   // Is the host parameter an IP address?
   uchar arrName[];
   StringToCharArray(HostnameOrIPAddress, arrName);
   ArrayResize(arrName, ArraySize(arrName) + 1);
   uint addr = inet_addr(arrName);
   
   if (addr == INADDR_NONE) {
      // Not an IP address. Need to look up the name
      // .......................................................................................
      // Unbelievably horrible handling of the hostent structure depending on whether
      // we're in 32-bit or 64-bit, with different-length memory pointers. 
      // Ultimately, we're having to deal here with extracting a uint** from
      // the memory block provided by Winsock - and with additional 
      // complications such as needing different versions of gethostbyname(),
      // because the return value is a pointer, which is 4 bytes in x86 and
      // 8 bytes in x64. So, we must artifically pass different types of buffer
      // to gethostbyname() depending on the environment, so that the compiler
      // doesn't treat them as imports which differ only by their return type.
      if (TerminalInfoInteger(TERMINAL_X64)) {
         char arrName64[];
         ArrayResize(arrName64, ArraySize(arrName));
         for (int i = 0; i < ArraySize(arrName); i++) arrName64[i] = (char)arrName[i];
         ulong nres = gethostbyname(arrName64);
         if (nres == 0) {
            // Name lookup failed
            mLastWSAError = WSAGetLastError();
            #ifdef SOCKET_LIBRARY_LOGGING
               Print("Name-resolution in gethostbyname() failed, 64-bit, error: ", mLastWSAError);
            #endif
            return;
         } else {
            // Need to navigate the hostent structure. Very, very ugly...
            ushort addrlen;
            RtlMoveMemory(addrlen, nres + 18, 2);
            if (addrlen == 0) {
               // No addresses associated with name
               #ifdef SOCKET_LIBRARY_LOGGING
                  Print("Name-resolution in gethostbyname() returned no addresses, 64-bit, error: ", mLastWSAError);
               #endif
               return;
            } else {
               ulong ptr1, ptr2, ptr3;
               RtlMoveMemory(ptr1, nres + 24, 8);
               RtlMoveMemory(ptr2, ptr1, 8);
               RtlMoveMemory(ptr3, ptr2, 4);
               addr = (uint)ptr3;
            }
         }
      } else {
         uint nres = gethostbyname(arrName);
         if (nres == 0) {
            // Name lookup failed
            mLastWSAError = WSAGetLastError();
            #ifdef SOCKET_LIBRARY_LOGGING
               Print("Name-resolution in gethostbyname() failed, 32-bit, error: ", mLastWSAError);
            #endif
            return;
         } else {
            // Need to navigate the hostent structure. Very, very ugly...
            ushort addrlen;
            RtlMoveMemory(addrlen, nres + 10, 2);
            if (addrlen == 0) {
               // No addresses associated with name
               #ifdef SOCKET_LIBRARY_LOGGING
                  Print("Name-resolution in gethostbyname() returned no addresses, 32-bit, error: ", mLastWSAError);
               #endif
               return;
            } else {
               int ptr1, ptr2;
               RtlMoveMemory(ptr1, nres + 12, 4);
               RtlMoveMemory(ptr2, ptr1, 4);
               RtlMoveMemory(addr, ptr2, 4);
            }
         }
      }
   
   } else {
      // The HostnameOrIPAddress parameter is an IP address,
      // which we have stored in addr
   }

   // Fill in the address and port into a sockaddr_in structure
   sockaddr server;
   server.family = AF_INET;
   server.port = htons(port);
   server.address = addr; // Already in network-byte-order

   // connect() call has to differ between 32-bit and 64-bit
   int res;
   if (TerminalInfoInteger(TERMINAL_X64)) {
      res = connect(mSocket64, server, sizeof(sockaddr));
   } else {
      res = connect(mSocket32, server, sizeof(sockaddr));
   }
   if (res == SOCKET_ERROR) {
      // Ooops
      mLastWSAError = WSAGetLastError();
      #ifdef SOCKET_LIBRARY_LOGGING
         Print("connect() to server failed, error: ", mLastWSAError);
      #endif
   } else {
      mConnected = true;   

      // Set up event handling. Can fail if called in OnInit() when
      // MT4/5 is still loading, because no window handle is available
      #ifdef SOCKET_LIBRARY_USE_EVENTS
         SetupSocketEventHandling();
      #endif
   }
}

// -------------------------------------------------------------
// Constructors for internal use only, when accepting connections
// on a server socket
// -------------------------------------------------------------

ClientSocket::ClientSocket(ServerSocket* ForInternalUseOnly, SOCKET_HANDLE32 ForInternalUseOnly_clientsocket32)
{
   // Constructor ror "internal" use only, when accepting an incoming connection
   // on a server socket
   mConnected = true;
   ReceiveBufferSize = 10000;
   SendBufferSize = 999999999;

   mSocket32 = ForInternalUseOnly_clientsocket32;
}

ClientSocket::ClientSocket(ServerSocket* ForInternalUseOnly, SOCKET_HANDLE64 ForInternalUseOnly_clientsocket64)
{
   // Constructor ror "internal" use only, when accepting an incoming connection
   // on a server socket
   mConnected = true;
   ReceiveBufferSize = 10000;
   SendBufferSize = 999999999;

   mSocket64 = ForInternalUseOnly_clientsocket64;
}


// -------------------------------------------------------------
// Destructor. Close the socket if created
// -------------------------------------------------------------

ClientSocket::~ClientSocket()
{
   if (TerminalInfoInteger(TERMINAL_X64)) {
      if (mSocket64 != 0) {
         shutdown(mSocket64, 2);
         closesocket(mSocket64);
      }
   } else {
      if (mSocket32 != 0) {
         shutdown(mSocket32, 2);
         closesocket(mSocket32);
      }
   }   
}

// -------------------------------------------------------------
// Simple send function which takes a string parameter
// -------------------------------------------------------------

bool ClientSocket::Send(string strMsg)
{
   if (!mConnected) return false;

   // Make sure that event handling is set up, if requested
   #ifdef SOCKET_LIBRARY_USE_EVENTS
      SetupSocketEventHandling();
   #endif 

   int szToSend = StringLen(strMsg);
   if (szToSend == 0) return true; // Ignore empty strings
      
   bool bRetval = true;
   uchar arr[];
   StringToCharArray(strMsg, arr);
   
   while (szToSend > 0) {
      int res, szAmountToSend = (szToSend > SendBufferSize ? SendBufferSize : szToSend);
      if (TerminalInfoInteger(TERMINAL_X64)) {
         res = send(mSocket64, arr, szToSend, 0);
      } else {
         res = send(mSocket32, arr, szToSend, 0);
      }
      
      if (res == SOCKET_ERROR || res == 0) {
         mLastWSAError = WSAGetLastError();
         if (mLastWSAError == WSAWOULDBLOCK) {
            // Blocking operation. Retry.
         } else {
            #ifdef SOCKET_LIBRARY_LOGGING
               Print("send() failed, error: ", mLastWSAError);
            #endif

            // Assume death of socket for any other type of error
            szToSend = -1;
            bRetval = false;
            mConnected = false;
         }
      } else {
         szToSend -= res;
         if (szToSend > 0) {
            // If further data remains to be sent, shuffle the array downwards
            // by copying it onto itself. Note that the MQL4/5 documentation
            // says that the result of this is "undefined", but it seems
            // to work reliably in real life (because it almost certainly
            // just translates inside MT4/5 into a simple call to RtlMoveMemory,
            // which does allow overlapping source & destination).
            ArrayCopy(arr, arr, 0, res, szToSend);
         }
      }
   }

   return bRetval;
}


// -------------------------------------------------------------
// Simple send function which takes an array of uchar[], 
// instead of a string. Can optionally be given a start-index
// within the array (rather then default zero) and a number 
// of bytes to send.
// -------------------------------------------------------------

bool ClientSocket::Send(uchar & callerBuffer[], int startAt = 0, int szToSend = -1)
{
   if (!mConnected) return false;

   // Make sure that event handling is set up, if requested
   #ifdef SOCKET_LIBRARY_USE_EVENTS
      SetupSocketEventHandling();
   #endif 

   // Process the start-at and send-size parameters
   int arraySize = ArraySize(callerBuffer);
   if (!arraySize) return true; // Ignore empty arrays 
   if (startAt >= arraySize) return true; // Not a valid start point; nothing to send
   if (szToSend <= 0) szToSend = arraySize;
   if (startAt + szToSend > arraySize) szToSend = arraySize - startAt;
   
   // Take a copy of the array 
   uchar arr[];
   ArrayResize(arr, szToSend);
   ArrayCopy(arr, callerBuffer, 0, startAt, szToSend);   
      
   bool bRetval = true;
   
   while (szToSend > 0) {
      int res, szAmountToSend = (szToSend > SendBufferSize ? SendBufferSize : szToSend);
      if (TerminalInfoInteger(TERMINAL_X64)) {
         res = send(mSocket64, arr, szToSend, 0);
      } else {
         res = send(mSocket32, arr, szToSend, 0);
      }
      
      if (res == SOCKET_ERROR || res == 0) {
         mLastWSAError = WSAGetLastError();
         if (mLastWSAError == WSAWOULDBLOCK) {
            // Blocking operation. Retry.
         } else {
            #ifdef SOCKET_LIBRARY_LOGGING
               Print("send() failed, error: ", mLastWSAError);
            #endif

            // Assume death of socket for any other type of error
            szToSend = -1;
            bRetval = false;
            mConnected = false;
         }
      } else {
         szToSend -= res;
         if (szToSend > 0) {
            // If further data remains to be sent, shuffle the array downwards
            // by copying it onto itself. Note that the MQL4/5 documentation
            // says that the result of this is "undefined", but it seems
            // to work reliably in real life (because it almost certainly
            // just translates inside MT4/5 into a simple call to RtlMoveMemory,
            // which does allow overlapping source & destination).
            ArrayCopy(arr, arr, 0, res, szToSend);
         }
      }
   }

   return bRetval;
}


// -------------------------------------------------------------
// Simple receive function. Without a message separator,
// it simply returns all the data sitting on the socket.
// With a separator, it stores up incoming data until
// it sees the separator, and then returns the text minus
// the separator.
// Returns a blank string once no (more) data is waiting
// for collection.
// -------------------------------------------------------------

string ClientSocket::Receive(string MessageSeparator = "")
{
   if (!mConnected) return "";

   // Make sure that event handling is set up, if requested
   #ifdef SOCKET_LIBRARY_USE_EVENTS
      SetupSocketEventHandling();
   #endif
   
   string strRetval = "";
   
   uchar arrBuffer[];
   ArrayResize(arrBuffer, ReceiveBufferSize);

   uint nonblock = 1;
   if (TerminalInfoInteger(TERMINAL_X64)) {
      ioctlsocket(mSocket64, FIONBIO, nonblock);
 
      int res = 1;
      while (res > 0) {
         res = recv(mSocket64, arrBuffer, ReceiveBufferSize, 0);
         if (res > 0) {
            StringAdd(mPendingReceiveData, CharArrayToString(arrBuffer, 0, res));

         } else if (res == 0) {
            // No data

         } else {
            mLastWSAError = WSAGetLastError();

            if (mLastWSAError != WSAWOULDBLOCK) {
               #ifdef SOCKET_LIBRARY_LOGGING
                  Print("recv() failed, result:, " , res, ", error: ", mLastWSAError, " queued bytes: " , StringLen(mPendingReceiveData));
               #endif
               mConnected = false;
            }
         }
      }
   } else {
      ioctlsocket(mSocket32, FIONBIO, nonblock);

      int res = 1;
      while (res > 0) {
         res = recv(mSocket32, arrBuffer, ReceiveBufferSize, 0);
         if (res > 0) {
            StringAdd(mPendingReceiveData, CharArrayToString(arrBuffer, 0, res));

         } else if (res == 0) {
            // No data
         
         } else {
            mLastWSAError = WSAGetLastError();

            if (mLastWSAError != WSAWOULDBLOCK) {
               #ifdef SOCKET_LIBRARY_LOGGING
                  Print("recv() failed, result:, " , res, ", error: ", mLastWSAError, " queued bytes: " , StringLen(mPendingReceiveData));
               #endif
               mConnected = false;
            }
         }
      }
   }   
   
   if (mPendingReceiveData == "") {
      // No data
      
   } else if (MessageSeparator == "") {
      // No requested message separator to wait for
      strRetval = mPendingReceiveData;
      mPendingReceiveData = "";
   
   } else {
      int idx = StringFind(mPendingReceiveData, MessageSeparator);
      if (idx >= 0) {
         while (idx == 0) {
            mPendingReceiveData = StringSubstr(mPendingReceiveData, idx + StringLen(MessageSeparator));
            idx = StringFind(mPendingReceiveData, MessageSeparator);
         }
         
         strRetval = StringSubstr(mPendingReceiveData, 0, idx);
         mPendingReceiveData = StringSubstr(mPendingReceiveData, idx + StringLen(MessageSeparator));
      }
   }
   
   return strRetval;
}

// -------------------------------------------------------------
// Receive function which fills an array, provided by reference.
// Always clears the array. Returns the number of bytes 
// put into the array.
// If you send and receive binary data, then you can no longer 
// use the built-in messaging protocol provided by this library's
// option to process a message terminator such as \r\n. You have
// to implement the messaging yourself.
// -------------------------------------------------------------

int ClientSocket::Receive(uchar & callerBuffer[])
{
   if (!mConnected) return 0;

   ArrayResize(callerBuffer, 0);
   int ctTotalReceived = 0;
   
   // Make sure that event handling is set up, if requested
   #ifdef SOCKET_LIBRARY_USE_EVENTS
      SetupSocketEventHandling();
   #endif
   
   uchar arrBuffer[];
   ArrayResize(arrBuffer, ReceiveBufferSize);

   uint nonblock = 1;
   if (TerminalInfoInteger(TERMINAL_X64)) {
      ioctlsocket(mSocket64, FIONBIO, nonblock);
   } else {
      ioctlsocket(mSocket32, FIONBIO, nonblock);
   }

   int res = 1;
   while (res > 0) {
      if (TerminalInfoInteger(TERMINAL_X64)) {
         res = recv(mSocket64, arrBuffer, ReceiveBufferSize, 0);
      } else {
         res = recv(mSocket32, arrBuffer, ReceiveBufferSize, 0);
      }
      
      if (res > 0) {
         ArrayResize(callerBuffer, ctTotalReceived + res);
         ArrayCopy(callerBuffer, arrBuffer, ctTotalReceived, 0, res);
         ctTotalReceived += res;

      } else if (res == 0) {
         // No data

      } else {
         mLastWSAError = WSAGetLastError();

         if (mLastWSAError != WSAWOULDBLOCK) {
            #ifdef SOCKET_LIBRARY_LOGGING
               Print("recv() failed, result:, " , res, ", error: ", mLastWSAError);
            #endif
            mConnected = false;
         }
      }
   }
   
   return ctTotalReceived;
}

// -------------------------------------------------------------
// Event handling in client socket
// -------------------------------------------------------------

void ClientSocket::SetupSocketEventHandling()
{
   #ifdef SOCKET_LIBRARY_USE_EVENTS
      if (mDoneEventHandling) return;
      
      // Can only do event handling in an EA. Ignore otherwise.
      if (MQLInfoInteger(MQL_PROGRAM_TYPE) != PROGRAM_EXPERT) {
         mDoneEventHandling = true;
         return;
      }
      
      long hWnd = ChartGetInteger(0, CHART_WINDOW_HANDLE);
      if (!hWnd) return;
      mDoneEventHandling = true; // Don't actually care whether it succeeds.
      
      if (TerminalInfoInteger(TERMINAL_X64)) {
         WSAAsyncSelect(mSocket64, hWnd, 0x100 /* WM_KEYDOWN */, 0xFF /* All events */);
      } else {
         WSAAsyncSelect(mSocket32, (int)hWnd, 0x100 /* WM_KEYDOWN */, 0xFF /* All events */);
      }
   #endif
}


// -------------------------------------------------------------
// Server socket class
// -------------------------------------------------------------

class ServerSocket
{
   private:
      // Need different socket handles for 32-bit and 64-bit environments
      SOCKET_HANDLE32 mSocket32;
      SOCKET_HANDLE64 mSocket64;

      // Other state variables
      bool mCreated;
      int mLastWSAError;
      
      // Optional event handling
      void SetupSocketEventHandling();
      bool mDoneEventHandling;
                 
   public:
      // Constructor, specifying whether we allow remote connections
      ServerSocket(ushort ServerPort, bool ForLocalhostOnly);
      
      // Destructor
      ~ServerSocket();
      
      // Accept function, which returns NULL if no waiting client, or
      // a new instace of ClientSocket()
      ClientSocket * Accept();

      // Access to state information
      bool Created() {return mCreated;}
      int GetLastSocketError() {return mLastWSAError;}
      ulong GetSocketHandle() {return (mSocket32 ? mSocket32 : mSocket64);}
};


// -------------------------------------------------------------
// Constructor for server socket
// -------------------------------------------------------------

ServerSocket::ServerSocket(ushort serverport, bool ForLocalhostOnly)
{
   // Create socket and make it non-blocking
   mCreated = false;
   mLastWSAError = 0;
   if (TerminalInfoInteger(TERMINAL_X64)) {
      // Force compiler to use the 64-bit version of socket() 
      // by passing it a uint 3rd parameter 
      uint proto = IPPROTO_TCP;
      mSocket64 = socket(AF_INET, SOCK_STREAM, proto);
      
      if (mSocket64 == INVALID_SOCKET64) {
         mLastWSAError = WSAGetLastError();
         #ifdef SOCKET_LIBRARY_LOGGING
            Print("socket() failed, 64-bit, error: ", mLastWSAError);
         #endif
         return;
      }
      uint nonblock = 1;
      ioctlsocket(mSocket64, FIONBIO, nonblock);

   } else {
      // Force compiler to use the 32-bit version of socket() 
      // by passing it a int 3rd parameter 
      int proto = IPPROTO_TCP;
      mSocket32 = socket(AF_INET, SOCK_STREAM, proto);
      
      if (mSocket32 == INVALID_SOCKET32) {
         mLastWSAError = WSAGetLastError();
         #ifdef SOCKET_LIBRARY_LOGGING
            Print("socket() failed, 32-bit, error: ", mLastWSAError);
         #endif
         return;
      }
      uint nonblock = 1;
      ioctlsocket(mSocket32, FIONBIO, nonblock);
   }

   // Try a bind
   sockaddr server;
   server.family = AF_INET;
   server.port = htons(serverport);
   server.address = (ForLocalhostOnly ? 0x100007f : 0); // 127.0.0.1 or INADDR_ANY

   if (TerminalInfoInteger(TERMINAL_X64)) {
      int bindres = bind(mSocket64, server, sizeof(sockaddr));
      if (bindres != 0) {
         // Bind failed
         mLastWSAError = WSAGetLastError();
         #ifdef SOCKET_LIBRARY_LOGGING
            Print("bind() failed, 64-bit, port probably already in use, error: ", mLastWSAError);
         #endif
         return;
         
      } else {
         int listenres = listen(mSocket64, 10);
         if (listenres != 0) {
            // Listen failed
            mLastWSAError = WSAGetLastError();
            #ifdef SOCKET_LIBRARY_LOGGING
               Print("listen() failed, 64-bit, error: ", mLastWSAError);
            #endif
            return;
            
         } else {
            mCreated = true;         
         }
      }
   } else {
      int bindres = bind(mSocket32, server, sizeof(sockaddr));
      if (bindres != 0) {
         // Bind failed
         mLastWSAError = WSAGetLastError();
         #ifdef SOCKET_LIBRARY_LOGGING
            Print("bind() failed, 32-bit, port probably already in use, error: ", mLastWSAError);
         #endif
         return;
         
      } else {
         int listenres = listen(mSocket32, 10);
         if (listenres != 0) {
            // Listen failed
            mLastWSAError = WSAGetLastError();
            #ifdef SOCKET_LIBRARY_LOGGING
               Print("listen() failed, 32-bit, error: ", mLastWSAError);
            #endif
            return;
            
         } else {
            mCreated = true;         
         }
      }
   }
   
   // Try settig up event handling; can fail here in constructor
   // if no window handle is available because it's being called 
   // from OnInit() while MT4/5 is loading
   #ifdef SOCKET_LIBRARY_USE_EVENTS
      SetupSocketEventHandling();
   #endif
}


// -------------------------------------------------------------
// Destructor. Close the socket if created
// -------------------------------------------------------------

ServerSocket::~ServerSocket()
{
   if (TerminalInfoInteger(TERMINAL_X64)) {
      if (mSocket64 != 0)  closesocket(mSocket64);
   } else {
      if (mSocket32 != 0)  closesocket(mSocket32);
   }   
}

// -------------------------------------------------------------
// Accepts any incoming connection. Returns either NULL,
// or an instance of ClientSocket
// -------------------------------------------------------------

ClientSocket * ServerSocket::Accept()
{
   if (!mCreated) return NULL;
   
   // Make sure that event handling is in place; can fail in constructor
   // if no window handle is available because it's being called 
   // from OnInit() while MT4/5 is loading
   #ifdef SOCKET_LIBRARY_USE_EVENTS
      SetupSocketEventHandling();
   #endif
   
   ClientSocket * pClient = NULL;

   if (TerminalInfoInteger(TERMINAL_X64)) {
      SOCKET_HANDLE64 acc = accept(mSocket64, 0, 0);
      if (acc != INVALID_SOCKET64) {
         pClient = new ClientSocket(NULL, acc);
      }
   } else {
      SOCKET_HANDLE32 acc = accept(mSocket32, 0, 0);
      if (acc != INVALID_SOCKET32) {
         pClient = new ClientSocket(NULL, acc);
      }
   }

   return pClient;
}

// -------------------------------------------------------------
// Event handling
// -------------------------------------------------------------

void ServerSocket::SetupSocketEventHandling()
{
   #ifdef SOCKET_LIBRARY_USE_EVENTS
      if (mDoneEventHandling) return;
   
      // Can only do event handling in an EA. Ignore otherwise.
      if (MQLInfoInteger(MQL_PROGRAM_TYPE) != PROGRAM_EXPERT) {
         mDoneEventHandling = true;
         return;
      }
    
      long hWnd = ChartGetInteger(0, CHART_WINDOW_HANDLE);
      if (!hWnd) return;
      mDoneEventHandling = true; // Don't actually care whether it succeeds.
      
      if (TerminalInfoInteger(TERMINAL_X64)) {
         WSAAsyncSelect(mSocket64, hWnd, 0x100 /* WM_KEYDOWN */, 0xFF /* All events */);
      } else {
         WSAAsyncSelect(mSocket32, (int)hWnd, 0x100 /* WM_KEYDOWN */, 0xFF /* All events */);
      }
   #endif
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
struct _openOrder
{
   bool OK;
   ulong ticket;
   ulong position_order_id;
   string message;
   uint resultCode;
};

struct _deal_Info{
   long     ticket;
   long     positionTicket;
   long     orderTicket;
   long     magicNumber;
   int      type;
   int      entry;
   string   comment;
   string   symbol;
   double   volume;
   double   price;
   double   swap;
   double   commission;
   double   profit;
   int      time;
};

struct position_info{

   long ticket;
   long orderTicket;
   long magicNumber;
   double openPrice;
   double closePrice;
   int openDate;
   double volume;
   double swap;
   double commission;
   int closeDate;
   double profit;
   string symbol;
   string comment;
   int type;

};

MqlTick arrayTicks[];



// -------------------------------------------------------------
// Forward definitions of classes
// -------------------------------------------------------------


class MT5_F000;                           // check for connection
class MT5_F001;                           // get static account info
class MT5_F002;                           // get dynamic account info
class MT5_F003;                           // get symbol info
class MT5_F004;                           // check fot instrument excistence

class MT5_F005;                           // get server time
class MT5_F007;                           // get symbol list

class MT5_F020;                           // get tick info

class MT5_F030;                           // get instrument market info
class MT5_F040;                           // get x bars from now
class MT5_F041;                           // get actual bar info

class MT5_F060;                           // get market orders
class MT5_F061;                           // get market positions

class MT5_F070;                           // place order
class MT5_F071;                           // close position by ticket
class MT5_F073;                           // delete order by ticket
class MT5_F075;                           // update sl & tp for position
class MT5_F076;                           // update sl & tp for order

class MT5_F000                            // check for connection
{
   private:
      
      // Other state variables
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F000();

      // Destructor
      ~MT5_F000();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F000, symbol rates
// -------------------------------------------------------------
MT5_F000::MT5_F000()
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F000::~MT5_F000()
{
   
}

string MT5_F000::Execute(string command)
{
string returnString = "";
   
   returnString = "F000#OK#!";
   
   return returnString;
}


class MT5_F001                                                       // get static account info
{
   private:
      
      // Other state variables
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F001();

      // Destructor
      ~MT5_F001();
      
      // Simple send and receive methods
      string Execute(string command);
};

// -------------------------------------------------------------
// Constructor for a F001, symbol rates
// -------------------------------------------------------------
MT5_F001::MT5_F001()
{
}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F001::~MT5_F001()
{
}

string MT5_F001::Execute(string command)
{
   string returnString = "";
   string split[];
      
   StringSplit(command,char('#'), split);

   returnString = "F001#9#";
   
   returnString = returnString + AccountInfoString(ACCOUNT_NAME) + "#";
   returnString = returnString + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)) + "#";
   returnString = returnString + AccountInfoString(ACCOUNT_CURRENCY) + "#";
   if (AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_DEMO) {
      returnString = returnString + "demo#";
   } else if (AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_REAL) {
      returnString = returnString + "real#";
   } else {
      returnString = returnString + "Unknown";
   }
   
   returnString = returnString + IntegerToString(AccountInfoInteger(ACCOUNT_LEVERAGE)) + "#";
   returnString = returnString + IntegerToString(AccountInfoInteger(ACCOUNT_TRADE_ALLOWED)) + "#";
   returnString = returnString + IntegerToString(AccountInfoInteger(ACCOUNT_LIMIT_ORDERS)) + "#";
   returnString = returnString + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN_SO_CALL)) + "#";
   returnString = returnString + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN_SO_SO), 2) + "#!";
   
   return returnString;
}

class MT5_F002                                                       // get dynamic account info
{
   private:
      // Other state variables
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F002();

      // Destructor
      ~MT5_F002();
      
      // Simple send and receive methods
      string Execute(string command);
};

// -------------------------------------------------------------
// Constructor for a F002, symbol rates
// -------------------------------------------------------------
MT5_F002::MT5_F002()
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------

MT5_F002::~MT5_F002()
{
   
}

string MT5_F002::Execute(string command)
{
   string returnString = "";
   string split[];

   StringSplit(command,char('#'), split);

   returnString = "F002#6#";
   
   returnString = returnString + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + "#";
   returnString = returnString + DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2) + "#";
   returnString = returnString + DoubleToString(AccountInfoDouble(ACCOUNT_PROFIT), 2) + "#";
   returnString = returnString + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN), 2) + "#";
   returnString = returnString + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN_LEVEL), 2) + "#";
   returnString = returnString + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN_FREE), 2) + "#!";
   
   return returnString;
}

class MT5_F003                                                       // get instrument info
{
   private:
      
      // Other state variables
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F003();

      // Destructor
      ~MT5_F003();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F003, symbol rates
// -------------------------------------------------------------
MT5_F003::MT5_F003()
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F003::~MT5_F003()
{
   
}

string MT5_F003::Execute(string command)
{
   string returnString = "";
   string split[];
   
   StringSplit(command,char('#'), split);
   string _symbol = split[2];
   // check for demo
   if (bDemo) {
      if (checkInstrumentsInDemo(_symbol) == false) {
         return "F998#2#Instrument not in demo version#0#!";     
      }   
   }

   RefreshRates();
   
   returnString = "F003#7#";
   
   returnString = returnString + IntegerToString(MarketInfo(_symbol, MODE_DIGITS)) + "#";
   returnString = returnString + DoubleToString(MarketInfo(_symbol, MODE_MAXLOT), 2) + "#";
   returnString = returnString + DoubleToString(MarketInfo(_symbol, MODE_MINLOT), 2) + "#";
   returnString = returnString + DoubleToString(MarketInfo(_symbol, MODE_LOTSTEP), 2) + "#";
   returnString = returnString + DoubleToString(MarketInfo(_symbol, MODE_POINT),5) + "#";
   returnString = returnString + DoubleToString(MarketInfo(_symbol, MODE_TICKSIZE), 6) + "#";
   returnString = returnString + DoubleToString(MarketInfo(_symbol, MODE_TICKVALUE), 6) + "#!";
   
   //Print(returnString);
   
   return returnString;
}

class MT5_F004                                                       // check if instrument exist for broker
{
   private:
      
      // Other state variables
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F004();

      // Destructor
      ~MT5_F004();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F004, symbol rates
// -------------------------------------------------------------
MT5_F004::MT5_F004()
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F004::~MT5_F004()
{
   
}

string MT5_F004::Execute(string command)
{
   string returnString = "";
   string split[];
      
   StringSplit(command,char('#'), split);
   string _symbol = split[2];
   // check for demo
   if (bDemo) {
      if (checkInstrumentsInDemo(_symbol) == false) {
         return "F998#2#Instrument not in demo version#0#!";     
      }   
   }


   returnString = "F004#";
   
   if (MarketInfo(_symbol, MODE_ASK) > 0.0)
   {
      returnString = "F004#1#OK#!";
   }
   else
   {
      returnString = "F998#2#Not known#0#!";
   }
   
   return returnString;
}

class MT5_F005                                                       // get broker server time
{
   private:
      
      // Other state variables
      MqlDateTime serverTime;
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F005();

      // Destructor
      ~MT5_F005();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F005, server time
// -------------------------------------------------------------
MT5_F005::MT5_F005()
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F005::~MT5_F005()
{
   
}

string MT5_F005::Execute(string command)
{
   string returnString = "";
   string split[];
   datetime now;
      
   now = TimeCurrent(serverTime);
   
   returnString = "F005#1#";
   returnString = returnString + IntegerToString(serverTime.year) + "-" + IntegerToString(serverTime.mon) + "-"  + IntegerToString(serverTime.day) + "-"; 
   returnString = returnString + IntegerToString(serverTime.hour) + "-" + IntegerToString(serverTime.min) + "-"  + IntegerToString(serverTime.sec); 
   returnString = returnString + "#!";
   
   return returnString;
}

class MT5_F007                                                      // get broker market symbol list
{
   private:
      
      // Other state variables
      //MqlDateTime serverTime;
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F007();

      // Destructor
      ~MT5_F007();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F004, symbol rates
// -------------------------------------------------------------
MT5_F007::MT5_F007()
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F007::~MT5_F007()
{
   
}

string MT5_F007::Execute(string command)
{
   string returnString = "";
   string split[];
   datetime now;
   bool bMarket = true;
   int iNbrOfSymbols = 0;
      
   StringSplit(command,char('#'), split);
   if ((int)StrToNumber(split[1]) == 0) bMarket = false;
   
   iNbrOfSymbols = SymbolsTotal(bMarket);
   
   returnString = "F007#" + IntegerToString(iNbrOfSymbols) + "#";
   
   for( int u = 0; u < iNbrOfSymbols; u++) {
      returnString = returnString + SymbolName(u, bMarket) + "#";
   }
   
   returnString = returnString + "!";    
   return returnString;
}

class MT5_F020                                                       // get last tick info
{
   private:
      
      // Other state variables

      MqlTick last_tick;
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F020();

      // Destructor
      ~MT5_F020();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F020, symbol rates
// -------------------------------------------------------------
MT5_F020::MT5_F020()
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F020::~MT5_F020()
{
   
}

string MT5_F020::Execute(string command)
{
   string returnString = "";
   string split[];
   
   
   StringSplit(command,char('#'), split);
   string _symbol = split[2];
   // check for demo
   if (bDemo) {
      if (checkInstrumentsInDemo(_symbol) == false) {
         return "F998#2#Instrument not in demo version#0#!";     
      }   
   }

   ResetLastError();
   if(SymbolInfoTick(_symbol, last_tick))
   {
      returnString = "F020#5#" + IntegerToString(last_tick.time) + "#" + DoubleToString(last_tick.ask,5) + "#" + DoubleToString(last_tick.bid,5) + "#" ;
      returnString = returnString + DoubleToString(last_tick.last,5) + "#" + IntegerToString(last_tick.volume) + "#!";
   }
   else
   {
      returnString = "F998#2#" + IntegerToString(GetLastError()) + "#0#!";
   }  

   
   return returnString;
}

class MT5_F021                                                       // get last x ticks from now
{
   private:
      
      // Other state variables

      MqlTick last_tick;
      MqlTick array[];
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F021();

      // Destructor
      ~MT5_F021();
      
      // Simple send and receive methods
      string Execute(string command);
      

};

// -------------------------------------------------------------
// Constructor for a F020, symbol rates
// -------------------------------------------------------------
MT5_F021::MT5_F021()
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F021::~MT5_F021()
{
   
}

string MT5_F021::Execute(string command)
{
   string returnString = "";
   
   returnString = "F998#2#Not implemented#0#!";

   return returnString;
}

class MT5_F042
{
   private:
      
      // Other state variables

      MqlRates tmpRates[];
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F042();

      // Destructor
      ~MT5_F042();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F042, symbol rates
// -------------------------------------------------------------
MT5_F042::MT5_F042()                                                 
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F042::~MT5_F042()
{
   
}

string MT5_F042::Execute(string command)
{
   string returnString = "";
   string _symbol;
   int timeFrame = 0;
   int iNbrOfBars = 0;
   int iBegin = 0;
   int _digits = 5;
   ENUM_TIMEFRAMES _timeFrame;
   string split[];
   
   
   StringSplit(command,char('#'), split);
   _symbol = split[2];
   // check for demo
   if (bDemo) {
      if (checkInstrumentsInDemo(_symbol) == false) {
         return "F998#2#Instrument not in demo version#0#!";     
      }   
   }
   _digits = MarketInfo(_symbol, MODE_DIGITS); //_symbolInfo.Digits();
   timeFrame = (int)StrToNumber(split[3]);
   iBegin = (int)StrToNumber(split[4]);
   iNbrOfBars = (int)StrToNumber(split[5]);
   _timeFrame = getTimeFrame(timeFrame);
   if (_timeFrame == -1) {
      return "F998#2#Wrong timeframe#" + _symbol + "#0#!";
   }
   
   ArrayResize(tmpRates, iNbrOfBars);
   ArrayResize(tmpRates, iNbrOfBars);

   ResetLastError();
   int iNbrOfRecords = CopyRates(_symbol, _timeFrame, iBegin, iNbrOfBars, tmpRates);

   if (iNbrOfRecords == -1)
   {
      return "F998#2#Error no records selected by server# " + IntegerToString(GetLastError()) + "#0#!";
   }
   else
   {
      //Print("Records:  " + nbrOfRecords);
      returnString = "F042#" + IntegerToString(iNbrOfRecords) + "#";
      for (int u = 0; u < iNbrOfRecords; u++)
      {
         returnString = returnString + IntegerToString(tmpRates[u].time) + "$" + DoubleToString(tmpRates[u].open,_digits) + "$" 
                           + DoubleToString(tmpRates[u].high,_digits) + "$" + DoubleToString(tmpRates[u].low,_digits) + "$" + DoubleToString(tmpRates[u].close,_digits) + "$"
                           + IntegerToString(tmpRates[u].tick_volume) + "#";
      }
      returnString = returnString + "!";
      
   }
   
   //Print(StringLen(returnString));
   //Print(TimeLocal());
   
   return returnString;
}

class MT5_F041
{
   private:
      
      // Other state variables
      MqlRates tmpRates[];
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F041();

      // Destructor
      ~MT5_F041();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F041, symbol rates
// -------------------------------------------------------------
MT5_F041::MT5_F041()
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F041::~MT5_F041()
{
   
}

string MT5_F041::Execute(string command)
{
   string returnString = "";
   string _symbol;
   int timeFrame = 0;
   int nbrOfBars = 0;
   int _digits = 5;
   ENUM_TIMEFRAMES _timeFrame;
   string split[];
   
   
   StringSplit(command,char('#'), split);
   _symbol = split[2];
   // check for demo
   if (bDemo) {
      if (checkInstrumentsInDemo(_symbol) == false) {
         return "F998#2#Instrument not in demo version#0#!";     
      }   
   }

   _digits = MarketInfo(_symbol, MODE_DIGITS); //_symbolInfo.Digits();
   timeFrame = (int)StrToNumber(split[3]);
   nbrOfBars = 1;
   _timeFrame = getTimeFrame(timeFrame);
   //Alert(timeFrame);
   if (_timeFrame == -1) {
      return "F998#2#Wrong timeframe#0#!";
   }
   
   ArrayResize(tmpRates, nbrOfBars);
   ResetLastError();
   int nbrOfRecords = CopyRates(_symbol, _timeFrame, 0, 1, tmpRates);
   if (nbrOfRecords == -1)
   {
      return "F998#2#Error no records selected by server# " + IntegerToString(GetLastError()) + "#" + _symbol + "#!";
   }
   else if (nbrOfRecords == 1)
   {
      returnString = "F041#" + IntegerToString(6) + "#";
      returnString = returnString + IntegerToString(tmpRates[0].time) + "#" + DoubleToString(tmpRates[0].open,_digits) + "#" 
                           + DoubleToString(tmpRates[0].high,_digits) + "#" + DoubleToString(tmpRates[0].low,_digits) + "#" + DoubleToString(tmpRates[0].close,_digits) + "#"
                           + IntegerToString(tmpRates[0].tick_volume) + "#";
      returnString = returnString + "!";
      
   }
   else
   {
      return "F998#2#Error#0#!";
   }
   
   return returnString;
}

class MT5_F045                                                      // get specific bars for list of instruments
{
   private:
      
      // Other state variables
      MqlRates tmpRates[];
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F045();

      // Destructor
      ~MT5_F045();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F041, symbol rates
// -------------------------------------------------------------
MT5_F045::MT5_F045()
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F045::~MT5_F045()
{
   
}

string MT5_F045::Execute(string command)
{
   
   //Print(command);
   string returnString = "";
   string _symbols;
   string _symbol = ";";
   int timeFrame = 0;
   int nbrOfBars = 0;
   int _digits = 5;
   int bar_index = 0;
   ENUM_TIMEFRAMES _timeFrame;
   string split[];
   string symbolSplit[];

   
   StringSplit(command,char('#'), split);
   _symbols = split[2];
   
   StringSplit(_symbols, char('$'), symbolSplit);
   //Print(symbolSplit[0]);
   bar_index = (int)StrToNumber(split[3]);
   timeFrame = (int)StrToNumber(split[4]);
   nbrOfBars = 2;
   _timeFrame = getTimeFrame(timeFrame);
   
   if (_timeFrame == -1) {
      return "F998#2#Wrong timeframe.#0#!";
   }   
   
   int iNbrOfSymbols = SymbolsTotal(true);
   for( int u = 0; u < iNbrOfSymbols; u++) {
      returnString = returnString + SymbolName(u, true) + "#";
   }  
   
   // check if all symbols are in marketwatch
   bool checkAll = true;
   bool checkSingle = false;
   for (int u = 0; u < ArraySize(symbolSplit)-1; u++) {
      _symbol = symbolSplit[u];
      // check for demo
      if (bDemo) {
         if (checkInstrumentsInDemo(_symbol) == false) {
            return "F998#2#Instrument not in demo version#0#!";     
         }   
      }
      checkSingle = false;
      for ( int uu = 0; uu < iNbrOfSymbols; uu++) {
         if (_symbol == SymbolName(uu, true)) {
            checkSingle = true;
         }
      }
      if (checkSingle == false) {checkAll = false; break;}
   }
   
   if (checkAll == false) {
      returnString = "F998#2#Missing market symbols#0#!";
      return returnString;
   }
   
   ArrayResize(tmpRates, nbrOfBars);
   ResetLastError();
   
   returnString = "F045#" + IntegerToString(ArraySize(symbolSplit)-1) + "#";
   //Print(returnString);
   
   for (int u = 0; u < ArraySize(symbolSplit)-1; u++) {  
      _symbol = symbolSplit[u];
      RefreshRates();
      
      _digits = (int)MarketInfo(_symbol, MODE_DIGITS); //_symbolInfo.Digits();
      int nbrOfRecords = CopyRates(_symbol, _timeFrame, bar_index, 1, tmpRates);
      if (nbrOfRecords == -1) {
         return "F998#2#Error no records selected by server# " + IntegerToString(GetLastError()) + "#" + _symbol + "#!";
      }
      else if (nbrOfRecords == 1) {
      
         returnString = returnString + _symbol + "$";
         returnString = returnString + IntegerToString(tmpRates[0].time) + "$" + DoubleToString(tmpRates[0].open,_digits) + "$" 
                              + DoubleToString(tmpRates[0].high,_digits) + "$" + DoubleToString(tmpRates[0].low,_digits) + "$" 
                              + DoubleToString(tmpRates[0].close,_digits) + "$"
                              + IntegerToString(tmpRates[0].tick_volume) + "#";
      }      
   }
   //Print(returnString);
   returnString = returnString + "!"; 
   return returnString;
}

class MT5_F060
{
   private:
      
      // Other state variables
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F060();

      // Destructor
      ~MT5_F060();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F060, symbol rates
// -------------------------------------------------------------
MT5_F060::MT5_F060()
{

}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F060::~MT5_F060()
{
   
}

string MT5_F060::Execute(string command)
{
   string returnString = "";
      
   int nbrOfOrders = OrdersTotal();
   if (nbrOfOrders == 0)
   {
      returnString = "F060#0#!";
      return returnString;
   }
   // count number of pendings
   int counter = 0;
   for (int u = nbrOfOrders-1; u >= 0; u--) {
      if (OrderSelect(u, SELECT_BY_POS, MODE_TRADES) == true) {
         if (OrderType() != OP_BUY && OrderType() != OP_SELL)
         {
            counter++;
         }
      }
   }
   
   returnString = "F060#" + IntegerToString(counter) + "#";
   
   for (int u = nbrOfOrders-1; u >= 0; u--)
   {
      if (OrderSelect(u, SELECT_BY_POS, MODE_TRADES) == true) {
         ulong    orderTicket          = OrderTicket();
         long     orderType            = OrderType(); //OrderGetInteger(ORDER_TYPE);
         string   orderSymbol          = OrderSymbol(); //OrderGetString(ORDER_SYMBOL);
         string   orderComment         = OrderComment(); //OrderGetString(ORDER_COMMENT);
         long     orderMagic           = OrderMagicNumber(); //OrderGetInteger(ORDER_MAGIC);
         double   orderLots            = OrderLots(); //OrderGetDouble(ORDER_VOLUME_INITIAL);
         double   orderSL              = OrderStopLoss(); //OrderGetDouble(ORDER_SL);
         double   orderTP              = OrderTakeProfit(); //OrderGetDouble(ORDER_TP);
         double   orderOpenPrice       = OrderOpenPrice(); //OrderGetDouble(ORDER_PRICE_OPEN);
         
         string _comment = filterComment(orderComment);
         
         if (orderType != OP_BUY && orderType != OP_SELL) {
            returnString = returnString + IntegerToString(orderTicket) + "$" + orderSymbol + "$" ;
            if (orderType == ORDER_TYPE_BUY_STOP) returnString = returnString + "buy_stop$";
            else if (orderType == ORDER_TYPE_SELL_STOP) returnString = returnString + "sell_stop$";
            else if (orderType == ORDER_TYPE_BUY_LIMIT) returnString = returnString + "buy_limit$";
            else if (orderType == ORDER_TYPE_SELL_LIMIT) returnString = returnString + "sell_limit$";
            else returnString = returnString + "unknown$";
            returnString = returnString + IntegerToString(orderMagic) + "$" + DoubleToString(orderLots, 5) + "$" + DoubleToString(orderOpenPrice, 5) + "$";
            returnString = returnString + DoubleToString(orderSL, 5) + "$" + DoubleToString(orderTP, 5) + "$" + _comment + "#";
         }
      }
   }
   returnString = returnString + "!";
   
   return returnString;
}

class MT5_F061
{
   private:
      
      // Other state variables     
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F061();

      // Destructor
      ~MT5_F061();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F061, symbol rates
// -------------------------------------------------------------
MT5_F061::MT5_F061()
{

}
// -------------------------------------------------------------
// Destructor.
// -------------------------------------------------------------
MT5_F061::~MT5_F061()
{
   
}

string MT5_F061::Execute(string command)
{
   string returnString = "";
      
   int nbrOfPositions = OrdersTotal();
   if (nbrOfPositions == 0)
   {
      returnString = "F061#0#!";
      return returnString;
   }
   returnString = "F061#" + IntegerToString(nbrOfPositions) + "#";
   
   for (int u = nbrOfPositions-1; u >= 0; u--) {
      if (OrderSelect(u, SELECT_BY_POS, MODE_TRADES) == true) {
         if (OrderType() == OP_BUY || OrderType() == OP_SELL) {
         
            ulong    positionTicket          = OrderTicket();
            long     positionType            = OrderType();
            string   positionSymbol          = OrderSymbol();
            string   positionComment         = OrderComment();;
            long     positionMagic           = OrderMagicNumber();
            double   positionLots            = OrderLots();
            double   positionSL              = OrderStopLoss();
            double   positionTP              = OrderTakeProfit();
            double   positionOpenPrice       = OrderOpenPrice();
            double   positionProfit          = OrderProfit();
            double   positionSwap            = OrderSwap();
            double   positionCommission      = OrderCommission();
            datetime positionOpenTime        = OrderOpenTime();
            
            string _comment = filterComment(positionComment);
            
            returnString = returnString + IntegerToString(positionTicket) + "$" + positionSymbol + "$" ;
            if (positionType == OP_BUY) returnString = returnString + "buy$";
            else if (positionType == OP_SELL) returnString = returnString + "sell$";
            else returnString = returnString + "unknown$";
            
            returnString = returnString + IntegerToString(positionMagic) + "$" + DoubleToString(positionLots, 5) + "$" + DoubleToString(positionOpenPrice, 5) + "$";
            returnString = returnString + IntegerToString(positionOpenTime) + "$" + DoubleToString(positionSL, 5) + "$" + DoubleToString(positionTP, 5) 
                     + "$" + _comment + "$" + DoubleToString(positionProfit, 2) + "$" + DoubleToString(positionSwap,2) + "$" + DoubleToString(positionCommission,2) + "#";
         }
      }
      
   }
   returnString = returnString + "!";
   
   return returnString;
}

class MT5_F062
{
   private:
      
      // Other state variables
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F062();

      // Destructor
      ~MT5_F062();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F062, historical positions
// -------------------------------------------------------------
MT5_F062::MT5_F062()
{

}
// -------------------------------------------------------------
// Destructor.
// -------------------------------------------------------------
MT5_F062::~MT5_F062()
{
   
}

string MT5_F062::Execute(string command)
{
   string returnString = "";
   string split[];
   string split_2[];
   MqlDateTime begin;
   MqlDateTime end;
   datetime beginDate, endDate, selectDate;
   
   position_info positions[];
   
   StringSplit(command, char('#'), split);
   // start date
   StringSplit(split[2], char('/'), split_2);
   begin.year = (int) StrToNumber(split_2[0]);
   if (begin.year < 2010) begin.year = 2010;
   begin.mon = (int) StrToNumber(split_2[1]);
   begin.day = (int) StrToNumber(split_2[2]);
   begin.hour = (int) StrToNumber(split_2[3]);
   begin.min = (int) StrToNumber(split_2[4]);
   begin.sec = (int) StrToNumber(split_2[5]);
   // end date
   StringSplit(split[3], char('/'), split_2);
   end.year = (int) StrToNumber(split_2[0]);
   end.mon = (int) StrToNumber(split_2[1]);
   end.day = (int) StrToNumber(split_2[2]);
   end.hour = (int) StrToNumber(split_2[3]);
   end.min = (int) StrToNumber(split_2[4]);
   end.sec = (int) StrToNumber(split_2[5]);
   
   
   if (StructToTime(end) < StructToTime(begin)) {
      returnString = "F998#2#Wrong period selection#0#!";
      return returnString;
   }
   
   beginDate = StructToTime(begin);
   endDate = StructToTime(end);

   int nbrOfHistoricalOrders = OrdersHistoryTotal();
   Print(nbrOfHistoricalOrders);
   int iCounter = 0;
   ArrayResize(positions, 0);
   for (int u = 0;  u < nbrOfHistoricalOrders-1; u++) {
      if (OrderSelect(u, SELECT_BY_POS, MODE_HISTORY) == true) {
         if (OrderCloseTime() >= beginDate && OrderCloseTime() < endDate) {
            if (OrderType() == OP_BUY || OrderType() == OP_SELL) {
               ArrayResize(positions, ArraySize(positions) + 1);
               positions[iCounter].ticket = OrderTicket();
               positions[iCounter].orderTicket = OrderTicket();
               positions[iCounter].symbol = OrderSymbol();
               positions[iCounter].volume = OrderLots();
               positions[iCounter].comment = OrderComment();
               positions[iCounter].magicNumber = OrderMagicNumber();
               positions[iCounter].type = OrderType();
               positions[iCounter].openDate = OrderOpenTime();
               positions[iCounter].openPrice = OrderOpenPrice();
               positions[iCounter].closePrice = OrderClosePrice();
               positions[iCounter].closeDate = OrderCloseTime();
               positions[iCounter].profit = OrderProfit();
               positions[iCounter].swap = OrderSwap();
               positions[iCounter].commission = OrderCommission();
               iCounter++;
            }
         }
      }
   }
   
   // build return string
   returnString = "F062#" + IntegerToString(ArraySize(positions)) + "#";
   for (int u = 0; u < ArraySize(positions); u++){
      returnString = returnString + IntegerToString(positions[u].ticket) + "$" + positions[u].symbol + "$" + IntegerToString(positions[u].orderTicket) + "$";
      if (positions[u].type == OP_BUY) { 
         returnString = returnString + "buy$";
      } else {
         returnString = returnString + "sell$";
      }
      string _comment = filterComment(positions[u].comment);
      returnString = returnString + IntegerToString(positions[u].magicNumber) + "$" + DoubleToString(positions[u].volume,2) + "$" + DoubleToString(positions[u].openPrice, 5) + "$";
      returnString = returnString + IntegerToString(positions[u].openDate) + "$" + DoubleToString(positions[u].closePrice, 5) + "$"  + IntegerToString(positions[u].closeDate) + "$";
      returnString = returnString + _comment + "$";
      returnString = returnString + DoubleToString(positions[u].profit,2) + "$" + DoubleToString(positions[u].swap,2) + "$" + DoubleToString(positions[u].commission,2) +"#";
   }
   
   returnString = returnString + "!";
   
   return returnString;
}

class MT5_F070                                                       // open an order
{
   private:
      
      // Other state variables
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F070();

      // Destructor
      ~MT5_F070();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F070, 
// -------------------------------------------------------------
MT5_F070::MT5_F070()
{
}
// -------------------------------------------------------------
// Destructor.
// -------------------------------------------------------------
MT5_F070::~MT5_F070()
{
}

string MT5_F070::Execute(string command)
{
   string returnString = "";
   string split[];
   double orderVolume, orderOpenPrice, orderStopLoss, orderTakeProfit;
   string _symbol, orderComment;
   long orderMagicNumber;
   int orderSlippage = 0;
   int ticket = -1;
   ENUM_ORDER_TYPE orderType;
   
   
   // check for trades allowed
   if (!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED))
   {
      return "F998#2#Trading not allowed for terminal/or EA.#0#!";
   }

   
   StringSplit(command, char('#'), split);
   _symbol = split[2];
   // check for demo
   if (bDemo) {
      if (checkInstrumentsInDemo(_symbol) == false) {
         return "F998#2#Instrument not in demo version#0#!";     
      }   
   }
   RefreshRates();
   
   if (split[3] == "buy") orderType = ORDER_TYPE_BUY;
   else if (split[3] == "sell") orderType = ORDER_TYPE_SELL;
   else if (split[3] == "buy_stop") orderType = ORDER_TYPE_BUY_STOP;
   else if (split[3] == "sell_stop") orderType = ORDER_TYPE_SELL_STOP;
   else if (split[3] == "buy_limit") orderType = ORDER_TYPE_BUY_LIMIT;
   else if (split[3] == "sell_limit") orderType = ORDER_TYPE_SELL_LIMIT;
   else
   {
      // unknow order type
      returnString = "F998#2#Unknown order type.#0#!";
      return returnString;
   }
   orderVolume = StrToNumber(split[4]);
   orderOpenPrice = StrToNumber(split[5]);
   orderSlippage = (int)StrToNumber(split[6]);
   orderMagicNumber = (long)StrToNumber(split[7]);
   orderStopLoss = StrToNumber(split[8]);
   orderTakeProfit = StrToNumber(split[9]);
   orderComment = split[10];
   
   string _comment = filterComment(orderComment);
   
   // check consistancy for parameters
   if (orderVolume > MarketInfo(_symbol, MODE_MAXLOT) || orderVolume < MarketInfo(_symbol, MODE_MINLOT)) return "F998#2#Wrong volume.#0#!";
   
   if (orderType == ORDER_TYPE_BUY && orderStopLoss != 0.0)
   {
      if (orderStopLoss >= MarketInfo(_symbol, MODE_ASK)) return "F998#2#Wrong stop loss.#0#!";
   }
   if (orderType == ORDER_TYPE_BUY && orderTakeProfit != 0.0)
   {
      if (orderTakeProfit <= MarketInfo(_symbol, MODE_ASK)) return "F998#2#Wrong take profit.#0#!";
   }
   if (orderType == ORDER_TYPE_SELL && orderStopLoss != 0.0)
   {
      if (orderStopLoss <= MarketInfo(_symbol, MODE_BID)) return "F998#2#Wrong stop loss.#0#!";
   }
   if (orderType == ORDER_TYPE_SELL && orderTakeProfit != 0.0)
   {
      if (orderTakeProfit >= MarketInfo(_symbol, MODE_BID)) return "F998#2#Wrong take profit.#0#!";
   }
   
   if (orderType == ORDER_TYPE_BUY_STOP && (orderTakeProfit < orderOpenPrice && orderTakeProfit != 0.0)) return "F998#2#Wrong take profit.#0#!";
   if (orderType == ORDER_TYPE_BUY_STOP && (orderStopLoss > orderOpenPrice && orderStopLoss != 0.0)) return "F998#2#Wrong stop loss.#0#!";
   
   if (orderType == ORDER_TYPE_SELL_STOP && (orderTakeProfit > orderOpenPrice && orderTakeProfit != 0.0)) return "F998#2#Wrong take profit.#0#!";
   if (orderType == ORDER_TYPE_SELL_STOP && (orderStopLoss < orderOpenPrice && orderStopLoss != 0.0)) return "F998#2#Wrong take profit.#0#!";

   if (orderType == ORDER_TYPE_BUY_LIMIT && (orderTakeProfit < orderOpenPrice && orderTakeProfit != 0.0)) return "F998#2#Wrong take profit.#0#!";
   if (orderType == ORDER_TYPE_BUY_LIMIT && (orderStopLoss > orderOpenPrice && orderStopLoss != 0.0)) return "F998#2#Wrong stop loss.#0#!";
   
   if (orderType == ORDER_TYPE_SELL_LIMIT && (orderTakeProfit > orderOpenPrice && orderTakeProfit != 0.0)) return "F998#2#Wrong take profit.#0#!";
   if (orderType == ORDER_TYPE_SELL_LIMIT && (orderStopLoss < orderOpenPrice && orderStopLoss != 0.0)) return "F998#2#Wrong stop loss or take profit.#0#!";
   
   ResetLastError();
   ticket = tlbOrderSendReliable(_symbol, orderType, orderVolume, orderOpenPrice, orderSlippage, orderStopLoss, orderTakeProfit, orderMagicNumber, _comment, 0, 0);
   if (ticket > 0)
   {
      returnString = "F070#2#" + IntegerToString(ticket) + "#" + "OK" + "#!";
   }
   else
   {
      returnString = "F998#2#" + "Error opening order.#" + IntegerToString(errorNumber) + "#!";
   }
   
   return returnString;
}


class MT5_F071                         // --------------------------------------------------------close position by ticket
{
   private:
      
      // Other state variables
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F071();

      // Destructor
      ~MT5_F071();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F071, symbol rates
// -------------------------------------------------------------
MT5_F071::MT5_F071()
{
}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F071::~MT5_F071()
{
}

string MT5_F071::Execute(string command)
{
   string returnString;
   string split[];
   ulong ticket;
   
   
   StringSplit(command, char('#'), split);
   ticket = (ulong)StrToNumber(split[2]);
   
   ResetLastError();
   if (OrderSelect(ticket, SELECT_BY_TICKET, MODE_TRADES) == true) {
   
      bool OK = tlbOrderCloseReliable(ticket, OrderLots(), 5, 0);
      if (OK == true) {
         returnString = "F071#1#OK#!";
      } else {
         returnString = "F988#2#Error in closing position.#" + IntegerToString(errorNumber) + "#!";
      }
   }
   
   return returnString;
}

class MT5_F072                         // --------------------------------------------------------partly close position by ticket
{
   private:
      
      // Other state variables
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F072();

      // Destructor
      ~MT5_F072();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F071, symbol rates
// -------------------------------------------------------------
MT5_F072::MT5_F072()
{
}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------
MT5_F072::~MT5_F072()
{
}

string MT5_F072::Execute(string command)
{
   string returnString;
   string split[];
   ulong ticket;
   int _digits = 2;
   double volume_to_close = 0.0;
   

   // check for trades allowed
   if (!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED))
   {
      return "F998#2#Trading not allowed for terminal/or EA.#0#!";
   }
   
   StringSplit(command, char('#'), split);
   ticket = (ulong)StrToNumber(split[2]);
   volume_to_close = (double)StrToNumber(split[3]);   
   
   
   ResetLastError();
   if (OrderSelect(ticket, SELECT_BY_TICKET, MODE_TRADES) == true)
   {
      string _symbol = OrderSymbol();
      double _volume = OrderLots();
      if (volume_to_close < MarketInfo(_symbol, MODE_MINLOT)) {
         volume_to_close = MarketInfo(_symbol, MODE_MINLOT);
      }
      if (volume_to_close > MarketInfo(_symbol, MODE_MAXLOT)) return "F998#2#Wrong volume.#0#!";
      if (volume_to_close >= _volume) {return "F998#2#Wrong volume.#0#!";}
      // normalize volume
      double tmpValue = MarketInfo(_symbol, MODE_LOTSTEP);
      if (tmpValue >= 1.0) {_digits = 0;}
      if (tmpValue >= 0.1 && tmpValue < 1.0) {_digits = 1;}
      if (tmpValue == 0.01) {_digits = 2;}
      volume_to_close = NormalizeDouble(volume_to_close, _digits);
      
      bool OK = tlbOrderCloseReliable(ticket, volume_to_close, 5, 0);
      
      if (OK == true) {
         returnString = "F072#1#OK#!";
      } else {
         returnString = "F988#2#Error in closing position.#" + IntegerToString(errorNumber) + "#!";
      }
   }
   
   return returnString;
   
}





class MT5_F073                         // --------------------------------------------------------delete order by ticket
{
   private:
      // Other state variables
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F073();

      // Destructor
      ~MT5_F073();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F073, symbol rates
// -------------------------------------------------------------
MT5_F073::MT5_F073()
{
}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------

MT5_F073::~MT5_F073()
{
}

string MT5_F073::Execute(string command)
{
   string returnString;
   string split[];
   ulong ticket;
   
   
   StringSplit(command, char('#'), split);
   ticket = (ulong)StrToNumber(split[2]);
   
   ResetLastError();
   bool OK = tlbOrderDeleteReliable(ticket);
   
   if (OK == true) {
      returnString = "F073#1#OK#!";   
   } else {
   //Print("Test: " + GetLastError());
      returnString = "F988#2#Error in deleting order.#" + IntegerToString(errorNumber) + "#!";
   }
   
   return returnString;
}

class MT5_F075                         // --------------------------------------------------------update sl & tp for position
{
   private:
      // Other state variables
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F075();

      // Destructor
      ~MT5_F075();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F073, symbol rates
// -------------------------------------------------------------
MT5_F075::MT5_F075()
{
}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------

MT5_F075::~MT5_F075()
{
}

string MT5_F075::Execute(string command)
{
   string returnString;
   string split[];
   ulong ticket;
   double sl, tp;
   ulong positionTicket;
   
   
   StringSplit(command, char('#'), split);
   ticket = (ulong)StrToNumber(split[2]);
   sl = StrToNumber(split[3]);
   tp = StrToNumber(split[4]);
   
   ResetLastError();
   if (OrderSelect(ticket, SELECT_BY_TICKET, MODE_TRADES) == true) {
      if (sl == 0.0 && tp != 0.0) {
         tp = NormalizeDouble(tp, MarketInfo(OrderSymbol(), MODE_DIGITS));
         bool OK = OrderModify(ticket, OrderOpenPrice(), OrderStopLoss(), tp, 0, 0);
         if (OK == true) {
            returnString = "F075#1#OK#!";
         } else {
            returnString = "F988#2#Error in modifying sl/tp.#" + IntegerToString(::GetLastError()) + "#!";
         }
      } else if (sl != 0.0 && tp == 0.0) {
         sl = NormalizeDouble(sl, MarketInfo(OrderSymbol(), MODE_DIGITS));
         bool OK = OrderModify(ticket, OrderOpenPrice(), sl, OrderTakeProfit(), 0, 0);
         if (OK == true) {
            returnString = "F075#1#OK#!";
         } else {
            returnString = "F988#2#Error in modifying sl/tp.#" + IntegerToString(::GetLastError()) + "#!";
         }
      } else if (sl != 0.0 && tp != 0.0) {
         tp = NormalizeDouble(tp, MarketInfo(OrderSymbol(), MODE_DIGITS));
         sl = NormalizeDouble(sl, MarketInfo(OrderSymbol(), MODE_DIGITS));
         bool OK = OrderModify(ticket, OrderOpenPrice(), OrderStopLoss(), OrderTakeProfit(), 0, 0);
         if (OK == true) {
            returnString = "F075#1#OK#!";
         } else {
            returnString = "F988#2#Error in modifying sl/tp.#" + IntegerToString(::GetLastError()) + "#!";
         }
      } else {
         returnString = "F075#1#OK#!";
      }
   }

   return returnString;
}

class MT5_F076                         // --------------------------------------------------------update sl & tp for order
{
   private:
      
      // Other state variables
      
   public:
      
      // Constructors for connecting to a server, either locally or remotely
      MT5_F076();

      // Destructor
      ~MT5_F076();
      
      // Simple send and receive methods
      string Execute(string command);

};

// -------------------------------------------------------------
// Constructor for a F073, symbol rates
// -------------------------------------------------------------
MT5_F076::MT5_F076()
{
}
// -------------------------------------------------------------
// Destructor. 
// -------------------------------------------------------------

MT5_F076::~MT5_F076()
{
}

string MT5_F076::Execute(string command)
{
   string returnString;
   string split[];
   ulong ticket;
   double sl, tp;
   ulong orderTicket;
   
   
   StringSplit(command, char('#'), split);
   ticket = (int)StrToNumber(split[2]);
   sl = StrToNumber(split[3]);
   tp = StrToNumber(split[4]);
   
   ResetLastError();
   if (OrderSelect(ticket, SELECT_BY_TICKET, MODE_TRADES) == true) {
      if (sl == 0.0 && tp != 0.0) {
         tp = NormalizeDouble(tp, MarketInfo(OrderSymbol(), MODE_DIGITS));
         bool OK = OrderModify(ticket, OrderOpenPrice(), OrderStopLoss(), tp, 0, 0);
         if (OK == true) {
            returnString = "F075#1#OK#!";
         } else {
            returnString = "F988#2#Error in modifying sl/tp.#" + IntegerToString(::GetLastError()) + "#!";
         }
      } else if (sl != 0.0 && tp == 0.0) {
         sl = NormalizeDouble(sl, MarketInfo(OrderSymbol(), MODE_DIGITS));
         bool OK = OrderModify(ticket, OrderOpenPrice(), sl, OrderTakeProfit(), 0, 0);
         if (OK == true) {
            returnString = "F075#1#OK#!";
         } else {
            returnString = "F988#2#Error in modifying sl/tp.#" + IntegerToString(::GetLastError()) + "#!";
         }
      } else if (sl != 0.0 && tp != 0.0) {
         tp = NormalizeDouble(tp, MarketInfo(OrderSymbol(), MODE_DIGITS));
         sl = NormalizeDouble(sl, MarketInfo(OrderSymbol(), MODE_DIGITS));
         bool OK = OrderModify(ticket, OrderOpenPrice(), OrderStopLoss(), OrderTakeProfit(), 0, 0);
         if (OK == true) {
            returnString = "F075#1#OK#!";
         } else {
            returnString = "F988#2#Error in modifying sl/tp.#" + IntegerToString(::GetLastError()) + "#!";
         }
      } else {
         returnString = "F075#1#OK#!";
      }
   }
   
   return returnString;
}


//+------------------------------------------------------------------+
double StrToNumber(string str)  {
//+------------------------------------------------------------------+
// Usage: strips all non-numeric characters out of a string, to return a numeric (double) value
//  valid numeric characters are digits 0,1,2,3,4,5,6,7,8,9, decimal point (.) and minus sign (-)
// Example: StrToNumber("the balance is $-34,567.98") returns the numeric value -34567.98
  int    dp   = -1;
  int    sgn  = 1;
  double num  = 0.0;
  for (int i=0; i<StringLen(str); i++)  
  {
    string s = StringSubstr(str,i,1);
    if (s == "-")  sgn = -sgn;   else
    if (s == ".")  dp = 0;       else
    if (s >= "0" && s <= "9")  {
      if (dp >= 0)  dp++;
      if (dp > 0)
        num = num + StringToInteger(s) / MathPow(10,dp);
      else
        num = num * 10 + StringToInteger(s);
    }
  }
  return(num*sgn);
}

ENUM_TIMEFRAMES getTimeFrame(int frame)
{
   //Print("Frame:  " + frame);
   if (frame == 1) return PERIOD_M1;
   if (frame == 5) return PERIOD_M5;
   if (frame == 15) return PERIOD_M15;
   if (frame == 30) return PERIOD_M30;
   if (frame == 16385) return PERIOD_H1;
   if (frame == 16388) return PERIOD_H4;
   if (frame == 16408) return PERIOD_D1;
   if (frame == 32769) return PERIOD_W1;
   return -1;
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
MT5_F000 mt5_f000 = MT5_F000();
MT5_F001 mt5_f001 = MT5_F001();
MT5_F002 mt5_f002 = MT5_F002();
MT5_F003 mt5_f003 = MT5_F003();
MT5_F004 mt5_f004 = MT5_F004();
MT5_F005 mt5_f005 = MT5_F005();
MT5_F007 mt5_f007 = MT5_F007();

// ticket classes
MT5_F020 mt5_f020 = MT5_F020();
MT5_F021 mt5_f021 = MT5_F021();

// bar classes
MT5_F042 mt5_f042 = MT5_F042();
MT5_F041 mt5_f041 = MT5_F041();
MT5_F045 mt5_f045 = MT5_F045();

// orders and positions info retrieval
MT5_F060 mt5_f060 = MT5_F060();
MT5_F061 mt5_f061 = MT5_F061();
MT5_F062 mt5_f062 = MT5_F062();

MT5_F070 mt5_f070 = MT5_F070();
MT5_F071 mt5_f071 = MT5_F071();
MT5_F072 mt5_f072 = MT5_F072();
MT5_F073 mt5_f073 = MT5_F073();

MT5_F075 mt5_f075 = MT5_F075();
MT5_F076 mt5_f076 = MT5_F076();

// --------------------------------------------------------------------
// EA user inputs
// --------------------------------------------------------------------
input ushort   ServerPort = 1122;           // Prefer server port < 10000
input string   subFolder         = "Market\\";         // Subfolder for authorization indicator


// --------------------------------------------------------------------
// Global variables and constants
// --------------------------------------------------------------------

// Frequency for EventSetMillisecondTimer(). Doesn't need to 
// be very frequent, because it is just a back-up for the 
// event-driven handling in OnChartEvent()
#define TIMER_FREQUENCY_MS    500

// Server socket
ServerSocket * glbServerSocket = NULL;

// Array of current clients
ClientSocket * glbClients[];

// Watch for need to create timer;
bool glbCreatedTimer = false;

int errorNumber = 0;

string comment;
bool newBar;

bool bDemo = false;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // If the EA is being reloaded, e.g. because of change of timeframe,
   // then we may already have done all the setup. See the 
   // termination code in OnDeinit.
   
   // check for dll are allowed
   int _dll = TerminalInfoInteger(TERMINAL_DLLS_ALLOWED);
   if ((bool)_dll == false)
   {
      Alert("Allow DLL import");
      return(INIT_FAILED);
   }
   
   string authorIndi = subFolder + "pytrader_MT4";

   // read the settings from the indicator
   double _port = iCustom(NULL, 0, authorIndi, ServerPort, 0, 0);

   if (_port > 0) 
   {
      Print("Port: " + _port);     
      double _value = iCustom(NULL, 0, authorIndi, ServerPort, 4, 0);
      if (_value != 999) {     
         Alert("EA working in demo.");
         bDemo = true;
         _port = ServerPort;
      }
      else {
         bDemo = false;
      }      
   }
   else 
   {         
      Alert("EA working in demo.");
      bDemo = true;
      _port = ServerPort;
   }
   EventSetTimer(1);
   
   if (glbServerSocket) 
   {
      Print("Reloading EA with existing server socket");
   } 
   else 
   {
      // Create the server socket
      glbServerSocket = new ServerSocket(_port, false);
      if (glbServerSocket.Created()) 
      {
         Print("Server socket created");
   
         // Note: this can fail if MT4/5 starts up
         // with the EA already attached to a chart. Therefore,
         // we repeat in OnTick()
         glbCreatedTimer = EventSetMillisecondTimer(TIMER_FREQUENCY_MS);
      } 
      else 
      {
         Print("Server socket FAILED - is the port already in use?");
      }
   }   
   
   
   comment = "";
   if (bDemo == false) {
      comment = comment + "\r\nPytrader MT4 server (licensed), port#: " + IntegerToString(ServerPort);
   }
   else {
      comment = comment + "\r\nPytrader MT4 server (demo), port#: " + IntegerToString(ServerPort);
   }
   Comment(comment);
      
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
// --------------------------------------------------------------------
// Termination - free server socket and any clients
// --------------------------------------------------------------------
void OnDeinit(const int reason)
{
   Comment("");
   switch (reason) {
      case REASON_CHARTCHANGE:
         // Keep the server socket and all its clients if 
         // the EA is going to be reloaded because of a 
         // change to chart symbol or timeframe 
         break;
         
      default:
         // For any other unload of the EA, delete the 
         // server socket and all the clients 
         glbCreatedTimer = false;
         
         // Delete all clients currently connected
         for (int i = 0; i < ArraySize(glbClients); i++) {
            delete glbClients[i];
         }
         ArrayResize(glbClients, 0);
      
         // Free the server socket. *VERY* important, or else
         // the port number remains in use and un-reusable until
         // MT4/5 is shut down
         delete glbServerSocket;
         Print("Server socket terminated");
         break;
   }

}

// --------------------------------------------------------------------
// Use OnTick() to watch for failure to create the timer in OnInit()
// --------------------------------------------------------------------
void OnTick()
{
   if (!glbCreatedTimer) glbCreatedTimer = EventSetMillisecondTimer(TIMER_FREQUENCY_MS);
}

// --------------------------------------------------------------------
// Timer - accept new connections, and handle incoming data from clients.
// Secondary to the event-driven handling via OnChartEvent(). Most
// socket events should be picked up faster through OnChartEvent()
// rather than being first detected in OnTimer()
// --------------------------------------------------------------------
void OnTimer()
{
   
   // Accept any new pending connections
   //AcceptNewConnections();
   
   // Process any incoming data on each client socket,
   // bearing in mind that HandleSocketIncomingData()
   // can delete sockets and reduce the size of the array
   // if a socket has been closed

   for (int i = ArraySize(glbClients) - 1; i >= 0; i--) {
      HandleSocketIncomingData(i);
   }
   
   
}
//+------------------------------------------------------------------+
//| Trade function                                                   |
//+------------------------------------------------------------------+
void OnTrade()
{
//---
   
}

// --------------------------------------------------------------------
// Event-driven functionality, turned on by #defining SOCKET_LIBRARY_USE_EVENTS
// before including the socket library. This generates dummy key-down
// messages when socket activity occurs, with lparam being the 
// .GetSocketHandle()
// --------------------------------------------------------------------

void OnChartEvent(const int id, const long& lparam, const double& dparam, const string& sparam)
{
   if (id == CHARTEVENT_KEYDOWN) 
   {
      // If the lparam matches a .GetSocketHandle(), then it's a dummy
      // key press indicating that there's socket activity. Otherwise,
      // it's a real key press
         
      if (lparam == glbServerSocket.GetSocketHandle()) 
      {
         // Activity on server socket. Accept new connections
         Print("Chart event -- New server socket event - incoming connection");
         AcceptNewConnections();

      } else 
      {
         // Compare lparam to each client socket handle
         for (int i = 0; i < ArraySize(glbClients); i++) 
         {
            if (lparam == glbClients[i].GetSocketHandle()) 
            {
               HandleSocketIncomingData(i);
               return; // Early exit
            }
         }
         
         // If we get here, then the key press does not seem
         // to match any socket, and appears to be a real
         // key press event...
      }
   }
}

// --------------------------------------------------------------------
// Accepts new connections on the server socket, creating new
// entries in the glbClients[] array
// --------------------------------------------------------------------

void AcceptNewConnections()
{
   // Keep accepting any pending connections until Accept() returns NULL
   
   ClientSocket * pNewClient = NULL;
   do {
	  //if(initializationActive == true) {return;}
      pNewClient = glbServerSocket.Accept();
      if (pNewClient != NULL) 
      {
         int sz = ArraySize(glbClients);
         ArrayResize(glbClients, sz + 1);
         glbClients[sz] = pNewClient;
         Print("New client connection");
         
         pNewClient.Send("Hello new client;");
      }
      
   } while (pNewClient != NULL);
}

// --------------------------------------------------------------------
// Handles any new incoming data on a client socket, identified
// by its index within the glbClients[] array. This function
// deletes the ClientSocket object, and restructures the array,
// if the socket has been closed by the client
// --------------------------------------------------------------------

void HandleSocketIncomingData(int idxClient)
{
   ClientSocket * pClient = glbClients[idxClient];

   // Keep reading CRLF-terminated lines of input from the client
   // until we run out of new data
   bool bForceClose = false; // Client has sent a "close" message
   string strCommand;
   do {
      strCommand = pClient.Receive("!");
      
      if (StringLen(strCommand) > 0)
      {

         ;
      }
      if (strCommand == "Hello") 
      {
         //Print("Hello:" + strCommand);
         pClient.Send(Symbol() + "!");
      } 
      else if (StringFind(strCommand,"F") >= 0)
      {
         string strResult = executeCommand(strCommand);
         pClient.Send(strResult);
      } 
      else if (strCommand != "") {
         // Potentially handle other commands etc here.
         // For example purposes, we'll simply print messages to the Experts log
         Print("<- ", strCommand);
      }
   } while (strCommand != "");

   // If the socket has been closed, or the client has sent a close message,
   // release the socket and shuffle the glbClients[] array
   if (!pClient.IsSocketConnected() || bForceClose) {
      Print("Client has disconnected");

      // Client is dead. Destroy the object
      delete pClient;
      
      // And remove from the array
      int ctClients = ArraySize(glbClients);
      for (int i = idxClient + 1; i < ctClients; i++) {
         glbClients[i - 1] = glbClients[i];
      }
      ctClients--;
      ArrayResize(glbClients, ctClients);
   }
}

//+------------------------------------------------------------------+

string executeCommand(string command)
{
   string returnString = "Error";
   string commandSplit[];
   
   StringSplit(command, char('#'), commandSplit);

   if (commandSplit[0] == "F000") {
      returnString = mt5_f000.Execute(command);
   }
   else if (commandSplit[0] == "F001") {
      returnString = mt5_f001.Execute(command);
   }
   else if (commandSplit[0] == "F002") {
      returnString = mt5_f002.Execute(command);
   }
   else if (commandSplit[0] == "F003") {
      returnString = mt5_f003.Execute(command);
   }
   else if (commandSplit[0] == "F004") {
      returnString = mt5_f004.Execute(command);
   }
   else if (commandSplit[0] == "F005") {
      returnString = mt5_f005.Execute(command);
   }
   else if (commandSplit[0] == "F007")
   {
      returnString = mt5_f007.Execute(command);
   }
   else if (commandSplit[0] == "F020") {
      returnString = mt5_f020.Execute(command);
   }
   else if (commandSplit[0] == "F021") {
      returnString = mt5_f021.Execute(command);
   }
   else if (commandSplit[0] == "F041")
   {
      returnString = mt5_f041.Execute(command);
   }
   else if (commandSplit[0] == "F042") {
      returnString = mt5_f042.Execute(command);
   }
   else if (commandSplit[0] == "F045")
   {
      returnString = mt5_f045.Execute(command);
   }
   else if (commandSplit[0] == "F041") {
      returnString = mt5_f041.Execute(command);
   }
   else if (commandSplit[0] == "F060") {
      returnString = mt5_f060.Execute(command);
   }
   else if (commandSplit[0] == "F061") {
      returnString = mt5_f061.Execute(command);
   }
   else if (commandSplit[0] == "F062") {
      returnString = mt5_f062.Execute(command);
   }
   else if (commandSplit[0] == "F070") {
      returnString = mt5_f070.Execute(command);
   }
   else if (commandSplit[0] == "F071") {
      returnString = mt5_f071.Execute(command);
   }
   else if (commandSplit[0] == "F072") {
      returnString = mt5_f072.Execute(command);
   }
   else if (commandSplit[0] == "F073") {
      returnString = mt5_f073.Execute(command);
   }
   else if (commandSplit[0] == "F075") {
      returnString = mt5_f075.Execute(command);
   }
   else if (commandSplit[0] == "F076") {
      returnString = mt5_f076.Execute(command);
   }
   else {
      returnString = "F999:2:Command not implemented:xx:;";
   }

   return returnString;
}

/* -------------------------------------------------------------------
	OrderSendReliable
	ordersend reliable
	simplex: modified logging
	------------------------------------------------------------------- */
int tlbOrderSendReliable(string symbol,
                      int cmd,
                      double volume,
                      double price,
                      int _slippage,
                      double stoploss,
                      double takeprofit,
                      int _magic,
                      string comment = "",
                      datetime expiration = 0,
                      color arrow_color = clrNONE
							) {
   int ticket;
   errorNumber = 0;
   
   int tryCounter = 0;
   int tryLevel = 5;
   
   int err;
   double _price = price;
   //int __magic =0;
	string printPrefix = tlbEaLog(__FUNCTION__, "");
	
	string tlbStringToLog = printPrefix
         + tlbOrderTypeToStr(cmd) + ", "
         + symbol + ", "
         + DoubleToStr(volume, 2) + ", "
         + tlbPrice2String(price) + ", "
         + IntToStr(_slippage) + ", "
         + tlbPrice2String(stoploss) + ", "
         + tlbPrice2String(takeprofit) + ", "
         + comment + ", "
         + IntToStr(_magic) + ", "
         + TimeToStr(expiration) + ", "
         + ColorToString(arrow_color) + ")";
         
   Print(  tlbStringToLog);

   while (tryCounter < tryLevel) 
   {
      if (IsStopped()) {
         Print(printPrefix + " Trading is stopped!");
         return(-1);
      }
      RefreshRates();
      if (cmd == OP_BUY) {
         _price = MarketInfo(symbol, MODE_ASK);
         //__magic = magicNumberBuy;
      }
      else if (cmd == OP_SELL) {
         _price = MarketInfo(symbol, MODE_BID);
         //__magic = magicNumberSell;
      }
      else
      {
         _price = price;
      
      }
      if (!IsTradeContextBusy()) 
      {
         tryCounter++;
         ticket = OrderSend(symbol,
                            cmd,
                            volume,
                            NormalizeDouble(_price, (int)MarketInfo(symbol, MODE_DIGITS)),
                            _slippage,
                            NormalizeDouble(stoploss, (int)MarketInfo(symbol, MODE_DIGITS)),
                            NormalizeDouble(takeprofit, (int)MarketInfo(symbol, MODE_DIGITS)),
                            comment,
                            _magic,
                            expiration,
                            arrow_color);
         if (ticket > 0) 
         {
				printPrefix = printPrefix + tlbTicket2String(ticket);
            Print(printPrefix + "opened.");
            
            // log trade info
            //tlbWriteToLogFile(tlbStringToLog, "STO_");
            return(ticket); 						// normal exit
         }
         
         Sleep(MathRand() / 10);
         err = GetLastError();
         errorNumber = err;
         if (tlbIsTemporaryError(err)) {
            Print(printPrefix + "Temporary Error: " + IntToStr(err) + " " + ErrorDescription(err) + ". Waiting.");
			}
         else {
            Print(printPrefix + "Permanent Error: " + IntToStr(err) + " " + ErrorDescription(err) + ". Giving up.");
            return(-1);
         }
      }
      else 
      {
         Print(printPrefix + "Must wait for trade context.");
		}

      Sleep(MathRand() / 10);
   }
   return (-2);
}

/* -----------------------------------------------------------
   OrderCloseReliable
	Drop-in replacement for OrderClose().
	Try to handle all errors and locks and return only if successful
	or if the error can not be handled or waited for.
	simplex: modified logging
   ----------------------------------------------------------- */
bool tlbOrderCloseReliable(	int ticket,
									double lots,
									int _slippage,
									color arrow_color = clrNONE
								) 
{
   

   bool success;
   int err;
   double price = 0;
   int counter = 0;
   bool selected = OrderSelect(ticket, SELECT_BY_TICKET, MODE_TRADES);
	string printPrefix = tlbEaLog(__FUNCTION__, tlbTicket2String(ticket));
   errorNumber = 0;
   while (true) {
      if (IsStopped()) {
         Print(printPrefix, " Trading is stopped. Cannot close order!");
         return(false);
      }
      RefreshRates();
      if (OrderType() == OP_BUY) {
         price = MarketInfo(OrderSymbol(), MODE_BID); // close long at bid
      }
      if (OrderType() == OP_SELL) {
         price = MarketInfo(OrderSymbol(), MODE_ASK); // close short at ask
      }
      if (!IsTradeContextBusy()) {
         success = OrderClose(ticket,
                              lots,
                              NormalizeDouble(price, (int)MarketInfo(OrderSymbol(), MODE_DIGITS)),
                              _slippage,
                              arrow_color);
         if (success == true) {
            Print(printPrefix, "Order closed.");
            return(true); 									// the normal exit
         }

         err = GetLastError();
         errorNumber = err;
         if (tlbIsTemporaryError(err)) {
            Print(printPrefix, "Temporary Error: " + IntToStr(err) + " " + ErrorDescription(err) + ". waiting.");
            counter++;
            if (counter >= 5) {
               return false;
            }
         } 
         else {
            Print(printPrefix, "Permanent Error: " + IntToStr(err) + " " + ErrorDescription(err) + ". giving up.");
            return(false);
         }
      } 
      else {
         Print(printPrefix, "Must wait for trade context");
      }
      Sleep(MathRand() / 10);
   }
   
   return (false);
}

/* -----------------------------------------------------------
OrderDeleteReliable
Drop-in replacement for OrderDelete().
Try to handle all errors and locks and return only if successful
or if the error can not be handled or waited for.
simplex: modified logging
----------------------------------------------------------- */
bool tlbOrderDeleteReliable(int ticket) 
{
   bool success;
   int err;
	string printPrefix = tlbEaLog(__FUNCTION__, tlbTicket2String(ticket));
   // Print(printPrefix);
	errorNumber = 0;
   while (true) {
		tlbWaitForTradeContext(printPrefix);

      success = OrderDelete(ticket);

      if (success == true) {
         Print(printPrefix, "Order deleted.");
         return(true);
      }

      err = GetLastError();
      errorNumber = err;
      if (tlbIsTemporaryError(err)) {
         Print(printPrefix, "Temporary Error: " + IntToStr(err) + " " + ErrorDescription(err) + ". waiting.");
      } 
      else {
         Print(printPrefix, "Permanent Error: " + IntToStr(err) + " " + ErrorDescription(err) + ". giving up.");
         return(false);
      }
      Sleep(MathRand() / 10);
   }
   return false;
}

/* -----------------------------------------------------------
NormalizeLots
----------------------------------------------------------- */
double tlbNormalizeLots(string sym, double lots) 
{
   RefreshRates();
   double step = MarketInfo(sym, MODE_LOTSTEP);
   int norm = 0;
   if (step == 1   ) norm = 0;
   if (step == 0.1 ) norm = 1;
   if (step == 0.01) norm = 2;
   return NormalizeDouble(lots, norm);
}


/* -----------------------------------------------------------
waitForTradeContext
Author:		simplex, 2016
Returns: 	false if trade context is occupied
				true if trade context is free
----------------------------------------------------------- */
bool tlbWaitForTradeContext(const string message) 
{
	while (IsTradeContextBusy()) {
		Print(message + "Waiting for trade context.");
		Sleep(MathRand() / 10);
	}
	return(true);
}

/* -------------------------------------------------------------------
	eaLog
	Author:		simplex, 2016
	Returns: 	formatted string to print out in a log file
	------------------------------------------------------------------- */
string tlbEaLog(string _input1, string _input2, int tabSize = 30) 
{
	_input1 = tlbStringLeftTrim(tlbStringRightTrim(_input1)) + " ";
	_input2 = tlbStringLeftTrim(tlbStringRightTrim(_input2));
	while(StringLen(_input1) < tabSize) {
		_input1 = _input1 + " ";
	}
	string out = _input1 + _input2;
	if (StringLen(_input2) > 0) {
		out = out + " ";
	}
	return(out);
}

/* -------------------------------------------------------------------
	price2String
	Author:		simplex, 2016
	Returns: 	formatted price string to print out in a log file
	Remarks:		depends on global variable digits
	------------------------------------------------------------------- */
string tlbPrice2String(double _input) 
{
	string out = DoubleToStr(_input, 5);
	return(out);
}


/* -------------------------------------------------------------------
	ticket2String
	Author:		simplex, 2016
	Returns: 	formatted ticket string to print out in a log file
	------------------------------------------------------------------- */
string tlbTicket2String(int ticket) 
{
	string out = "Ticket_" + IntegerToString(ticket) + " ";
	return(out);
}

/* -------------------------------------------------------------------
	IsTemporaryError
	Is the error temporary (does it make sense to wait).
	------------------------------------------------------------------- */
bool tlbIsTemporaryError(int error) 
{
   return(error == ERR_NO_ERROR ||
          error == ERR_COMMON_ERROR ||
          error == ERR_SERVER_BUSY ||
          error == ERR_NO_CONNECTION ||
          error == ERR_MARKET_CLOSED ||
          error == ERR_PRICE_CHANGED ||
          error == ERR_INVALID_PRICE ||  //happens sometimes
          error == ERR_OFF_QUOTES ||
          error == ERR_BROKER_BUSY ||
          error == ERR_REQUOTE ||
          error == ERR_TRADE_TIMEOUT ||
          error == ERR_TRADE_CONTEXT_BUSY );
}

/* -----------------------------------------------------------
   StringLeftTrim
   ------------------
   hanover --- extensible functions (np).mqh
   ------------------
   Removes all leading spaces from a string
   Usage:    string x=StringLeftTrim("  XX YY  ")  returns x = "XX  YY  "
   _char defaults to space(s), but may contain a list of characters to be stripped
----------------------------------------------------------- */
string tlbStringLeftTrim(const string str, const string _char = " ") 
{
   bool left     = true;
   string outstr = "";

   for (int i = 0; i<StringLen(str); i++) {
      if (StringFind(_char, StringSubstr(str, i, 1)) < 0 || !left) {
         outstr = outstr + StringSubstr(str, i, 1);
         left   = false;
      }
   }
   return(outstr);
}

/* -----------------------------------------------------------
   StringRightTrim
   ------------------
   hanover --- extensible functions (np).mqh
   ------------------
	Removes all trailing spaces from a string
	Usage:    string x=StringRightTrim("  XX YY  ")  returns x = "  XX  YY"
	_char defaults to space(s), but may contain a list of characters to be stripped
	----------------------------------------------------------- */
string tlbStringRightTrim(const string str, const string _char=" ") 
{
	int pos = 0;
	for(int i=StringLen(str)-1; i>=0; i--) {
		if (StringFind(_char,StringSubstr(str,i,1)) < 0) {
			pos = i;
			break;
		} 
	}
	string outstr = StringSubstr(str,0,pos+1);
	return(outstr);
}
/* -----------------------------------------------------------
   OrderTypeToStr
	Converts integer value of order command type to its code
	simplex mod: OP_ALL
----------------------------------------------------------- */
string tlbOrderTypeToStr(int cmd) 
{
   switch(cmd) { 
      case OP_BUY: 
         return "OP_BUY"; 
      case OP_SELL: 
         return "OP_SELL";
      case OP_BUYLIMIT: 
         return "OP_BUYLIMIT";
      case OP_SELLLIMIT: 
         return "OP_SELLLIMIT";
      case OP_BUYSTOP: 
         return "OP_BUYSTOP";
      case OP_SELLSTOP: 
         return "OP_SELLSTOP";

   }
   return ("ORDERTYPE UNKNOWN: " + IntegerToString(cmd));
}


/* -----------------------------------------------------------
IntToStr
----------------------------------------------------------- */
string IntToStr(int i) 
{
   return (IntegerToString(i));
}

//+------------------------------------------------------------------+
string stringReplace(string str, string str1, string str2)  {
//+------------------------------------------------------------------+
// Usage: replaces every occurrence of str1 with str2 in str
// e.g. StringReplace("ABCDE","CD","X") returns "ABXE"
  string outstr = "";
  for (int i=0; i<StringLen(str); i++)   {
    if (StringSubstr(str,i,StringLen(str1)) == str1)  {
      outstr = outstr + str2;
      i += StringLen(str1) - 1;
    }
    else
      outstr = outstr + StringSubstr(str,i,1);
  }
  return(outstr);
}

string filterComment(string _tofilter)
{
   string tmpString = "";
   
   tmpString = stringReplace(_tofilter, "#", "");
   tmpString = stringReplace(tmpString, "$", "");
   tmpString = stringReplace(tmpString, "!", "");
   
   return tmpString;
}

bool checkInstrumentsInDemo(string instrument)
{
   string demoInstruments[] = {"EURUSD", "AUDCHF", "NZDCHF", "GBPNZD", "USDCAD"};
   
   for (int u = 0; u < ArraySize(demoInstruments); u++) {
      if (StringFind(instrument, demoInstruments[u]) >= 0) {
         return true;
      }   
   }
   return false;
}