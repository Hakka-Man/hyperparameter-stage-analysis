## IMPORTS
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
        return df.iloc[index]['WMA30']/df.iloc[index-1]['WMA30']

#*Stage Checker
def checkIfStage2(price,volumePerc, RS, slope, WMA,prevStage,prevClose):
    if volumePerc < 0.3:
            return "Volume"
    if RS < 0.1:
        return "RS"
    if slope < 1.03:
        return "Slope"
    if price < WMA*1.1 and prevStage != "Stage 2":
        return "Price"
    return "Clear"
def checkStage(price,volumePerc, RS, slope, WMA,prevStage,prevClose):
    stage2Check = checkIfStage2(price,volumePerc, RS, slope, WMA,prevStage,prevClose)
    if stage2Check == "Clear":
        return "Stage 2"
    return stage2Check    

## Main Function
def returnStageDf(dfSorted,spDfSorted):
    weights = np.arange(1,31)
    sumWeights = np.sum(weights)
    dfSorted['WMA30'] = dfSorted['close'].rolling(window=30).apply(lambda x: np.sum(weights*x)/sumWeights)
    dfSorted['WMA30Slope'] = dfSorted.apply(lambda x: calculateSlope(dfSorted,dfSorted.index.get_loc(x.name)),axis=1)
    dfSorted['VolumePerc'] = dfSorted['volume'].pct_change()
    dfSorted['Percent'] = dfSorted.apply(lambda x: product(dfSorted,dfSorted.index.get_loc(x.name)),axis=1)
    spDfSorted['Percent'] = dfSorted.apply(lambda x: product(spDfSorted,spDfSorted.index.get_loc(x.name)),axis=1)
    dfSorted['RS'] = dfSorted['Percent'] - spDfSorted['Percent']
    dfSorted = dfSorted.dropna()
    dfSorted['Stage'] = ""
    for index, element in dfSorted.iterrows():
        if dfSorted.index.get_loc(index) == 0:
            continue
        dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('Stage')] = checkStage(dfSorted.loc[index]['close'],dfSorted.loc[index]['VolumePerc'],dfSorted.loc[index]['RS'],dfSorted.loc[index]['WMA30Slope'],dfSorted.loc[index]['WMA30'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['Stage'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['close'])
    return dfSorted[["close","Stage"]]

def getStage(ticker):
    today = date.today()
    startDate = today - timedelta(weeks=200)
    today = today.strftime('%Y-%m-%d')
    startDate = startDate.strftime('%Y-%m-%d')
    df = get_data(ticker, start_date=startDate, end_date=today, index_as_date = True, interval="1wk")
    sp = "^GSPC"
    spdf = get_data(sp, start_date=startDate, end_date=today, index_as_date = True, interval="1wk")
    return returnStageDf(df,spdf)