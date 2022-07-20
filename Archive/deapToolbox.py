from deap import creator, tools, base

## Imports Functions from Toolbox
from estimatorToolbox import calculateGroupReturn
from estimatorToolbox import evalReturn
from estimatorToolbox import generate_random_num_attr
from estimatorToolbox import mutate

## Initialize Creator & Toolbox
# Initialize Deap Creator Objects
creator.create("FitnessMax", base.Fitness, weights=(1.0,1,0))
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