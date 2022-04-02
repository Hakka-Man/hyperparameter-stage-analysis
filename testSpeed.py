from stage import getStage
import pandas as pd
import time
from multiprocessing import Pool
import os
import multiprocessing

procCount = 7



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
            #print(df.at[date,'MA30Slope'],df.at[date,'RS'])
            #!!!!!!!! or for new params
            #!!!!!!!!
            #!!!!!!!!
            #!!!!!!!!
            if  df.at[date,'MA30Slope'] > 0.992549883242513 and df.loc[date,'RS'] > -0.3044455098712273:
                if df.at[date,'close'] > df.at[date,'MA30']:
                    #print(df.at[date,'ticker'])
                    listOfSector.append(df.at[date,'ticker'])
        except: 
            pass
        # print(listOfSector)
    goodSectorDf.iat[index,0] = set(listOfSector)
    index = index + 1
nasdaqList = pd.read_pickle("stockData/tickerList.pkl")

def calculatePi(stock, multi):
    if multi:
        print(multiprocessing.current_process())
    getStage(stock,[0.10684256968972883, 1.1421709856192384, 0.27350824408318475, 1.0231080328602544, 1.0760547872425865, 1.2745231615209662, 0.9038554056254413, 1.0764846753295985, 1.2709398376771783, 0.992549883242513, -0.3044455098712273, 0.9467020070162686, 1.0014235121991226, 0.8164237632733558, 0.9867262709280287],goodSectorDf)
if __name__ == '__main__':
    pool = Pool(processes=procCount)
    start = time.time()
    pool.starmap(calculatePi,zip(nasdaqList[0:1000],[True for i in range(len(nasdaqList))]))
    multiple_results = [pool.apply_async(os.getpid, ()) for i in range(procCount)]
    print([res.get(timeout=1) for res in multiple_results])
    pool.close()
    print("Finished in: {:.2f}s".format(time.time()-start))
    start = time.time()
    for i in nasdaqList[0:1000]:
        j = calculatePi(i,False)
    print("Finished in: {:.2f}s".format(time.time()-start))
