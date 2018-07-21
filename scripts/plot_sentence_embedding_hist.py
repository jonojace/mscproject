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

#script to create and plot range of values that each emotion dimension can takes
first_epoch_projection_weights =
last_epoch_projection_weights =
OUT_DIR = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/plots_and_figures/' #output plots here
