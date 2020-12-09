import numpy

def myTradingSystem(DATE, OPEN, HIGH, LOW, CLOSE, settings):
    # Check if initial run
    if ~hasattr(settings, 'HA_Close'):
        nMarkets = CLOSE.shape[1]
        nRows = CLOSE.shape[0]

        # Initial p vector, only need to define on first run
        settings['lastP'] = numpy.zeros(nMarkets)

        # Initial Heikin Values
        settings['HA_Close'] = (OPEN[0,]+HIGH[0,]+LOW[0,]+CLOSE[0,])/4
        settings['HA_Open'] = (OPEN[0,]+CLOSE[0,])/2

        # Run across lookback period, starting with 2nd row
        for i in range(1,nRows):
            HAmatrix = HEIKIN(OPEN[i,:],HIGH[i,:],LOW[i,:],CLOSE[i,:],settings['HA_Open'],settings['HA_Close'])
            # To keep from running on the latest value to use in trade logic
            if i < nRows-1:
                settings['HA_Close'] = HAmatrix[0,:]
                settings['HA_Open'] = HAmatrix[1,:]
    else: # If not first run just get latest Heikin values
        HAmatrix = HEIKIN(OPEN[-1,:],HIGH[-1,:],LOW[-1,:],CLOSE[-1,:],settings['HA_Open'],settings['HA_Close'])
    
    # Run Trade Logic
    tLogic = trades(HAmatrix, settings['HA_Open'], settings['HA_Close'])
    
    # Set new previous Heikin values for next run
    settings['HA_Close'] = HAmatrix[0,:]
    settings['HA_Open'] = HAmatrix[1,:]
    
    # Execute Positions
    p = executeP(tLogic[0,:],tLogic[1,:],tLogic[2,:],tLogic[3,:],settings['lastP'])
    
    # Save positions to be able to do trade logic on next run
    settings['lastP'] = p;
    
    return p, settings

def mySettings():
    settings = {}

    settings['markets'] = ['CASH', 'F_AD', 'F_AE', 'F_AH', 'F_AX', 'F_BC', 'F_BG', 'F_BO', 'F_BP', 'F_C',  'F_CA',
                           'F_CC', 'F_CD', 'F_CF', 'F_CL', 'F_CT', 'F_DL', 'F_DM', 'F_DT', 'F_DX', 'F_DZ', 'F_EB',
                           'F_EC', 'F_ED', 'F_ES', 'F_F',  'F_FB', 'F_FC', 'F_FL', 'F_FM', 'F_FP', 'F_FV', 'F_FY',
                           'F_GC', 'F_GD', 'F_GS', 'F_GX', 'F_HG', 'F_HO', 'F_HP', 'F_JY', 'F_KC', 'F_LB', 'F_LC',
                           'F_LN', 'F_LQ', 'F_LR', 'F_LU', 'F_LX', 'F_MD', 'F_MP', 'F_ND', 'F_NG', 'F_NQ', 'F_NR',
                           'F_NY', 'F_O',  'F_OJ', 'F_PA', 'F_PL', 'F_PQ', 'F_RB', 'F_RF', 'F_RP', 'F_RR', 'F_RU',
                           'F_RY', 'F_S',  'F_SB', 'F_SF', 'F_SH', 'F_SI', 'F_SM', 'F_SS', 'F_SX', 'F_TR', 'F_TU',
                           'F_TY', 'F_UB', 'F_US', 'F_UZ', 'F_VF', 'F_VT', 'F_VW', 'F_VX',  'F_W', 'F_XX', 'F_YM',
                           'F_ZQ']

    settings['slippage']    = 0.05
    settings['budget']      = 1000000
    settings['lookback']    = 11

    return settings

def HEIKIN(O, H, L, C, oldO, oldC):
    HA_Close = (O + H + L + C)/4
    HA_Open = (oldO + oldC)/2
    elements = numpy.array([H, L, HA_Open, HA_Close])
    HA_High = elements.max(0) 
    HA_Low = elements.min(0)
    out = numpy.array([HA_Close, HA_Open, HA_High, HA_Low])    
    return out

def trades(HA, oldO, oldC):
    # Heikin Ashi Reversal Strategy
    # ------------- Entry ----------------
    # Buying
    # latest HA candle is bearish, HA_Close < HA_Open
    long1 = HA[0,:] < HA[1,:]    

    # current candle body is longer than previous candle body
    long2 = numpy.abs(HA[0,:] - HA[1,:]) > numpy.abs(oldC - oldO)

    # previous candle was bearish
    long3 = oldC < oldO

    # latest candle has no upper wick HA_Open == HA_High
    long4 = HA[1,:] == HA[2,:]
    long = long1 & long2 & long3 & long4

    # Selling
    # latest candle bullish, previous candle bullish with smaller body
    # latest candle has no lower wick HA_Open == HA_Low
    short4 = HA[1,:] == HA[3,:]
    short = ~long1 & long2 & ~long3 & short4

    # ------------- Exit -----------------
    # Exiting Long Positions - same conditions as short except for candle body
    long_exit = ~long1 & ~long3 & short4

    # Exiting Short Positions - same conditions as long except for candle body
    short_exit = long1 & long3 & long4
    out = numpy.array([long, short, long_exit, short_exit])
    return out
    
def executeP(L, S, L_e, S_e, oldP):
    # Split buy and sell from p
    Pbought = oldP > 0
    Psold = oldP < 0

    # Close Long Positions
    closeBuy = Pbought & L_e
    oldP[closeBuy] = 0

    # Close Sort Positions
    closeSell = Psold & S_e
    oldP[closeSell] = 0

    # Enter New Long Positions
    oldP[L] = 1

    # Enter New Short Positions
    oldP[S] = -1
    return oldP
    
# Evaluate trading system defined in current file.
if __name__ == '__main__':
    import quantiacsToolbox
    results = quantiacsToolbox.runts(__file__)