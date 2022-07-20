## IMPORTS
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from datetime import datetime, timedelta

goodSector = pd.DataFrame()
spdf = pd.read_pickle("stockData/Spy.pkl")
sectorOfTicker = pd.read_pickle("stockData/nasdaq.pkl")
sectorOfIndustry = pd.read_pickle("stockData/industryList.pkl")

#CONSTANTS
CLOSE = 0
VOLUME = 1
FIVE_YEAR_HIGH = 2
WMA30 = 3
WMA30_SLOPE = 4
VOLUME_PERC = 5
PERCENT = 6
RS = 7
PEAK = 8
TROUGH = 9
SUPPORT = 10
INITIAL_SUPPORT = 11
STAGE = 12
SECOND_BUY = 13
TICKER = 17

## TOOL FUNCTIONS
def fullPrint(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)

#*Stage Checker
def checkIfStage2(indexNum,price,volumePerc, RS, slope, wMA30,prevStage,prevClose,prevSupport,prevPeak,prevTrough,index,dfSorted,secondBought,initialSupport,fiveYearHigh,param,goodSectorDf):
    if prevStage == "Stage 2" or prevStage == "Buy":
        if spdf.at[index, 'Close'] < spdf.at[index, 'WMA30'] * param[13]:
            return "Sell" +" " + str(spdf.at[index, 'Close']) + " " + str(spdf.at[index, 'WMA30']) +" " + str(param[13])
        if spdf.at[index, 'WMA30Slope'] < param[14]:
            return "Sell" +" " + str(spdf.at[index, 'WMA30Slope']) +" " + str(param[14])
        if price>prevPeak:
            dfSorted.iat[indexNum,PEAK] = price
            dfSorted.iat[indexNum,TROUGH] = price
        else:
            dfSorted.iat[indexNum,PEAK] = prevPeak
            dfSorted.iat[indexNum,TROUGH] = min(prevTrough, price)
        if price < prevSupport*param[7]:
            return "Sell" +" " + str(prevSupport) +" " + str(param[7])
        dfSorted.iat[indexNum,SUPPORT] = prevSupport
        dfSorted.iat[indexNum, INITIAL_SUPPORT] = initialSupport
        if price == dfSorted.iat[indexNum,PEAK] and prevTrough < prevPeak*param[6]:
            dfSorted.iat[indexNum,SUPPORT] = prevTrough
        if secondBought == True:
            dfSorted.at[index, 'secondBuy'] = True
            if price <= initialSupport*param[5] and dfSorted.at[index,'trough'] < dfSorted.at[index,'peak']:
                dfSorted.iat[indexNum, SECOND_BUY] = False        
                return "Buy"
        return "Stage 2"
    indexDate = index.strftime('%Y-%m-%d')
    dates = "1998-12-20"
    if indexDate > dates:
        if sectorOfIndustry[dfSorted.at[index,"ticker"]] in goodSectorDf.at[pd.Timestamp(indexDate),"Sectors"]:
            pass
        else:
            return "bad sector " + str(sectorOfIndustry[dfSorted.at[index,"ticker"]]) + str(goodSectorDf.at[index,"Sectors"])
    else:
        return "bad sector"
    if spdf.at[index, 'Close'] < spdf.at[index, 'WMA30'] * param[11]:
        return "bearish"
    if spdf.at[index, 'WMA30Slope'] < param[12]:
        return "bearish"
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
        dfSorted.iat[indexNum,PEAK] = price
        # trough
        dfSorted.iat[indexNum,TROUGH] = price
        # support
        dfSorted.iat[indexNum,SUPPORT] = prevClose
        # initialSupport
        dfSorted.iat[indexNum,INITIAL_SUPPORT] = prevClose
    else:
        dfSorted.iat[indexNum,PEAK] = price
        dfSorted.iat[indexNum,TROUGH] = price*0.95
        dfSorted.iat[indexNum,SUPPORT] = price*0.95
        dfSorted.iat[indexNum,INITIAL_SUPPORT] = price*0.95
    dfSorted.at[index, 'secondBuy'] = True
    return "Buy"

#*Stage Checker
def checkIfIndustryStage2(indexNum,price,volumePerc, RS, slope, wMA30,prevStage,prevClose,prevSupport,prevPeak,prevTrough,index,dfSorted,secondBought,initialSupport,fiveYearHigh,param,goodSectorDf):
    if prevStage == "Stage 2" or prevStage == "Buy":
        if spdf.at[index, 'Close'] < spdf.at[index, 'WMA30'] * param[13]:
            return "Sell" +" " + str(spdf.at[index, 'Close']) + " " + str(spdf.at[index, 'WMA30']) +" " + str(param[13])
        if spdf.at[index, 'WMA30Slope'] < param[14]:
            return "Sell" +" " + str(spdf.at[index, 'WMA30Slope']) +" " + str(param[14])
        if price>prevPeak:
            dfSorted.iat[indexNum,PEAK] = price
            dfSorted.iat[indexNum,TROUGH] = price
        else:
            dfSorted.iat[indexNum,PEAK] = prevPeak
            dfSorted.iat[indexNum,TROUGH] = min(prevTrough, price)
        if price < prevSupport*param[7]:
            return "Sell" +" " + str(prevSupport) +" " + str(param[7])
        dfSorted.iat[indexNum,SUPPORT] = prevSupport
        dfSorted.iat[indexNum, INITIAL_SUPPORT] = initialSupport
        if price == dfSorted.iat[indexNum,PEAK] and prevTrough < prevPeak*param[6]:
            dfSorted.iat[indexNum,SUPPORT] = prevTrough
        if secondBought == True:
            dfSorted.at[index, 'secondBuy'] = True
            if price <= initialSupport*param[5] and dfSorted.at[index,'trough'] < dfSorted.at[index,'peak']:
                dfSorted.iat[indexNum, SECOND_BUY] = False        
                return "Buy"
        return "Stage 2"
    indexDate = index.strftime('%Y-%m-%d')
    dates = "1998-12-20"
    # if indexDate > dates:
    #     if sectorOfTicker[dfSorted.at[index,"ticker"]] in goodSectorDf.at[pd.Timestamp(indexDate),"Sectors"]:
    #         pass
    #     else:
    #         return "bad sector " + str(sectorOfTicker[dfSorted.at[index,"ticker"]]) + str(goodSectorDf.at[index,"Sectors"])
    # else:
    #     return "bad sector"
    if spdf.at[index, 'Close'] < spdf.at[index, 'WMA30'] * param[11]:
        return "bearish"
    if spdf.at[index, 'WMA30Slope'] < param[12]:
        return "bearish"
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
        dfSorted.iat[indexNum,PEAK] = price
        # trough
        dfSorted.iat[indexNum,TROUGH] = price
        # support
        dfSorted.iat[indexNum,SUPPORT] = prevClose
        # initialSupport
        dfSorted.iat[indexNum,INITIAL_SUPPORT] = prevClose
    else:
        dfSorted.iat[indexNum,PEAK] = price
        dfSorted.iat[indexNum,TROUGH] = price*0.95
        dfSorted.iat[indexNum,SUPPORT] = price*0.95
        dfSorted.iat[indexNum,INITIAL_SUPPORT] = price*0.95
    dfSorted.at[index, 'secondBuy'] = True
    return "Buy"


