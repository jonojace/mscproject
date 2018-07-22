'''
script to plot histograms of the values for each sentence embedding dimension, similar to what you did with the emotion dimensions
'''

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
from glob import glob
from math import log10, floor

#directories
FIRST_EPOCH_PROJECTION_WEIGHTS_FILE = '/Users/jonojace/Downloads/plotting/proj_INFERENCE_epoch_1'
LAST_EPOCH_PROJECTION_WEIGHTS = '/Users/jonojace/Downloads/plotting/proj_INFERENCE_epoch_23'
FIG_NAME = 'figure.eps' # output plots here

#load in data
with open(FIRST_EPOCH_PROJECTION_WEIGHTS_FILE) as f:
    proj_w_1 = f.readlines()
with open(LAST_EPOCH_PROJECTION_WEIGHTS) as f:
    proj_w_2 = f.readlines()

#only load in weights from proj_w_2 if they are not equal to the proj_w_1
#if they ARE equal, then these weights were never trained in the projection matrix
weights = []
for line1, line2 in zip(proj_w_1, proj_w_2):
    if line1 != line2:
        weights.append(line2)

#convert the items in weights to floats
for i, line in enumerate(weights):
    weights[i] = [float(string) for string in line.split()]

#get number of sentence embedding dims
n_dims = len(weights[0])
print(weights[0])

#get subplots
n_rows = 2
n_cols = 5
_, axarr = plt.subplots(n_rows, n_cols, figsize=(10,5))

#define the function that helps plot histograms for a given dimension
def plot_hist(dim, values, subplot):
    subplot.hist(values, bins=50)
    mean = np.mean(values)
    subplot.axvline(mean, color='k', linestyle='dashed', linewidth=1) #plot the mean as a line
    subplot.set_title('Dimension ' + str(dim + 1))

for dim in range(n_dims):
    #get all values in weights for each dimension
    this_dim_values = [line[dim] for line in weights]

    #get right position for this dim in the array of subplots
    x = dim // n_cols
    y = dim % n_cols

    #plot a histogram in the subplot position for this dim and its values
    plot_hist(dim, this_dim_values, axarr[x, y])

plt.tight_layout(pad=0, h_pad=0.5, w_pad=0.5)
plt.savefig(FIG_NAME, format='eps')
# plt.show()
