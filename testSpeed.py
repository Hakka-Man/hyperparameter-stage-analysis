import pandas as pd
import time
from multiprocessing import Pool
import os
import multiprocessing

procCount = 22

def calculatePi(x, multi):
    if multi:
        print(multiprocessing.current_process())
    # Initialize denominator
    k = 1
    
    # Initialize sum
    s = 0
    for l in range(100):
        for i in range(100000):
            # even index elements are positive
            if i % 2 == 0:
                s += 4/k
            else:
                # odd index elements are negative
                s -= 4/k
            # denominator is odd
            k += 2
if __name__ == '__main__':
    pool = Pool(processes=7)
    start = time.time()
    pool.starmap(calculatePi,zip(range(12000),[True for i in range(procCount)]))
    multiple_results = [pool.apply_async(os.getpid, ()) for i in range(procCount)]
    print([res.get(timeout=1) for res in multiple_results])
    pool.close()
    print("Finished in: {:.2f}s".format(time.time()-start))
    start = time.time()
    for i in range(procCount):
        j = calculatePi(i,False)
    print("Finished in: {:.2f}s".format(time.time()-start))
