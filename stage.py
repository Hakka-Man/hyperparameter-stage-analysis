## IMPORTS
from socket import if_nametoindex
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from datetime import date, timedelta
from yahoo_fin.stock_info import get_data

goodSector = pd.read_pickle("stockData/goodSector.pkl")
sectorOfTicker = pd.read_pickle("stockData/sector.pkl")


## TOOL FUNCTIONS
def fullPrint(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)  

#*Stage Checker
def checkIfStage2(price,volumePerc, RS, slope, wMA30,prevStage,prevClose,prevSupport,peak,prevPeak,prevTrough,index,dfSorted,secondBought,initialSupport,fiveYearHigh,param):
    dfSorted.at[index, 'support'] = prevSupport
    if prevStage == "Stage 2" or prevStage == "Buy":
        if price < prevSupport*param[7]:
            return "Sell"
        dfSorted.at[index, 'initialSupport'] = initialSupport
        if price == peak and prevTrough < prevPeak*param[6]:
            dfSorted.at[index, 'support'] = prevTrough
        if secondBought == True:
            dfSorted.at[index, 'secondBuy'] = True
            if price <= initialSupport*param[5] and dfSorted.loc[index]['trough'] < dfSorted.loc[index]['peak']:
                dfSorted.at[index, 'secondBuy'] = False                
                return "Buy"
        return "Stage 2"
    try:
        if sectorOfTicker[dfSorted.at[index,'ticker']] in goodSector.at[index.strftime('%Y-%m-%d'),'Sectors']:
            pass
        else:
            return "bad sector"
    except:
        return "bad sector"
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
    dfSorted.at[index, 'support'] = prevClose
    dfSorted.at[index, 'initialSupport'] = prevClose
    i = dfSorted.index.get_loc(index)
    while i < dfSorted.shape[0] and dfSorted.at[index, 'trough']<prevClose:
        dfSorted.iloc[i, dfSorted.columns.get_loc('trough')] = prevClose
        i=i+1
    dfSorted.at[index, 'secondBuy'] = True
    return "Buy"


## Main Function
def returnStageDf(dfSorted,param):
    for index, element in dfSorted.iterrows():
        if dfSorted.index.get_loc(index) == 0:
            continue
        dfSorted.at[index, 'Stage'] =  checkIfStage2(100,1,1,1,80,"Stage 2",100,80,100,95,80,index,dfSorted,True,60,100,param)
        #dfSorted.at[index, 'Stage'] =  checkIfStage2(dfSorted.loc[index]['close'],dfSorted.loc[index]['volumePerc'],dfSorted.loc[index]['RS'],dfSorted.loc[index]['WMA30Slope'],dfSorted.loc[index]['WMA30'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['Stage'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['close'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['support'],dfSorted.loc[index]['peak'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['peak'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['trough'],index,dfSorted,dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['secondBuy'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['initialSupport'],dfSorted.loc[index]['fiveYearHigh'],param)
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