## IMPORTS
from fileinput import close
from socket import if_nametoindex
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from datetime import date, timedelta
from yahoo_fin.stock_info import get_data

goodSector = pd.DataFrame()
spdf = pd.read_pickle("stockData/Spy.pkl")
sectorOfTicker = pd.read_pickle("stockData/nasdaq.pkl")
sectorOfNyse = pd.read_pickle("stockData/nyse.pkl")
sectorOfTicker.update(sectorOfNyse)

#CONSTANTS
PEAK = 9
TROUGH = 10
SUPPORT = 11
INITIAL_SUPPORT = 12
SECOND_BUY = 14
SHORT_PEAK = 16
SHORT_TROUGH = 17
RESISTANCE = 15

## TOOL FUNCTIONS
def fullPrint(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)

#*Stage Checker
def checkIfStage4(
    i,price,volumePerc, RS, slope, wMA30,prevStage,prevClose,prevResistance,peak,prevPeak,prevTrough,index,dfSorted,secondBought,initialSupport,fiveYearHigh,param,goodSectorDf):
    if prevStage == "Stage 4" or prevStage == "Sell Short":
        if price < prevPeak:
            # update shortPeak and shortTrough
            dfSorted.iat[i,SHORT_PEAK] = price
            dfSorted.iat[i,SHORT_TROUGH] = price
        else:
            dfSorted.iat[i,SHORT_PEAK] = prevPeak
            dfSorted.iat[i,SHORT_TROUGH] = min(prevTrough, price)
        if price >= prevResistance*param[5] or price > wMA30*param[6]:
            return "Cover Buy"

        dfSorted.iat[i,RESISTANCE] = prevResistance

        if price == dfSorted.iat[i,SHORT_TROUGH] and prevResistance < prevTrough*param[6]:
            dfSorted.iat[i,RESISTANCE] = prevPeak
        return "Stage 4"
        
    if price > wMA30*param[0]:
        return "Price"
    if slope > param[1]:
        return "Slope"
    if volumePerc < param[2]:
        return "volume"
    if RS > param[3]:
        return "RS"
    if price < prevClose:
        dfSorted.iat[i,SHORT_PEAK] = price
        dfSorted.iat[i,SHORT_TROUGH] = price
    else:
        dfSorted.iat[i,SHORT_PEAK] = price
        dfSorted.iat[i,SHORT_TROUGH] = price*0.95
    
    return "Sell Short"
  


## Main Function
def returnStageDf(dfSorted,param,goodSectorDf):
    first = True
    for index in dfSorted.index:
        if first:
            if dfSorted.index.get_loc(index) == 0:
                first = False
                continue
        prevIndex = index - timedelta(weeks=1)
        i = dfSorted.index.get_loc(index)
        dfSorted.at[index, 'Stage'] = checkIfStage4(i,dfSorted.at[index,'close'],dfSorted.at[index,'volumePerc'],dfSorted.at[index,'RS'],dfSorted.at[index,'WMA30Slope'],dfSorted.at[index,'WMA30'],dfSorted.at[prevIndex,'Stage'],dfSorted.at[prevIndex,'close'],dfSorted.iat[i-1,11],dfSorted.iat[i,PEAK],dfSorted.iat[i-1,PEAK],dfSorted.iat[i-1,TROUGH],index,dfSorted,dfSorted.at[prevIndex,'secondBuy'],dfSorted.iat[i-1,INITIAL_SUPPORT],dfSorted.at[index,'fiveYearHigh'],param,goodSectorDf)
    first = True
    return dfSorted[["close","Stage"]]

def getStage(ticker,param, goodSectorDf):
#     today = date.today()
#     # #200->1000
    
    # today = today.strftime('%Y-%m-%d')
    # startDate = startDate.strftime('%Y-%m-%d')
    # df = get_data(ticker, start_date=startDate, end_date=today, index_as_date = True, interval="1wk")
    try:
        df = pd.read_pickle("stockData/nyseNasdaq/"+ticker+".pkl")
        return returnStageDf(df,param, goodSectorDf)
    except:
        return pd.DataFrame()

def getFullDf(ticker,param):
    dfSorted = pd.read_pickle("stockData/nyseNasdaq/"+ticker+".pkl")
    first = True
    for index in dfSorted.index:
        if first:
            if dfSorted.index.get_loc(index) == 0:
                first = False
                continue
        prevIndex = index - timedelta(weeks=1)
        i = dfSorted.index.get_loc(index)
        dfSorted.at[index, 'Stage'] = checkIfStage4(i,dfSorted.at[index,'close'],dfSorted.at[index,'volumePerc'],dfSorted.at[index,'RS'],dfSorted.at[index,'WMA30Slope'],dfSorted.at[index,'WMA30'],dfSorted.at[prevIndex,'Stage'],dfSorted.at[prevIndex,'close'],dfSorted.iat[i-1,11],dfSorted.iat[i,PEAK],dfSorted.iat[i-1,PEAK],dfSorted.iat[i-1,TROUGH],index,dfSorted,dfSorted.at[prevIndex,'secondBuy'],dfSorted.iat[i-1,INITIAL_SUPPORT],dfSorted.at[index,'fiveYearHigh'],param)
    first = True
    print(len(sectorOfTicker))
    return dfSorted
    