## Main Function
def returnStageDf(dfSorted, param, goodSectorDf):
    first = True
    for index in dfSorted.index:
        if first:
            if dfSorted.index.get_loc(index) == 0:
                first = False
                continue
        indexNum = dfSorted.index.get_loc(index)
        dfSorted.iat[indexNum, STAGE] = checkIfStage2(indexNum,dfSorted.iat[indexNum,CLOSE],dfSorted.iat[indexNum,VOLUME_PERC],dfSorted.iat[indexNum,RS],dfSorted.iat[indexNum,WMA30_SLOPE],dfSorted.iat[indexNum,WMA30],dfSorted.iat[indexNum-1,STAGE],dfSorted.iat[indexNum-1,CLOSE],dfSorted.iat[indexNum-1,SUPPORT],dfSorted.iat[indexNum,PEAK],dfSorted.iat[indexNum-1,TROUGH],index,dfSorted,dfSorted.iat[indexNum-1,SECOND_BUY],dfSorted.iat[indexNum-1,INITIAL_SUPPORT],dfSorted.iat[indexNum,FIVE_YEAR_HIGH],param,goodSectorDf)
    first = True
    return dfSorted[["Close", "Stage", "support"]]

def returnIndustryStageDf(dfSorted, param, goodSectorDf):
    first = True
    for index in dfSorted.index:
        if first:
            if dfSorted.index.get_loc(index) == 0:
                first = False
                continue
        indexNum = dfSorted.index.get_loc(index)
        dfSorted.iat[indexNum, STAGE] = checkIfIndustryStage2(indexNum,dfSorted.iat[indexNum,CLOSE],dfSorted.iat[indexNum,VOLUME_PERC],dfSorted.iat[indexNum,RS],dfSorted.iat[indexNum,WMA30_SLOPE],dfSorted.iat[indexNum,WMA30],dfSorted.iat[indexNum-1,STAGE],dfSorted.iat[indexNum-1,CLOSE],dfSorted.iat[indexNum-1,SUPPORT],dfSorted.iat[indexNum-1,PEAK],dfSorted.iat[indexNum-1,TROUGH],index,dfSorted,dfSorted.iat[indexNum-1,SECOND_BUY],dfSorted.iat[indexNum-1,INITIAL_SUPPORT],dfSorted.iat[indexNum,FIVE_YEAR_HIGH],param,goodSectorDf)
    first = True
    return dfSorted[["Close", "Stage", "support"]]

def getStage(ticker, param, goodSectorDf):
    df = pd.read_pickle("stockData/nyseNasdaq/"+ticker+".pkl")
    if df.empty:
        return pd.DataFrame()
    return returnStageDf(df, param, goodSectorDf)

def getIndustryStage(industry, param, goodSectorDf):
    df = pd.read_pickle('stockData/industriesData/'+str(industry[0])+'/'+industry[1]+'.pkl')
    if df.empty:
        return pd.DataFrame()
    resDf = returnIndustryStageDf(df, param, goodSectorDf)
    resDf.to_csv('sampleIndustryDfs/' + str(industry[1]) + '.csv')
    return resDf

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
#         dfSorted.iat[indexNum,STAGE] = checkIfStage2(indexNum,dfSorted.iat[indexNum,CLOSE],dfSorted.iat[indexNum,VOLUME_PERC],dfSorted.iat[indexNum,RS],dfSorted.iat[indexNum,WMA30_SLOPE],dfSorted.iat[indexNum,WMA30],dfSorted.iat[indexNum-1,STAGE],dfSorted.iat[indexNum-1,CLOSE],dfSorted.iat[indexNum-1,SUPPORT],dfSorted.iat[indexNum,PEAK],dfSorted.iat[indexNum-1,PEAK],dfSorted.iat[indexNum-1,TROUGH],index,dfSorted,dfSorted.iat[indexNum-1,SECOND_BUY],dfSorted.iat[indexNum-1,INITIAL_SUPPORT],dfSorted.iat[indexNum,FIVE_YEAR_HIGH],param)
#     first = True
#     print(len(sectorOfTicker))
#     return dfSorted
    