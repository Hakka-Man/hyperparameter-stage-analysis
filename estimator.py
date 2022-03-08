#Imports
from deap import creator, tools, base
import numpy as np
import random
from stage import fullPrint, getStage
from datetime import datetime
import pandas as pd
import yahoo_fin.stock_info as yf
from sklearn.model_selection import train_test_split
import warnings
import pickle

## Warning Statements
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning) 

## Imports Functions from Toolbox
from estimatorToolbox import calculateGroupReturn
from estimatorToolbox import evalReturn
from estimatorToolbox import generate_random_num_attr
from estimatorToolbox import mutate

## Initialize Creator & Toolbox
# Initialize Deap Creator Objects
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)
# Initialize Toolbox
toolbox = base.Toolbox()
toolbox.register("attr_bool", generate_random_num_attr) # Attribute generator 
toolbox.register("individual", tools.initRepeat, creator.Individual, 
    toolbox.attr_bool, 1) # Structure initializers
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evalReturn)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mutate)
toolbox.register("select", tools.selTournament, tournsize=3)

## Initialize Variables 
now = datetime.now()


# Initialize Test/Train Stock Lists
nasdaqList = pd.read_pickle("stockData/tickerList.pkl")
train, test = train_test_split(nasdaqList, test_size=0.3, shuffle=True)
trainSet1, trainSet2, trainSet3  = np.array_split(train,3)
trainSets = [trainSet1, trainSet2, trainSet3]
with open('testSetPickle/trainSet.pkl', 'wb') as f:
    pickle.dump(trainSets, f)

#Initilize Output File & Write Testsets to the TXT File
resultFile = open("resultML.txt","a")
resultFile.write("trainSets "+str(trainSets)+"\n")
resultFile.write("test "+str(test)+"\n")
resultFile.close()

#Initilize Backtest Transaction Database
transactionTemplate = yf.get_data('AAPL', start_date="1995-01-06",end_date= now, index_as_date = True).drop(['open','high','low','close','adjclose','volume','ticker'],axis=1)
transactionTemplate['Dates'] = pd.to_datetime(transactionTemplate.index)
transactionTemplate = transactionTemplate[transactionTemplate['Dates'].dt.weekday == 4]
transactionTemplate = transactionTemplate.drop('Dates', axis = 1)
transactionTemplate.to_pickle("transactionTemplate.pkl")

## Get list of returns of tickers
listOfDf = calculateGroupReturn(train)

## Calculate (and normalize) returns of each folds 
ratio = [1,1,1,1,1,1]
for i in range(6):
    if i < 3:
        l = trainSets[i]
    else:
        l = np.concatenate((trainSets[(i+1)%3],trainSets[(i+2)%3]))
    index = 0
    while index != len(l):
        if l[index] not in listOfDf.columns:
            l = np.delete(l, index)
        else:
            index += 1
    for index, element in listOfDf[l].iterrows():
        #print(element.to_list())
        listOfStockRet = element.to_list()
        while 1.0 in listOfStockRet:
            listOfStockRet.remove(1.0)
        if len(listOfStockRet) != 0:
            ratio[i] = ratio[i] * np.mean(listOfStockRet)     
for i in range(1,6):
    ratio[i] = ratio[i] / ratio[0]
ratio[0] = 1.0
with open('testSetPickle/trainSetRatio.pkl', 'wb') as f:
    pickle.dump(ratio, f)


pop = toolbox.population(n=128)
# Evaluate the entire population
# here
# pool = Pool()
# tempResult = pool.map(toolbox.evaluate, pop)
fitnesses = map(toolbox.evaluate, pop)
print(fitnesses)
# here
# pool.close()
for ind, fit in zip(pop, fitnesses):
    ind.fitness.values = fit
    if ind.fitness.values[0]<=100:
        del ind.fitness.values
badInd = [ind for ind in pop if not ind.fitness.valid]
while len(badInd)!=0:
    for ind in badInd:
        index = pop.index(ind)
        temp = toolbox.individual()
        pop[index] = temp
        del pop[index].fitness.values
    badInd = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, badInd)
    for ind, fit in zip(badInd, fitnesses):
        ind.fitness.values = fit
        if ind.fitness.values[0]<=100:
            del ind.fitness.values
    badInd = [ind for ind in pop if not ind.fitness.valid]

    
# Begin the evolution
for g in range(7):
    np.random.shuffle(train)
    trainSet1, trainSet2, trainSet3  = np.array_split(train,3)
    trainSets = [trainSet1, trainSet2, trainSet3]
    resultFile = open("resultML.txt","a")
    resultFile.write("train "+str(trainSets)+"\n")
    resultFile.close()
    with open('testSetPickle/trainSet.pkl', 'wb') as f:
        pickle.dump(trainSets, f)
    ## Calculate (and normalize) returns of each folds 
    ratio = [1,1,1,1,1,1]
    for i in range(6):
        if i < 3:
            l = trainSets[i]
        else:
            l = np.concatenate((trainSets[(i+1)%3],trainSets[(i+2)%3]))
        index = 0
        while index != len(l):
            if l[index] not in listOfDf.columns:
                l = np.delete(l, index)
            else:
                index += 1
        for index, element in listOfDf[l].iterrows():
            #print(element.to_list())
            listOfStockRet = element.to_list()
            while 1.0 in listOfStockRet:
                listOfStockRet.remove(1.0)
            if len(listOfStockRet) != 0:
                ratio[i] = ratio[i] * np.mean(listOfStockRet)     
    for i in range(1,6):
        ratio[i] = ratio[i] / ratio[0]
    ratio[0] = 1.0
    with open('testSetPickle/trainSetRatio.pkl', 'wb') as f:
        pickle.dump(ratio, f)
    print("-- Generation %i --" % g)
    resultFile = open("resultML.txt","a")
    resultFile.write("-- Generation %i --" % g+"\n")
    resultFile.close()
    
    # Select the next generation individuals
    offspring = toolbox.select(pop, len(pop))
    # Clone the selected individuals
    offspring = list(map(toolbox.clone, offspring))

    # Apply crossover and mutation on the offspring
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < 0.5:
            toolbox.mate(child1[0], child2[0])
            del child1.fitness.values
            del child2.fitness.values

    for mutant in offspring:
        if random.random() < 0.2:
            toolbox.mutate(mutant[0])
            del mutant.fitness.values        

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    # here
    # pool = Pool()
    # fitnesses = pool.map(toolbox.evaluate, invalid_ind)
    # pool.close()
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    
    # Replace population
    pop[:] = offspring

    # Gather all the fitnesses in one list and print the stats
    fits = [ind.fitness.values[0] for ind in pop]
    
    length = len(pop)
    mean = sum(fits) / length
    sum2 = sum(x*x for x in fits)
    std = abs(sum2 / length - mean**2)**0.5
    
    print("  Min %s" % min(fits))
    print("  Max %s" % max(fits))
    print("  Avg %s" % mean)
    print("  Std %s" % std)

print("-- End of (successful) evolution --")
best_ind = tools.selBest(pop, 1)[0]
print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))



