import numpy as np

def root_mean_squared_error(targets, predictions):
    return round(np.sqrt(np.mean(np.power(targets-predictions, 2))),3)

def mean_absolute_error(targets, predictions):
    return round(np.mean(np.abs(targets-predictions)),3)
