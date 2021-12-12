## IMPORTS
import pandas as pd
import pandas_datareader.data as pdr
from pandas import Series, DataFrame
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import datetime
from datetime import date, timedelta
import yfinance as yf
yf.pdr_override()

## TOOL FUNCTIONS
def fullPrint(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)   
def product(df,index):
    if index < 30:
        return 0
    else:
        return df.iloc[index].Close/df.iloc[index-30].Close
def calculateSlope(df,index):
    if index < 31:
        return 0
    else:
        return df.iloc[index]['WMA30']/df.iloc[index-1]['WMA30']

#*Stage Checkers
def checkIfStage1(price,volumePerc, RS, slope, WMA,P4WH,P4WL):
    stageOneIndicator = 0
    falseReason = ""
    if volumePerc<0.3:
        stageOneIndicator+=1
    else:
        falseReason += "volume "
    if slope<=1.025 and slope>=0.995:
        stageOneIndicator+=1
    else:
        falseReason += "slope "
    if P4WH<P4WL*1.15:
        stageOneIndicator+=1
    else:
        falseReason += "range "
    if price <= WMA*1.1 and price>= WMA*0.9:
        stageOneIndicator+=1
    else:
        falseReason += "price "
    if stageOneIndicator>=3:
        return True
    return "False " + falseReason
def checkIfStage2(price,volumePerc, RS, slope, WMA,prevStage,prevClose):
    if volumePerc < 0.3:
        if prevStage != "Stage 2":
            #print(prevStage)
            return "Volume"
    if RS < 0.1 and prevStage != "Stage 2":
        return "RS"
    if RS < 0 and prevStage == "Stage 2":
        return "RS"
    if slope < 1.025 and prevStage != "Stage 2":
        return "Slope"
    if slope < 1.005 and prevStage == "Stage 2":
        return "Slope"
    if price < WMA*1.1 and prevStage != "Stage 2":
        return "Price"
    if price < WMA*0.95 and prevStage == "Stage 2":
        return "Price"
    return "Clear"
def checkStage(price,volumePerc, RS, slope, WMA,P4WH,P4WL,prevStage,prevClose):
    stage1Check = checkIfStage1(price,volumePerc, RS, slope, WMA,P4WH,P4WL)
    stage2Check = checkIfStage2(price,volumePerc, RS, slope, WMA,prevStage,prevClose)
    if stage2Check == "Clear":
        return "Stage 2"
    if stage1Check == True:
        return "Stage 1 " + stage2Check 
    return stage2Check   
def checkStage(price,volumePerc, RS, slope, WMA,P4WH,P4WL,prevStage,prevClose):
    stage1Check = checkIfStage1(price,volumePerc, RS, slope, WMA,P4WH,P4WL)
    stage2Check = checkIfStage2(price,volumePerc, RS, slope, WMA,prevStage,prevClose)
    if stage2Check == "Clear":
        return "Stage 2"
    if stage1Check == True:
        return "Stage 1 " + stage2Check 
    return stage2Check    

## Main Function
def returnStageDf(dfSorted,spDfSorted,hold):
    deltaX = 10.4
    weights = np.arange(1,31)
    sumWeights = np.sum(weights)
    dfSorted['WMA30'] = dfSorted['Close'].rolling(window=30).apply(lambda x: np.sum(weights*x)/sumWeights)
    dfSorted['WMA30Slope'] = dfSorted.apply(lambda x: calculateSlope(dfSorted,dfSorted.index.get_loc(x.name)),axis=1)
    dfSorted['P4WH'] = dfSorted['Close'].rolling(window=4).max()
    dfSorted['P4WL'] = dfSorted['Close'].rolling(window=4).min()
    dfSorted['VolumePerc'] = dfSorted['Volume'].pct_change()
    dfSorted['Percent'] = dfSorted.apply(lambda x: product(dfSorted,dfSorted.index.get_loc(x.name)),axis=1)
    spDfSorted['Percent'] = dfSorted.apply(lambda x: product(spDfSorted,spDfSorted.index.get_loc(x.name)),axis=1)
    dfSorted['RS'] = dfSorted['Percent'] - spDfSorted['Percent']
    dfSorted = dfSorted.dropna()
    dfSorted['Stage'] = ""
    for index, element in dfSorted.iterrows():
        if dfSorted.index.get_loc(index) == 0:
            continue
        dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('Stage')] = checkStage(dfSorted.loc[index]['Close'],dfSorted.loc[index]['VolumePerc'],dfSorted.loc[index]['RS'],dfSorted.loc[index]['WMA30Slope'],dfSorted.loc[index]['WMA30'],dfSorted.loc[index]['P4WH'],dfSorted.loc[index]['P4WL'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['Stage'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['Close'])
    return dfSorted[["Close","Stage"]]

def getStage(ticker,hold):
    today = date.today()
    startDate = today - timedelta(weeks=156)
    threeDays = today - timedelta(days=3)
    today = today.strftime('%Y-%m-%d')
    startDate = startDate.strftime('%Y-%m-%d')
    threeDays = threeDays.strftime('%Y-%m-%d')
    price = pdr.get_data_yahoo(ticker, start=threeDays,end=today).iloc[-1].Close
    if hold != "hold" and price>300:
        return "too Expensive"
    df = pdr.get_data_yahoo(ticker, start=startDate,end=today)
    sp = "^GSPC"
    spdf = pdr.get_data_yahoo(sp, start=startDate,end=today)
    sortLogic = {
        'Close': 'last',
        'Volume': 'sum'
    }
    dfSorted = df.resample("W-FRI").agg(sortLogic)
    spDfSorted = spdf.resample("W-FRI").agg(sortLogic)
    return returnStageDf(dfSorted,spDfSorted,hold)