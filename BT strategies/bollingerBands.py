import numpy as np


def myTradingSystem(DATE, OPEN, HIGH, LOW, CLOSE, VOL, OI, P, R, RINFO, exposure, equity, settings):

    def bollingerBands(a, n=20):
        sma = np.nansum(a[-n:]) / n
        std = np.std(a[-n:], ddof=1)
        return sma, sma + 2 * std, sma - 2 * std

    nMarkets = len(settings['markets'])
    threshold = settings['threshold']
    pos = np.zeros((1, nMarkets), dtype=np.float)

    for market in range(nMarkets):
        sma, upperBand, lowerBand = bollingerBands(CLOSE[:, market])
        currentPrice = CLOSE[-1, market]

        if currentPrice >= upperBand + (upperBand - lowerBand) * threshold:
            pos[0, market] = -1
        elif currentPrice <= lowerBand - (upperBand - lowerBand) * threshold:
            pos[0, market] = 1

    return pos, settings


def mySettings():
    """ Define your trading system settings here """

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

    # Futures Contracts
    settings['lookback'] = 20
    settings['budget'] = 10 ** 6
    settings['slippage'] = 0.05

    settings['threshold'] = 0.4

    return settings


if __name__ == '__main__':
    import quantiacsToolbox

    quantiacsToolbox.runts(__file__)
