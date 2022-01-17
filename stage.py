## IMPORTS
from socket import if_nametoindex
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from datetime import date, timedelta
from yahoo_fin.stock_info import get_data



## TOOL FUNCTIONS
def fullPrint(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)   
def product(df,index):
    if index < 30:
        return 0
    else:
        return df.iloc[index].close/df.iloc[index-30].close
def calculateSlope(df,index):
    if index < 31:
        return 0
    else:
        return df.iloc[index]['wMA30']/df.iloc[index-1]['wMA30']
def peakCheck(df, index):
    if index == 0:
        return df.iloc[index]["close"]
    else:
        return max(df.iloc[index-1]["peak"], df.iloc[index]["close"])
def troughCheck(df, index):
    if index == 0:
        return df.iloc[index]["close"]
    elif df.iloc[index]["peak"]==df.iloc[index]["close"]:
        return df.iloc[index]["close"]
    else:
        return min(df.iloc[index-1]["trough"], df.iloc[index]["close"])

#*Stage Checker
def checkIfStage2(price,volumePerc, RS, slope, wMA30,prevStage,prevClose,prevSupport,peak,prevPeak,prevTrough,index,dfSorted,secondBought,initialSupport):
    dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('support')] = prevSupport
    if prevStage == "Stage 2" or prevStage == "Buy":
        if price < prevSupport*1:
            return "Sell"
        dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('initialSupport')] = initialSupport
        if price == peak and prevPeak != prevClose and prevTrough < prevPeak*0.975:
            dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('support')] = prevTrough
        if secondBought == True:
            if price <= initialSupport*1.05 and dfSorted.loc[index]['trough'] < dfSorted.loc[index]['peak']:
                dfSorted.iloc[dfSorted.index.get_loc(index)]['secondBuy'] = False
                return "Buy"
        return "Clear"
    
    if volumePerc < 0.3:
            return "volume"
    if RS < 0.1:
        return "RS"
    if slope < 1.03:
        return "Slope"
    if price < wMA30*1.1:
        return "Price"
    dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('support')] = prevClose
    dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('initialSupport')] = prevClose
    i = dfSorted.index.get_loc(index)
    while dfSorted.iloc[i, dfSorted.columns.get_loc('trough')]<prevClose:
        dfSorted.iloc[i, dfSorted.columns.get_loc('trough')] = prevClose
        i=i+1
    dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('secondBuy')] = True
    return "Buy"
def checkStage(price,volumePerc, RS, slope, wMA30,prevStage,prevClose,prevSupport,peak,prevPeak,prevTrough,index,dfSorted,secondBought,initialSupport):
    stage2Check = checkIfStage2(price,volumePerc, RS, slope, wMA30,prevStage,prevClose,prevSupport,peak,prevPeak,prevTrough,index,dfSorted,secondBought,initialSupport)
    if stage2Check == "Clear":
        return "Stage 2"
    return stage2Check    

## Main Function
def returnStageDf(dfSorted):
    dfSorted['peak'] = 0
    dfSorted['trough'] = 0
    dfSorted['support'] = 0
    dfSorted['initialSupport'] = 0
    for index, element in dfSorted.iterrows():
        dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('peak')] = peakCheck(dfSorted,dfSorted.index.get_loc(element.name))
        dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('trough')] = troughCheck(dfSorted,dfSorted.index.get_loc(element.name))
    dfSorted['Stage'] = ""
    dfSorted['secondBuy'] = False
    for index, element in dfSorted.iterrows():
        if dfSorted.index.get_loc(index) == 0:
            continue
        dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('Stage')] = checkStage(dfSorted.loc[index]['close'],dfSorted.loc[index]['volumePerc'],dfSorted.loc[index]['RS'],dfSorted.loc[index]['wMA30Slope'],dfSorted.loc[index]['wMA30'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['Stage'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['close'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['support'],dfSorted.loc[index]['peak'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['peak'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['trough'],index,dfSorted,dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['secondBuy'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['initialSupport'])
    return dfSorted[["close","Stage","support","trough","peak"]]

def getStage(ticker):
#     today = date.today()
#     # #200->1000
#     startDate = today - timedelta(weeks=1000)
    # today = today.strftime('%Y-%m-%d')
    # startDate = startDate.strftime('%Y-%m-%d')
    # df = get_data(ticker, start_date=startDate, end_date=today, index_as_date = True, interval="1wk")
    df = pd.read_pickle("stockData/S&P500/"+ticker+".pkl")
    return returnStageDf(df,spdf)