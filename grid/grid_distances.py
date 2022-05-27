from re import T
from turtle import distance
import pandas as pd
import time
import os

from yaml import load

def timer(func): # decorator
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(f'{func.__name__} took {round(end-start, 4)} seconds.')
        return res
    return wrapper
    
# class Distances():
#     @timer
#     def __init__(self):
#         self.dist_df = pd.read_parquet('bangalore_grid_distances.parquet')

#     @timer
#     def get_distances(self, c1, c2): # ~2.5 seconds
#         try:
#             distance = self.dist_df.loc[str(c1+c2)]['distance']
#         except KeyError:
#             distance = self.dist_df.loc[str(c2+c1)]['distance']
#         return distance  

import numpy as np
class Nodes():
    @timer
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.nodes = self.load_data(os.path.join(self.base_dir, 'bangalore_grid/bangalore_grid_cords.csv'))
    
    def load_data(self, csv_name):
        nodes = pd.read_csv(csv_name).to_numpy()
        print(nodes.shape)
        return nodes

    @timer
    def genrate_tsp(self, dataset_size = 10000, tsp_size = 20):
        # genrate 1000 random tsp of length 20
        tsp_list = []
        for i in range(dataset_size):
            idx = np.random.randint(0, self.nodes.shape[0], tsp_size)
            tsp = self.nodes[idx]
            tsp_list.append(tsp)
        return tsp_list

from sqlitedict import SqliteDict
class DBDistances():
    @timer
    def __init__(self, grid_name='bangalore_grid'):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.grid_dir = os.path.join(self.base_dir, grid_name)
        self.db = self.load_db()
    
    @timer
    def load_db(self, db_name='bangalore_grid_distances.sqlite'):
        print(os.path.join(self.grid_dir, db_name))
        db = SqliteDict(os.path.join(self.grid_dir, db_name))
        print("db saved, %d items" % len(db))
        return db

    # @timer # ~0.001 seconds
    def get_distances(self, c1, c2):
        key1 = "[%s, %s, %s, %s]" % (c1[0], c1[1], c2[0], c2[1])
        key2 = "[%s, %s, %s, %s]" % (c2[0], c2[1], c1[0], c1[1])

        try:
            distance = self.db[key1]['distance']
        except KeyError:
            distance = self.db[key2]['distance']
        return distance

class CostFunc():
    def __init__(self):
        self.db = DBDistances()
    
    # @timer # ~0.001 seconds
    def get_cost(self, tsp_sol):
        tsp_sol = tsp_sol.astype(float).round(4).astype(str).tolist()

        cost = 0
        for i in range(len(tsp_sol)):
            cost += self.db.get_distances(tsp_sol[i], tsp_sol[(i+1)%len(tsp_sol)])
        return cost

if __name__ == "__main__":
    # db = DBDistances()
    # c1, c2 = [[12.8566, 77.492], [12.8602, 77.492]]
    # print(db.get_distances(c1, c2))


    n = Nodes()
    dataset = n.genrate_tsp()
