import pandas as pd

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
                if (lastPrice / initialPrice >= 1.01 and lastPrice / initialPrice < 2):
                    rowNumber = monthlyReturn.index.get_loc(index.strftime("%Y:%m"))
                    monthlyReturn.iat[rowNumber, currentColumn] = (lastPrice / initialPrice)
                initialPrice = element[0]
                lastPrice = element[0]
                monthCheck = index.strftime("%Y:%m")
            lastPrice = element[0]
    return monthlyReturn