import numpy as np

def simulate_total(lam, sims=10000):
    return np.random.poisson(lam, sims)

def prob_over(results, line):
    return (results > line).mean()