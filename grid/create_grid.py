import pandas as pd
import numpy as np
from haversine import haversine, Unit # pip install haversine
from itertools import combinations_with_replacement
import time
import os
from tqdm import tqdm

def timer(func): # decorator
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(f'{func.__name__} took {round(end-start, 4)} seconds.')
        return res
    return wrapper

class CSVUtils():
    def __init__(self, grid_name='bangalore_grid') -> None:
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.grid_dir = os.path.join(self.base_dir, grid_name)
        self.create_grid_dir()

    def create_grid_dir(self):
        if not os.path.exists(self.grid_dir):
            os.mkdir(self.grid_dir)
        return self.grid_dir
    @timer
    def save_grid(  self,
                    cords,
                    headers = ["lat", "lng"], 
                    csv_name = "bangalore_grid_cords.csv"
                    ):
        '''
        Save to csv file
        
        Args:
            cords: list of lat, lng coordinates
        
        Returns:
            None
            
        #TODO: Could be made more efficient by saving to a dataframe and then saving to csv
        '''
        with open(os.path.join(self.grid_dir, csv_name), 'w') as f:
            f.write(','.join(headers) + '\n')
            for cord in cords:
                f.write(str(cord[0]) + ',' + str(cord[1]) + '\n')

    @timer
    def save_combinations(self, 
                          combinations, 
                          save_name='bangalore_grid_distances.parquet'
                          ): # takes > 70 seconds
        ''' 
        Save to parquet file
        '''
        df = pd.DataFrame(combinations, columns=["c1", "c2"])
        df['key'] = df["c1"] + df["c2"]
        df['key'] = df['key'].apply(lambda x: str(x))
        df['distance'] = df.apply(lambda x: haversine(x["c1"], x["c2"], unit=Unit.METERS), axis=1)
        df.set_index('key', inplace=True)
        df.to_parquet(os.path.join(self.grid_dir, save_name), index=False)

    @timer
    def save_combinations_to_db(self, 
                                combinations, 
                                save_name='bangalore_grid_distances.sqlite'
                                ):
        from sqlitedict import SqliteDict
        db = SqliteDict(os.path.join(self.grid_dir, save_name))
        # for c1, c2 in tqdm(combinations):
        #     db[str(c1+c2)] = {'c1': c1, 'c2': c2, 'distance': haversine(c1, c2, unit=Unit.METERS)}
        # db.commit()
        # print("db saved, %d items" % len(db))
        db.close()

class Grid(CSVUtils):
    def __init__(self) -> None:
        super().__init__()
        self.center_cords = (12.9716, 77.61) #center coordinate
        self.dist = 400 #meters, num coordinates in each direction
        self.coors = 32 #num coordinates in each direction

    @timer
    def create_grid(self):
        '''
        Create the grid
        
        Args:
            None
        
        Returns:
            grid: list of lat, lng coordinates
        '''
        lat, lon = self.center_cords

        mini, maxi = -self.dist*self.coors, self.dist*self.coors
        n_coord = self.coors*2+1
        axis = np.linspace(mini, maxi, n_coord)
        X, Y = np.meshgrid(axis, axis)

        #avation formulate for offsetting the latlong by offset matrices
        R = 6378137 #earth's radius
        dLat = X/R
        dLon = Y/(R*np.cos(np.pi*lat/180))
        latO = lat + dLat * 180/np.pi
        lonO = lon + dLon * 180/np.pi

        #stack x and y latlongs and get (lat,long) format
        output = np.stack([latO, lonO]).transpose(1,2,0)

        # round to 4 decimal places
        output = np.around(output, 4) 

        points = output.reshape(-1,2)
        points = points.tolist()
        print(f'Created {len(points)} grid points')
        return points
    
    @timer
    def get_all_combinations(self, points):
        '''
        Get all combinations of points
        
        Args:
            points: list of lat, lng coordinates
        
        Returns:
            all_combinations: list of all combinations of points
        '''
        all_combinations = list(combinations_with_replacement(points, 2))
        print("Total combinations: ", len(all_combinations))
        return all_combinations

if __name__ == "__main__":
    print("Creating grid...")
    g = Grid()
    points = g.create_grid()
    all_combinations = g.get_all_combinations(points)
    g.save_grid(points)
    # g.save_combinations(all_combinations)
    g.save_combinations_to_db(all_combinations)
    print("Done")