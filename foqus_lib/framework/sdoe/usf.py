from operator import lt, gt
import numpy as np
from .distance import compute_dist
import time

# -----------------------------------
def compute_min_dist(mat, scl, hist=None):
    dmat = compute_dist(mat, scl=scl, hist=hist)
    min_dist = np.min(dmat, axis=0)
    return dmat, min_dist


def criterion(cand,    # candidates
              args,    # scaling factors for included columns
              nr,      # number of restarts (each restart uses a random set of <nd> points)
              nd,      # design size <= len(candidates)
              mode='maximin', hist=None):

    mode = mode.lower()
    assert mode in ['maximin', 'minimax'], 'MODE {} not recognized.'.format(mode)
    if mode == 'maximin':
        best_val = -1
        fcn = np.mean
        cond = gt
    elif mode == 'minimax':
        best_val = 99999
        fcn = np.max
        cond = lt

    # indices of type ...
    idx = args['xcols']  # Input
    
    # scaling factors
    scl = args['scale_factors']
    scl = scl[idx].values

    # history, if provided
    if hist is not None:
        hist = hist[idx].values

    best_cand = []
    _best_rand_sample = []

    t0 = time.time()
    for i in range(nr):

        print('Random start {}'.format(i))
        
        # sample without replacement <nd> indices
        rand_index = np.random.choice(cand.index, nd, replace=False)
        # extract the <nd> rows
        rand_cand = cand.loc[rand_index]
        # extract the relevant columns (of type 'Input' only) for dist computations
        dmat, min_dist = compute_min_dist(rand_cand[idx].values, scl, hist=hist)
        dist = fcn(min_dist)

        if cond(dist, best_val):
            best_cand = rand_cand    
            best_index = rand_index  # for debugging
            best_val = dist          # for debugging
            best_dmat = dmat         # used for ranking candidates

        elapsed_time = time.time() - t0

    results = {'best_cand': best_cand,
               'best_index': best_index,
               'best_val': best_val,
               'best_dmat': best_dmat,
               'dmat_cols': idx,      
               'mode': mode,
               'design_size': nd,
               'num_restarts': nr,
               'elapsed_time': elapsed_time}
         
    return results
