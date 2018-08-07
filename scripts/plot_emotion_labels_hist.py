import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
from glob import glob
from math import log10, floor

#script to create and plot range of values that each emotion dimension can takes
IN_DIR = '/group/project/disnv/AVEC2012/emotion labels/{0}/FC_{0}_labels/' #original AVEC2012 directory
OUT_DIR = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/plots_and_figures/' #output plots here

data = defaultdict(list)

#for each emotion
for dataset in ['train', 'devel', 'test']:
    for emotion in ['arousal', 'expectancy', 'power', 'valence']:
        #get all files for this emotion and in this dataset folder
        paths = glob(IN_DIR.format(dataset) + '*' + emotion + '.dat')
        for p in paths:
            with open(p) as f:
                lines = f.readlines()
                #load all the data for this emotion into the data defaultdict
                data[emotion].extend(float(line) for line in lines)

#sanity check
assert len(data['arousal']) == len(data['expectancy']) == len(data['power']) == len(data['valence'])
# print('Number of frames of data for each emotion is', len(data['arousal']))

def plot_hist(emotion, subplot):
    #make histograms for each emotion in 4 subplots
    subplot.hist(data[emotion], bins=50)
    # print(min(data[emotion]), max(data[emotion]))
    round_to_n = lambda x, n: round(x, -int(floor(log10(abs(x)))) + (n - 1))
    subplot.set_xticks([round_to_n(x,2) for x in np.arange(min(data[emotion]),max(data[emotion]), (max(data[emotion])-min(data[emotion]))/5 )])
    std = np.std(data[emotion])
    mean = np.mean(data[emotion])
    upper = mean + 2*std
    lower = mean - 2*std
    print(emotion, 'mean is', mean, 'lower bound is', lower, 'upper is', upper)
    subplot.axvline(mean, color='k', linestyle='dashed', linewidth=1) #plot the mean as a line
    # subplot.axvspan(lower, upper, alpha=0.25, color='grey')
    subplot.set_title(emotion.title())

# plot_hist(emotion, plt)

# four axes returned as a 2D array, subplots
f, axarr = plt.subplots(2, 2)
plot_hist('arousal', axarr[0,0])
plot_hist('expectancy', axarr[0,1])
plot_hist('power', axarr[1,0])
plot_hist('valence', axarr[1,1])

# axarr[0, 0].hist(data['arousal'], bins=50)
# axarr[0, 0].set_title('Arousal')
# axarr[0, 1].hist(data['expectancy'], bins=50)
# axarr[0, 1].set_title('Expectancy')
# axarr[1, 0].hist(data['power'], bins=50)
# axarr[1, 0].set_title('Power')
# axarr[1, 1].hist(data['valence'], bins=50)
# axarr[1, 1].set_title('Valence')

plt.tight_layout() #make sure that titles and axes don't overlap

plt.savefig(OUT_DIR + 'emotion_analysis.eps', format='eps')

# #make histograms for each emotion in 4 subplots
# plt.hist(data['arousal'], bins=50)
# # print(min(data['arousal']), max(data['arousal']))
# plt.xticks(np.arange(min(data['arousal']),max(data['arousal']), 0.2))
# std = np.std(data['arousal'])
# mean = np.mean(data['arousal'])
# # print('lower bound is', mean - 2*std, 'upper is', mean + 2*std)
# plt.axvline(mean, color='k', linestyle='dashed', linewidth=1)
# plt.axvspan(mean - 2*std, mean + 2*std, alpha=0.25, color='grey')
# plt.title('Arousal')

# plt.savefig(OUT_DIR + 'arousal.png')


# plt.show()

#also plot mean and variance
