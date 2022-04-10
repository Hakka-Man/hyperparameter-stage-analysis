from StockStageEstimator import StockStageEstimator
import pandas as pd
import numpy as np
import random
from datetime import datetime
import mariadb
import sys
import os
from dotenv import load_dotenv

load_dotenv()

### ENV CONSTANT
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')

### Connect To DB
try:
    conn = mariadb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=3306,
        database="stock",
        autocommit=True
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
cur = conn.cursor()

### CONSTANT VARIABLES ###

## Mutation Noise 
mutationNoises = []
mutationNoises.append(np.random.normal(0, 0.025)) # 0 - Five Year High
mutationNoises.append(np.random.normal(0, 0.075)) # 1 - Volume Perc
mutationNoises.append(np.random.normal(0, 0.015)) # 2 - RS
mutationNoises.append(np.random.normal(0, 0.005)) # 3 - Slope
mutationNoises.append(np.random.normal(0, 0.0125)) # 4 - Price v WMA30
mutationNoises.append(np.random.normal(0, 0.015)) # 5 - Price v Initial Support
mutationNoises.append(np.random.normal(0, 0.005)) # 6 - Prev Trough v Peak
mutationNoises.append(np.random.normal(0, 0.01)) # 7 - Price v Prev Support
mutationNoises.append(np.random.normal(0, 0.0125)) # 8 - Price v Prev Close
mutationNoises.append(np.random.normal(0, 0.0005)) # 9 - Sector MA30 Slope
mutationNoises.append(np.random.normal(0, 0.0025)) # 10 - Sector RS
mutationNoises.append(np.random.normal(0, 0.0025)) # 11 - SPDF Price v WMA30
mutationNoises.append(np.random.normal(0, 0.0002)) # 12 - SPDF WMA30 Slope
mutationNoises.append(np.random.normal(0, 0.0025)) # 13 - SPDF Sell P v WMA30
mutationNoises.append(np.random.normal(0, 0.0002)) # 14 - SPDF Sell WMA30 Slope

## Get returns of a ticker list
def calculateGroupReturn(list):
    monthlyReturn = pd.read_pickle("transactionTemplate.pkl")
    monthlyReturn = monthlyReturn.resample('M').mean()
    monthlyReturn.index = monthlyReturn.index.strftime("%Y:%m")
    currentColumn = -1
    for symbol in list:
        if symbol in monthlyReturn.columns:
            continue
        try:
            df = pd.read_pickle("stockData/nyseNasdaq/"+symbol+".pkl")
        except:
            print(symbol)
            continue
        if not (df['close'] != 0).all() or df.empty:
            if df.empty:
                print(symbol)
            continue
        monthlyReturn[symbol] = 1
        currentColumn += 1
        monthCheck = df.index[0].strftime("%Y:%m")
        lastPrice = df.iat[0,0]
        initialPrice = df.iat[0,0]
        for index, element in df.iterrows():
            if (index.strftime("%Y:%m") != monthCheck):
                if (initialPrice == 0): continue
                if (lastPrice / initialPrice >= 1.01 and lastPrice / initialPrice < 2):
                    rowNumber = monthlyReturn.index.get_loc(index.strftime("%Y:%m"))
                    monthlyReturn.iat[rowNumber, currentColumn] = (lastPrice / initialPrice)
                initialPrice = element[0]
                lastPrice = element[0]
                monthCheck = index.strftime("%Y:%m")
            lastPrice = element[0]
    return monthlyReturn

