import numpy as np
import datetime

def LAG(field, period):
    nMarkets = np.shape(field)[1]
    out =  np.append(np.zeros((period,nMarkets))*np.nan,field[:-period,:],axis=0)
    return out

def ATR(HIGH, LOW, CLOSE, period):
    tr = TR(HIGH,LOW,CLOSE)
    out = np.mean(tr[-period:,:],axis=0)
    return out

def TR(HIGH, LOW, CLOSE):
    CLOSELAG = LAG(CLOSE,1)
    range1 = HIGH - LOW
    range2 = np.abs(HIGH-CLOSELAG)
    range3 = np.abs(LOW -CLOSELAG)
    out = np.fmax(np.fmax(range1,range2),range3)
    return out

def myTradingSystem(DATE, OPEN, HIGH, LOW, CLOSE, settings, exposure):
    if 'long' not in settings:
        settings['longrule']=[]
        settings['shortrule']=[]

    nMarkets = len(settings['markets'])
    p = np.zeros(nMarkets)

    date = datetime.datetime.strptime(str(int(DATE[-1])), '%Y%m%d')
    if date.weekday() != 0:
        p[:] = 0
        return p, settings

    closeRange = np.ptp(CLOSE[-4:,1])
    atr = ATR(HIGH, LOW, CLOSE, 4)

    LongRule1 = CLOSE[-1,1] < CLOSE[-2,1] and  closeRange < atr[1]
    ShortRule1 = CLOSE[-1,1] > CLOSE[-2,1] and  closeRange < atr[1]

    if LongRule1:
        p[0], p[1] = 0, 1

    if ShortRule1:
        p[0], p[1] = 0, -1

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
    settings['lookback']    = 504

    return settings

if __name__=='__main__':
    import quantiacsToolbox
    results = quantiacsToolbox.runts(__file__)
