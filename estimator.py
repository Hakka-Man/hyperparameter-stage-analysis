#Imports
from deap import creator, tools, base
import numpy as np
import timeit
from stage import fullPrint, getStage
from datetime import datetime, date, timedelta
from sklearn.base import BaseEstimator
import random
import pandas as pd
import yahoo_fin.stock_info as yf
from sklearn.model_selection import train_test_split
import pickle

# Imports Functions from Toolbox
from estimatorToolbox import calculateGroupReturn

# Initialize Variables 
now = datetime.now()

# Initialize Deap Creator Objects
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# Initialize Test/Train Stock Lists
nasdaqList = pd.read_pickle("stockData/tickerList.pkl")
train, test = train_test_split(nasdaqList, test_size=0.3, shuffle=True)
trainSet1, trainSet2, trainSet3  = np.array_split(train,3)
trainSets = [trainSet1, trainSet2, trainSet3]

#Initilize Output File
resultFile = open("resultML.txt","a")
resultFile.write("train "+str(train)+"\n")
resultFile.write("test "+str(test)+"\n")
resultFile.close()

#Initilize Backtest Transaction Database
transactionTemplate = yf.get_data('AAPL', start_date="1995-01-06",end_date= now, index_as_date = True).drop(['open','high','low','close','adjclose','volume','ticker'],axis=1)
transactionTemplate['Dates'] = pd.to_datetime(transactionTemplate.index)
transactionTemplate = transactionTemplate[transactionTemplate['Dates'].dt.weekday == 0]
transactionTemplate = transactionTemplate.drop('Dates', axis = 1)
transactionTemplate.to_pickle("transactionTemplate.pkl")




