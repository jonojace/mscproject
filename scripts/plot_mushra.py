'''
plot average mushra scores for each system along with std error bars
'''

import numpy as np
import matplotlib.pyplot as plt

N = 6

means = [
15.09555556,
22.43555556,
23.51444444,
69.03555556,
77.58444444,
97.66666667
]

stds = [
3.16234925,
7.030250904,
2.869303535,
5.442508868,
5.086755132,
3.112739951
]

systems = [
"sprocket arousal",
"sprocket",
"emotionbaseline",
"leslie",
"tokenprojection",
"groundtruth"
]

systems = [s.title() for s in systems]

OUT_DIR = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/plots_and_figures/' #output plots here

x_pos = np.arange(len(systems))

# Build the plot
fig, ax = plt.subplots(figsize=(8,6))
ax.bar(x_pos, means, width=0.66, yerr=stds, align='center', alpha=1, ecolor='black', capsize=5, edgecolor="black", color="coral")
ax.set_ylabel('MUSHRA Score')
ax.set_xlabel('Systems')
ax.set_xticks(x_pos)
ax.set_xticklabels(systems)
ax.yaxis.grid(True)
ax.set_axisbelow(True)



# Save the figure and show
plt.tight_layout()
plt.savefig(OUT_DIR + 'mushra_scores.eps', format='eps')
plt.show()
