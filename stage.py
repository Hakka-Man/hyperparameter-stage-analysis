## IMPORTS
from fileinput import close
from socket import if_nametoindex
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from datetime import datetime, timedelta
from yahoo_fin.stock_info import get_data

goodSector = pd.DataFrame()
spdf = pd.read_pickle("stockData/Spy.pkl")
sectorOfTicker = pd.read_pickle("stockData/nasdaq.pkl")
sectorOfNyse = pd.read_pickle("stockData/nyse.pkl")
sectorOfTicker.update(sectorOfNyse)

#CONSTANTS
CLOSE = 0
VOLUME = 1
TICKER = 2
FIVE_YEAR_HIGH = 3
WMA30 = 4
WMA30_SLOPE = 5
VOLUME_PERC = 6
PERCENT = 7
RS = 8
PEAK = 9
TROUGH = 10
SUPPORT = 11
INITIAL_SUPPORT = 12
STAGE = 13
SECOND_BUY = 14

## TOOL FUNCTIONS
def fullPrint(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)

#*Stage Checker
def checkIfStage2(i,price,volumePerc, RS, slope, wMA30,prevStage,prevClose,prevSupport,peak,prevPeak,prevTrough,index,dfSorted,secondBought,initialSupport,fiveYearHigh,param,goodSectorDf):
    if prevStage == "Stage 2" or prevStage == "Buy":
        if spdf.at[index, 'close'] < spdf.at[index, 'WMA30'] * param[13]:
            return "Sell" +" " + str(spdf.at[index, 'close']) + " " + str(spdf.at[index, 'WMA30']) +" " + str(param[13])
        if spdf.at[index, 'WMA30Slope'] < param[14]:
            return "Sell" +" " + str(spdf.at[index, 'WMA30Slope']) +" " + str(param[14])
        if price>prevPeak:
            dfSorted.iat[i,PEAK] = price
            dfSorted.iat[i,TROUGH] = price
        else:
            dfSorted.iat[i,PEAK] = prevPeak
            dfSorted.iat[i,TROUGH] = min(prevTrough, price)
        if price < prevSupport*param[7]:
            return "Sell" +" " + str(prevSupport) +" " + str(param[7])
        dfSorted.iat[i,SUPPORT] = prevSupport
        dfSorted.iat[i, INITIAL_SUPPORT] = initialSupport
        if price == dfSorted.iat[i,PEAK] and prevTrough < prevPeak*param[6]:
            dfSorted.iat[i,SUPPORT] = prevTrough
        if secondBought == True:
            dfSorted.at[index, 'secondBuy'] = True
            if price <= initialSupport*param[5] and dfSorted.at[index,'trough'] < dfSorted.at[index,'peak']:
                dfSorted.iat[i, SECOND_BUY] = False        
                return "Buy"
        return "Stage 2"
    indexDate = index.strftime('%Y-%m-%d')
    dates = "1998-12-20"
    datee = "2022-02-26"
    if indexDate > dates and indexDate < datee:
        if sectorOfTicker[dfSorted.at[index,"ticker"]] in goodSectorDf.at[index,"Sectors"]:
            pass
        else:
            return "bad sector " + str(sectorOfTicker[dfSorted.at[index,"ticker"]]) + str(goodSectorDf.at[index,"Sectors"])
    else:
        #print(goodSectorDf)
        return "bad sector"
    # if spdf.at[index, 'close'] < spdf.at[index, 'WMA30'] * param[11]:
    #     return "bearish"
    # if spdf.at[index, 'WMA30Slope'] < param[12]:
    #     return "bearish"
    if price < fiveYearHigh * param[0]:
        return "resistance" +" " + str(price) +" " + str(fiveYearHigh) +" " + str(param[0])
    if volumePerc < param[1]:
        return "volume" +" " + str(volumePerc) +" " + str(param[1])
    if RS < param[2]:
        return "RS" +" " + str(RS) +" " + str(param[2])
    if slope < param[3]:
        return "Slope" +" " + str(slope) +" " + str(param[3])
    if price < wMA30*param[4]:
        return "Price" +" " + str(wMA30) +" " + str(param[4])
    if price > prevClose*param[8]:
        return "Short"  + " " +str(prevClose) + " " +str(param[8])

    
    if price > prevClose:
        # peak
        dfSorted.iat[i,PEAK] = price
        # trough
        dfSorted.iat[i,TROUGH] = price
        # support
        dfSorted.iat[i,SUPPORT] = prevClose
        # initialSupport
        dfSorted.iat[i,INITIAL_SUPPORT] = prevClose
    else:
        dfSorted.iat[i,PEAK] = price
        dfSorted.iat[i,TROUGH] = price*0.95
        dfSorted.iat[i,SUPPORT] = price*0.95
        dfSorted.iat[i,INITIAL_SUPPORT] = price*0.95
    dfSorted.at[index, 'secondBuy'] = True
    return "Buy"