## Calculate Goodsector & Initialize Estimator Object 
def evalReturn(individual):
    print(individual[0])
    now = datetime.now()
    now = now.strftime("%Y-%m-%d-%H:%M")
    transaction = pd.read_pickle("transactionTemplate.pkl")
    transaction['holding'] = np.empty((len(transaction), 0)).tolist()
    SectorDict = {
    "Energy":"XLE","Technology":"XLK",
    "Communication Services":"XLC",
    "Consumer Staples":"XLP",
    "Health Care":"XLV",
    "Consumer Cyclical":"XLY",
    "Industrial":"XLI",
    "Utilities":"XLU",
    "Materials":"XLB",
    "Financial":"XLF",
    "Real Estate":"XLRE"}
    sectorDfList = []
    for sector in SectorDict.values():
        sectorDfList.append(pd.read_pickle("stockData/sectorCharts/"+sector+".pkl"))
        goodSectorDf = sectorDfList[0].drop(['open','high','low','adjclose','close','ticker','volume','percent','MA30','MA30Slope','RS'],axis=1)
        goodSectorDf['Sectors'] = [[] for _ in range(len(goodSectorDf))]
        goodSectorDf.index = sectorDfList[0].index
        index = 0
        for date in sectorDfList[0].index:
            listOfSector = []
            for df in sectorDfList:
                try:
                    # print(df.at[date,'MA30Slope'],df.at[date,'RS'])
                    # print(individual[0][9],individual[0][10])
                    if  df.at[date,'MA30Slope'] > individual[0][9] and df.at[date,'RS'] > individual[0][10]:
                        if df.at[date,'close'] > df.at[date,'MA30']:
                            # print(df.at[date,'ticker'])
                            listOfSector.append(df.at[date,'ticker'])
                except: 
                    pass
                # print(listOfSector)
            goodSectorDf.iat[index,0] = set(listOfSector)
            index = index + 1
    stockStageEstimator = StockStageEstimator(individual[0], goodSectorDf)
    scores = stockStageEstimator.score()
    debugFile = open("estimatorData/debug"+date.today().strftime('%Y-%m-%d')+".txt","a")
    debugFile.write(str(individual[0])+"\n")
    if scores == -1:
        debugFile.write(str(np.average(scores))+"\n")
        debugFile.write(str(stockStageEstimator.getReturns())+"\n")
        debugFile.close()
        return 0,
    result = stockStageEstimator.result()
    debugFile.write(str(np.average(scores[0]))+"\n")
    debugFile.write(str(np.average(scores[1]))+"\n")
    debugFile.write(str(stockStageEstimator.getReturns())+"\n")
    debugFile.write(str(result)+"\n")
    debugFile.close()
    if np.average(scores[0]) >  0.1:
        return 0,
    if np.average(scores[1]) > 1.3:
        return 0,
    paramFile = open("estimatorData/params"+date.today().strftime('%Y-%m-%d')+".txt","a")
    paramFile.write(str(individual[0])+"\n")
    paramFile.write(str(result)+"\n")
    paramFile.close()
    
    cur.execute("INSERT INTO Params (param,result) VALUES (?, ?)", (individual[0], result))

    resultFile = open("estimatorData/resultML"+date.today().strftime('%Y-%m-%d')+".txt","a")
    resultFile.write(str(individual[0])+"\n")
    resultFile.write(str(np.average(scores[0]))+"\n")
    resultFile.write(str(np.average(scores[1]))+"\n")
    resultFile.write(str(stockStageEstimator.getReturns())+"\n")
    resultFile.write(str(result)+"\n")
    resultFile.close()
    return result

### DEAP Evolutionary Functions ###

## Generating individuals
def generate_random_num_attr():
  original = np.array([0,  # 0 - Five Year High
                        0, # 1 - Volume Perc
                        0, # 2 - RS
                        0, # 3 - Slope
                        0, # 4 - Price v WMA30
                        0, # 5 - Price v Initial Support
                        0, # 6 - Prev Trough v Peak
                        0, # 7 - Price v Prev Support
                        0, # 8 - Price v Prev Close
                        0.995, # 9 - Sector MA30 Slope
                        0, # 10 - Sector RS
                        0.9, # 11 - SPDF Price v WMA30
                        0.995, # 12 - SPDF WMA30 Slope
                        0.85, # 13 - SPDF Sell P v WMA30
                        0.985]) # 14 - SPDF Sell WMA30 Slope
  noises = []
  sum_list = []

  noises.append(random.uniform(0,1))
  noises.append(random.uniform(0.1,2.5))
  noises.append(random.uniform(-0.1,0.4))
  noises.append(random.uniform(0.9,1.1))
  noises.append(random.uniform(1,1.4))
  noises.append(random.uniform(1, 1.3))
  noises.append(random.uniform(0.8, 1))
  noises.append(random.uniform(0.8, 1.1))
  noises.append(random.uniform(1.2, 1.5))
  noises.append(np.random.normal(0, 0.008))
  noises.append(np.random.normal(0, 0.2))

  noises.append(np.random.normal(0, 0.05))
  noises.append(np.random.normal(0, 0.008))
  noises.append(np.random.normal(0, 0.05))
  noises.append(np.random.normal(0, 0.008))

  while original[11] + noises[11] < original[13] + noises[13]:
    noises[11] = np.random.normal(0, 0.05)
    noises[13] = np.random.normal(0, 0.05)
  while original[12] + noises[12] < original[14] + noises[14]:
    noises[12] = np.random.normal(0, 0.004)
    noises[14] = np.random.normal(0, 0.004)
  
  for (item1, item2) in zip(original, noises):
      sum_list.append(item1+item2)
  
  return sum_list

## Mutating Individuals
def mutate(individual):
    size = len(individual)
    for i in range(0,size):
        if random.random() > 0.9:
            individual[i] = individual[i] + mutationNoises[i]
    return individual,