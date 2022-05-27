from torch.utils.data import Dataset
import torch
import os
import pickle
from problems.tsp.state_tsp import StateTSP
from utils.beam_search import beam_search

import time
import numpy as np

import grid.grid_distances as gd
n = gd.Nodes()
c = gd.CostFunc()

class TSP(object):

    NAME = 'tsp'

    @staticmethod
    def get_costs(dataset, pi): # 2.48 seconds for 512 TSP instances
        # Check that tours are valid, i.e. contain 0 to n -1
        assert (
            torch.arange(pi.size(1), out=pi.data.new()).view(1, -1).expand_as(pi) ==
            pi.data.sort(1)[0]
        ).all(), "Invalid tour"

        d = dataset.gather(1, pi.unsqueeze(-1).expand_as(dataset))
        d = np.round(d.numpy(), 4)

        costs = []
        for sol in d:
            costs.append(c.get_cost(sol)) # custom grid cost function

        return torch.FloatTensor(costs), None
        
    @staticmethod
    def make_dataset(*args, **kwargs):
        return TSPDataset(*args, **kwargs)

    @staticmethod
    def make_state(*args, **kwargs):
        return StateTSP.initialize(*args, **kwargs)

    @staticmethod
    def beam_search(input, beam_size, expand_size=None,
                    compress_mask=False, model=None, max_calc_batch_size=4096):

        assert model is not None, "Provide model"

        fixed = model.precompute_fixed(input)

        def propose_expansions(beam):
            return model.propose_expansions(
                beam, fixed, expand_size, normalize=True, max_calc_batch_size=max_calc_batch_size
            )

        state = TSP.make_state(
            input, visited_dtype=torch.int64 if compress_mask else torch.uint8
        )

        return beam_search(state, beam_size, propose_expansions)


class TSPDataset(Dataset):
    
    def __init__(self, filename=None, size=50, num_samples=1000000, offset=0, distribution=None):
        super(TSPDataset, self).__init__()

        self.data_set = []
        if filename is not None:
            assert os.path.splitext(filename)[1] == '.pkl'

            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.data = [torch.FloatTensor(row) for row in (data[offset:offset+num_samples])]
        else:
            # Use grid TSP instance generator
            data = n.genrate_tsp(num_samples, size)
            self.data = [torch.FloatTensor(row) for row in (data[offset:offset+num_samples])]

        self.size = len(self.data)

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        return self.data[idx]
