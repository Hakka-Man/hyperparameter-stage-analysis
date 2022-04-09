from sklearn.base import BaseEstimator
from stage import getStage
import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.model_selection import train_test_split

## CONSTANTS
HOLDING = 0
TOTAL = 1

class StockStageEstimator(BaseEstimator):
    def __init__(self, paramList = [0.20, 1.39, 0.35, 0.93, 1.09, 1.22, 0.98, 0.98, 1.38, 0.99, -0.01, 0.97, 0.99, 0.96, 0.98], goodSectorDf = pd.DataFrame, sets = [[]]):
        self.paramList = paramList
        self.goodSectorDf = goodSectorDf
        self.returns = [0,0,0,0,0,0]
        self.sets = pd.read_pickle("testSetPickle/trainSet.pkl")
        self.scores = [0,0,0]
        self.ratio = pd.read_pickle("testSetPickle/trainSetRatio.pkl")
    
    ## Calculate Returns base
    def evalFit(self, tickers, goodSectorDf):
        transactionFit = pd.read_pickle("transactionTemplate.pkl")
        transactionFit['holding'] = np.empty((len(transactionFit), 0)).tolist()
        #print("Reach #1")
        for symbol in tickers:
            df = getStage(symbol,self.paramList,goodSectorDf)
            buyDf = pd.read_pickle('stockData/nyseNasdaq/'+symbol+'Buy.pkl')
            inStage = False
            buyTwice = False
            if df.empty:
                continue
            if buyDf['open'].eq(0).any().any():
                continue
            for index, element in df.iterrows():
                open = 0
                monday = index + timedelta(3)
                i = transactionFit.index.get_loc(index)
                if element.Stage == "Stage 2" or element.Stage == "Buy":
                    if monday in buyDf.index:
                        open = buyDf.at[monday,'open']
                    else:
                        open = element.close
                    #delete
                    transactionFit.iat[int(i),HOLDING].append((symbol,open,0))
                    if buyTwice:
                        transactionFit.iat[i, HOLDING].append((symbol,open,0))
                    if element.Stage == "Buy" and inStage:
                        transactionFit.iat[i, HOLDING].append((symbol,open,0))
                        buyTwice = True
                    inStage = True
                    continue
                if "Sell" == element.Stage[0:4]:
                    if monday in buyDf.index:
                        open = buyDf.at[monday,'open']
                    else:
                        open = element.close
                    transactionFit.iat[i, HOLDING].append((symbol,open,-1))
                    if buyTwice:
                        transactionFit.iat[i, HOLDING].append((symbol,open,-1))
                    inStage = False
                    buyTwice = False
        #print("Reach #2")
        total = 100
        first = True
        transactionFitCopy = transactionFit
        transactionFitCopy['total'] = 0
        transactionFitCopy.to_csv("onlyShare.csv")
        #print("Reach #3")
        for index, element in transactionFitCopy.iterrows():
            indexNum = transactionFitCopy.index.get_loc(index)
            if first:
                first = False
                transactionFitCopy.iat[indexNum,1] = 100
                # print(i,transactionFitCopy.iat[i,1],"#1")
                continue
            if len(element.holding) == 0:
                transactionFitCopy.iat[indexNum,1] = transactionFitCopy.iat[indexNum-1,1]
                # print(i,transactionFitCopy.iat[i,1],"#2")
                continue
            else:
                prevData = transactionFitCopy.iat[indexNum-1, 0]
                if len(prevData):
                    total = 0
                    removeList = []
                    close = 0
                    for i in range(len(prevData)):
                        for j in range(len(element.holding)):
                            if element.holding[j][0] == prevData[i][0]:
                                close = element.holding[j][1]
                                if element.holding[j][2] == -1:
                                    removeList.append(element.holding[j])
                                break
                        total += close*prevData[i][2]
                    transactionFitCopy.iat[indexNum,1] = total
                    # print(i,transactionFitCopy.iat[indexNum,1],"#3")
                    for delete in removeList:
                        if delete in element.holding:
                            element.holding.remove(delete)
                else:
                    transactionFitCopy.iat[indexNum,1] = transactionFitCopy.iat[indexNum-1,1]
                    # print(i,transactionFitCopy.iat[i,1],"#4")
            if len(element.holding):
                allocation = total/len(element.holding)
            for i in range(len(element.holding)):
                element.holding[i] = (element.holding[i][0],element.holding[i][1],allocation/element.holding[i][1])
        stockHolding  = 0
        transactionFitCopy.to_csv("estimatorTest.csv")
        for i in transactionFitCopy.iterrows():
            stockHolding += len(i[1]['holding'])
        if stockHolding/(transactionFitCopy.shape[0])<(len(tickers)/1000) or transactionFitCopy.iat[-1,TOTAL]<=100:
            print(stockHolding)
            print(transactionFitCopy.iloc[-1]['total'])
            return -1
        if transactionFitCopy.iloc[-1]['total'] < 1000:
            return -1
        transactionFitCopy.to_pickle("transactionDfs/transactionDf"+str(self.paramList[0])+".pkl")
        return transactionFitCopy.iloc[-1]['total']

    def fit(self):
        for i in range(3):
            setsCombined = np.concatenate((self.sets[(i+1)%3],self.sets[(i+2)%3]))
            self.returns[i*2] = self.evalFit(setsCombined, self.goodSectorDf)
            if self.returns[i*2] == -1:
                return -1
            self.returns[i*2+1] = self.evalFit(self.sets[i%4], self.goodSectorDf)
            if self.returns[i*2+1] == -1:
                return -1
        return 0
    
    def score(self):
        if self.fit() == -1:
            return -1
        for i in range(3):
            self.scores[i] = np.absolute(((self.returns[i*2])/100/self.ratio[i])**(1/22)-((self.returns[i*2+1])/100/self.ratio[3+i])**(1/22))
        return self.scores
    
    def result(self):
        return np.average(self.returns)
    
    def getReturns(self):
        return self.returns