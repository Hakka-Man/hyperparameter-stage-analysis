import torch
import numpy as np
import pandas as pd
from util import DataLoaderS
import copy

model = torch.load('modelNoNormalization.pt')
print(model)
device = 'cuda'
data_dir = './multivariate-time-series-data/exchange_rate.txt'
data = DataLoaderS(data_dir, 0.6, 0.2, device, 3, 24*7)
X = data.train[0]
Y = data.train[1]
batch_size = 4


model.eval()
predict = None
test = None
print(len(X))
for X, Y in data.get_batches(X, Y, batch_size, False):
    X = torch.unsqueeze(X,dim=1)
    X = X.transpose(2,3)
    with torch.no_grad():
        output, adj_matrix = model(X)
    output = torch.squeeze(output)
    if len(output.shape)==1:
        output = output.unsqueeze(dim=0)
    if predict is None:
        predict = output
        test = Y
    else:
        predict = torch.cat((predict, output))
        test = torch.cat((test, Y))
print(predict)
print(test)