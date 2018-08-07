'''
plot interpolated heatmap for emotion values for the points in sentence embedding t-sne space
'''

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata

OUT_DIR = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/plots_and_figures/' #output plots here

'''initialise your data - we go from top left of cube to bottom right, row by row, from left to right'''
#excited vs bored
# x = [-1, -1, 0, 0, 1, 1, -1, -1, 1, 1, -1, -1, 0, 0, 1, 1]
# y = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1]
# z = [0.86, 0.32, -0.94, -0.72, -0.86, -0.94, 0.94, -0.18, 1, -0.24, -0.32, 0.18, -0.86, -0.8, -0.72, -0.8]

arousal = True
valence = False

if arousal:#averaged arousals
    x = [-1, 0, 1, -1, 1, -1, 0, 1]
    y = [1, 1, 1, 0, 0, -1, -1, -1]
    z = np.array([0.86 + 0.32, -0.94 -0.72, -0.86 -0.94, 0.94 -0.18, 1 -0.24, -0.32 + 0.18, -0.86 -0.8, -0.72 -0.8])
    print(z)
    z = z/2
    print(z)

#test
# x = [0, 1, 2, 0, 2, 0, 1, 2]
# y = [2, 2, 2, 1, 1, 0, 0, 0]
# z = [-1,-1,-1, 0,0, 1,1,1]
if valence: #averaged valences
    x = [-1, 0, 1, -1, 1, -1, 0, 1]
    y = [1, 1, 1, 0, 0, -1, -1, -1]
    z = np.array([-0.1+0.86,-0.72-0.52,-0.18-0.72,0.38+0.44,0.38+0.18,-0.32+0.18,-0.86-0.8,-0.72-0.8])
    print(z)
    z = z/2
    print(z)

'''define grid'''
xi = np.linspace(min(x), max(x), 1000)
yi = np.linspace(min(y), max(y), 1000)

'''grid the data'''
zi = griddata(x, y, z, xi, yi, interp='nn')

'''contour the gridded data, plotting dots at the nonuniform data points'''
plt.figure(figsize=(5,4))
CS = plt.contourf(xi, yi, zi, 15, cmap=plt.cm.rainbow, vmax=zi.max(), vmin=zi.min())
cbar = plt.colorbar(ticks=[zi.min(), (zi.min()+zi.max())/2, zi.max()])
if arousal:
    cbar.ax.set_yticklabels(['Bored', 'Neutral', 'Excited'])
if valence:
    cbar.ax.set_yticklabels(['Negative', 'Neutral', 'Positive'])

'''plot axes'''
plt.axhline(y=0, color='k', linestyle='dotted')
plt.axvline(x=0, color='k', linestyle='dotted')

'''plot the points for where we actually have data'''
# plt.scatter(x,y)

'''label axes'''
plt.xlabel("T-SNE Dim 1")
plt.ylabel("T-SNE Dim 2")

'''plot data points'''
plt.tight_layout()
plt.savefig(OUT_DIR + 'TSNE_heatmap.eps', format='eps')
# plt.show()