## Main Function
def returnStageDf(dfSorted,param,goodSectorDf):
    first = True
    fullPrint(dfSorted)
    for index in dfSorted.index:
        if first:
            if dfSorted.index.get_loc(index) == 0:
                first = False
                continue
        prevIndex = index - timedelta(weeks=1)
        i = dfSorted.index.get_loc(index)
        dfSorted.iat[i, STAGE] = checkIfStage2(i,dfSorted.iat[i,CLOSE],dfSorted.iat[i,VOLUME_PERC],dfSorted.iat[i,RS],dfSorted.iat[i,WMA30_SLOPE],dfSorted.iat[i,WMA30],dfSorted.iat[i-1,STAGE],dfSorted.iat[i-1,CLOSE],dfSorted.iat[i-1,SUPPORT],dfSorted.iat[i,PEAK],dfSorted.iat[i-1,PEAK],dfSorted.iat[i-1,TROUGH],index,dfSorted,dfSorted.iat[i-1,SECOND_BUY],dfSorted.iat[i-1,INITIAL_SUPPORT],dfSorted.iat[i,FIVE_YEAR_HIGH],param,goodSectorDf)
    first = True
    return dfSorted[["close","Stage"]]

def getStage(ticker,param, goodSectorDf):
#     today = date.today()
#     # #200->1000
    
    # today = today.strftime('%Y-%m-%d')
    # startDate = startDate.strftime('%Y-%m-%d')
    # df = get_data(ticker, start_date=startDate, end_date=today, index_as_date = True, interval="1wk")
    df = pd.read_pickle("stockData/nyseNasdaq/"+ticker+".pkl")
    return returnStageDf(df,param, goodSectorDf)
    return pd.DataFrame()

# def getFullDf(ticker,param):
#     dfSorted = pd.read_pickle("stockData/nyseNasdaq/"+ticker+".pkl")
#     first = True
#     for index in dfSorted.index:
#         if first:
#             if dfSorted.index.get_loc(index) == 0:
#                 first = False
#                 continue
#         prevIndex = index - timedelta(weeks=1)
#         i = dfSorted.index.get_loc(index)
#         dfSorted.iat[i,STAGE] = checkIfStage2(i,dfSorted.iat[i,CLOSE],dfSorted.iat[i,VOLUME_PERC],dfSorted.iat[i,RS],dfSorted.iat[i,WMA30_SLOPE],dfSorted.iat[i,WMA30],dfSorted.iat[i-1,STAGE],dfSorted.iat[i-1,CLOSE],dfSorted.iat[i-1,SUPPORT],dfSorted.iat[i,PEAK],dfSorted.iat[i-1,PEAK],dfSorted.iat[i-1,TROUGH],index,dfSorted,dfSorted.iat[i-1,SECOND_BUY],dfSorted.iat[i-1,INITIAL_SUPPORT],dfSorted.iat[i,FIVE_YEAR_HIGH],param)
#     first = True
#     print(len(sectorOfTicker))
#     return dfSorted
    