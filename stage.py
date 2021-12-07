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
import plotly.graph_objects as go
from plotly.subplots import make_subplots

## TOOL FUNCTIONS
def fullPrint(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)   
def product(df,index):
    if index < 30:
        return 0
    else:
        return df.iloc[index].Close/df.iloc[index-30].Close

#*Stage Checkers
def checkIfStage1(price,volumePerc, RS, slope, WMA,P4WH,P4WL):
    stageOneIndicator = 0
    falseReason = ""
    if volumePerc<0.2:
        stageOneIndicator+=1
    else:
        falseReason += "volume "
    if slope<=0.5 and slope>=-0.3:
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
def checkIfStage2(price,volumePerc, RS, slope, WMA,prevStage):
    if volumePerc < 0.2:
        if prevStage != "Stage 2":
            #print(prevStage)
            return "Volume"
    if RS < 0.1:
        return "RS"
    if slope < 0.5:
        return "Slope"
    if price < WMA*1.1:
        return "Price"
    return "Clear"
def checkStage(price,volumePerc, RS, slope, WMA,P4WH,P4WL,prevStage):
    stage1Check = checkIfStage1(price,volumePerc, RS, slope, WMA,P4WH,P4WL)
    stage2Check = checkIfStage2(price,volumePerc, RS, slope, WMA,prevStage)
    if stage1Check == True and stage2Check == "Clear":
        return "Error"
    if stage1Check == True:
        return "Stage 1 " + stage2Check 
    if stage2Check == "Clear":
        return "Stage 2"
    return stage2Check  

## Main Function
def returnStageDf(ticker):
    ##Variables
    sp = "^GSPC"
    sortLogic = {
        'Close': 'last',
        'Volume': 'sum'
    }
    deltaX = 10.4
    df = pdr.get_data_yahoo(ticker, start="2016-01-01",end="2021-11-26")
    spdf = pdr.get_data_yahoo(sp, start="2016-01-01",end="2021-11-26")
    dfSorted = df.resample("W-FRI").agg(sortLogic)
    spDfSorted = spdf.resample("W-FRI").agg(sortLogic)
    weights = np.arange(1,31)
    sumWeights = np.sum(weights)
    dfSorted['30WMA'] = dfSorted['Close'].rolling(window=30).apply(lambda x: np.sum(weights*x)/sumWeights)
    dfSorted['30WMASlope'] = dfSorted['30WMA'].diff()*500/(dfSorted['Close'].rolling(window=104).max()-dfSorted['Close'].rolling(window=104).min())/deltaX
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
        dfSorted.iloc[dfSorted.index.get_loc(index), dfSorted.columns.get_loc('Stage')] = checkStage(dfSorted.loc[index]['Close'],dfSorted.loc[index]['VolumePerc'],dfSorted.loc[index]['RS'],dfSorted.loc[index]['30WMASlope'],dfSorted.loc[index]['30WMA'],dfSorted.loc[index]['P4WH'],dfSorted.loc[index]['P4WL'],dfSorted.iloc[dfSorted.index.get_loc(index) - 1]['Stage'])
    return dfSorted[["Close","Stage"]]
