## IMPORTS
from socket import if_nametoindex
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from datetime import date, timedelta
from yahoo_fin.stock_info import get_data
from numba import jit
import numba

goodSector = pd.read_pickle("stockData/goodSector.pkl")
sectorOfTicker = pd.read_pickle("stockData/sector.pkl")
goodSector['stage'] = set(goodSector['sector'])
SectorDict = {
    "Energy":"XLE",
    "Technology":"XLK",
    "Communication Services":"XLC",
    "Consumer Defensive":"XLP",
    "Healthcare":"XLV",
    "Consumer Cyclical":"XLY",
    "Industrials":"XLI",
    "Utilities":"XLU",
    "Basic Materials":"XLB",
    "Financial Services":"XLF",
    "Real Estate":"XLRE"}

## TOOL FUNCTIONS
def fullPrint(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)  

#*Stage Checker
@jit
def checkIfStage2(price,volumePerc, RS, slope, wMA30,prevStage,prevClose,prevSupport,peak,prevPeak,prevTrough,dfSorted,secondBought,initialSupport,fiveYearHigh,param):
    dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('support')] = prevSupport
    if prevStage == "Stage 2" or prevStage == "Buy":
        if price < prevSupport*param[7]:
            return "Sell"
        dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('initialSupport')] = initialSupport
        if price == peak and prevTrough < prevPeak*param[6]:
            dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('support')] = prevTrough
        if secondBought == True:
            dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('secondBuy')] = True
            if price <= initialSupport*param[5] and dfSorted.loc[index]['trough'] < dfSorted.loc[index]['peak']:
                dfSorted.iloc[dfSorted.index.get_loc(index)]['secondBuy'] = False
                return "Buy"
        return "Stage 2"
    try:
        goodSectorIndex = goodSector.index.get_loc(index.strftime('%Y-%m-%d'))
    except:
        return "bad sector"
    try:
        for sector in sectorOfTicker:
            if dfSorted.loc[index]['ticker'] in sectorOfTicker[sector]:
                thisSector = sector
        if SectorDict[thisSector] not in goodSector.iloc[goodSectorIndex]['Sectors']:
            return "bad sector"
    except:
        pass
    if price < fiveYearHigh * param[0]:
        return "resistance"
    if volumePerc < param[1]:
        return "volume"
    if RS < param[2]:
        return "RS"
    if slope < param[3]:
        return "Slope"
    if price < wMA30*param[4]:
        return "Price"
    dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('support')] = prevClose
    dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('initialSupport')] = prevClose
    i = dfSorted.index.get_loc(index)
    while i < dfSorted.shape[0] and dfSorted.iloc[i, dfSorted.columns.get_loc('trough')]<prevClose:
        dfSorted.iloc[i, dfSorted.columns.get_loc('trough')] = prevClose
        i=i+1
    dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('secondBuy')] = True
    return "Buy"


## Main Function
def returnStageDf(dfSorted,param):
    # for index, element in dfSorted.iterrows():
    #     if dfSorted.index.get_loc(index) == 0:
    #         continue
    #     dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('Stage')] = checkIfStage2(dfSorted.loc[index]['close'],dfSorted.loc[index]['volumePerc'],dfSorted.loc[index]['RS'],dfSorted.loc[index]['WMA30Slope'],dfSorted.loc[index]['WMA30'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['Stage'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['close'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['support'],dfSorted.loc[index]['peak'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['peak'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['trough'],index,dfSorted,dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['secondBuy'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['initialSupport'],dfSorted.loc[index]['fiveYearHigh'],param)
    dfSorted['Stage'] = dfSorted.apply(checkIfStage2(dfSorted['close'],dfSorted['volumePerc'],dfSorted['RS'],dfSorted['WMA30Slope'],dfSorted['WMA30'],dfSorted['Stage'],dfSorted['close'],dfSorted['support'],dfSorted['peak'],dfSorted.iloc[dfSorted['peak'],dfSorted['trough'],dfSorted,dfSorted['secondBuy'],dfSorted['initialSupport'],dfSorted['fiveYearHigh'],param))
    return dfSorted[["close","Stage"]]

def getStage(ticker,param):
#     today = date.today()
#     # #200->1000
#     startDate = today - timedelta(weeks=1000)
    # today = today.strftime('%Y-%m-%d')
    # startDate = startDate.strftime('%Y-%m-%d')
    # df = get_data(ticker, start_date=startDate, end_date=today, index_as_date = True, interval="1wk")
    df = pd.read_pickle("stockData/S&P500/"+ticker+".pkl")
    return returnStageDf(df,param)