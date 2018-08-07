'''
Code to plot emotion results for question 1 and 2 in the write up
Also to calculate correlation values for each subplot

Four subplots
1st fixed valence lines, visualise effect on arousal dimension
2nd fixed valence lines, visualise effect on valence dimension
3rd fixed arousal lines, visualise effect on arousal dimension
4th fixed arousal lines, visualise effect on valence dimension
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from sklearn import linear_model

def plot_subplot(low, mean, high, input_dim, output_dim, constant_dim, subplot, letter):
    #'''calculate the average line'''
    # avg_first = (low[1][0] + mean[1][0] + high[1][0])/3
    # avg_second = (low[1][1] + mean[1][1] + high[1][1])/3
    # avg_third = (low[1][2] + mean[1][2] + high[1][2])/3
    # subplot.plot(low[0], [avg_first, avg_second, avg_third], color="gray", label="Average perceived values", linestyle="--")

    '''grid and axes'''
    subplot.grid(b=True, which="both", linestyle='dotted')
    subplot.axhline(y=0, color='k')
    subplot.axvline(x=0, color='k')

    '''ridge regression line'''
    X = np.array(low[0] + mean[0] + high[0]).reshape(-1,1)
    y = np.array(low[1] + mean[1] + high[1]).reshape(-1,1)
    ridge = linear_model.Ridge(alpha=1, fit_intercept=True)
    ridge.fit(X, y)
    new_X = np.linspace(low[0][0], low[0][2], 1000).reshape(-1,1)
    predicted = ridge.predict(new_X)
    subplot.plot(new_X, predicted, color="gray", label="Regression fit", linestyle="--")

    '''plot data'''
    subplot.plot(low[0], low[1], color="yellow", label="Low {}".format(constant_dim))
    subplot.plot(mean[0], mean[1], color="orange", label="Mean {}".format(constant_dim))
    subplot.plot(high[0], high[1], color="red", label="High {}".format(constant_dim))
    subplot.scatter(low[0], low[1], color="yellow", s=15)
    subplot.scatter(mean[0], mean[1], color="orange", s=15)
    subplot.scatter(high[0], high[1], color="red", s=15)

    '''set labels and title'''
    subplot.set_xlabel("Input {}".format(input_dim))
    subplot.set_ylabel("Perceived {}".format(output_dim))
    subplot.set_title("({}) Effect of varying {} on perceived {}".format(letter, input_dim, output_dim))
    subplot.legend(framealpha=0.5)

OUT_DIR = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/plots_and_figures/' #output plots here

_, axarr = plt.subplots(2, 2, figsize=(10,8), gridspec_kw={'wspace':0.25, 'hspace':0.3})
# _, axarr = plt.subplots(2, 2)

plot_emotionbaseline = False
plot_sprocket = True
plot_leslie = False

#assert that we only have one True flag
booleans = [plot_emotionbaseline, plot_sprocket, plot_leslie]
assert len([flag for flag in booleans if flag]) == 1, "You are trying to plot too many datasets"

if plot_emotionbaseline:
    low = [[-1.5, 0, 1.5], [-0.94, -0.94, -0.04]]
    mean = [[-1.5, 0, 1.5], [-0.94, 0.18, 0.94]]
    high = [[-1.5, 0, 1.5], [-0.52, -0.32, 1]]
    input_dim = "arousal"
    output_dim = "arousal"
    constant_dim = "valence"
    x_coord = 0
    y_coord = 0
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'A')

    low = [[-1.5, 0, 1.5], [-0.66, -0.38, 0.58]]
    mean = [[-1.5, 0, 1.5], [-0.58, 0.58, -0.18]]
    high = [[-1.5, 0, 1.5], [-0.32, 0.04, 0.38]]
    input_dim = "arousal"
    output_dim = "valence"
    constant_dim = "valence"
    x_coord = 0
    y_coord = 1
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'B')

    low = [[-1.5, 0, 1.5], [-0.94, -0.94, -0.52]]
    mean = [[-1.5, 0, 1.5], [-0.94, 0.18, -0.32]]
    high = [[-1.5, 0, 1.5], [-0.04, 0.94, 1]]
    input_dim = "valence"
    output_dim = "arousal"
    constant_dim = "arousal"
    x_coord = 1
    y_coord = 0
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'C')

    low = [[-1.5, 0, 1.5], [-0.66, -0.58, -0.32]]
    mean = [[-1.5, 0, 1.5], [-0.38, 0.58, -0.04]]
    high = [[-1.5, 0, 1.5], [0.58, -0.18, 0.38]]
    input_dim = "valence"
    output_dim = "valence"
    constant_dim = "arousal"
    x_coord = 1
    y_coord = 1
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'D')
elif plot_sprocket:
    low = [[-1.5, 0, 1.5], [-0.66,-0.24,0.8]]
    mean = [[-1.5, 0, 1.5], [-0.86,0.52,0.66]]
    high = [[-1.5, 0, 1.5], [0.94,-0.1,0.1]]
    input_dim = "arousal"
    output_dim = "arousal"
    constant_dim = "valence"
    x_coord = 0
    y_coord = 0
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'A')

    low = [[-1.5, 0, 1.5], [-0.52,0.38,0.44]]
    mean = [[-1.5, 0, 1.5], [-0.32,0.72,-0.04]]
    high = [[-1.5, 0, 1.5], [0.8,0.66,0.58]]
    input_dim = "arousal"
    output_dim = "valence"
    constant_dim = "valence"
    x_coord = 0
    y_coord = 1
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'B')

    low = [[-1.5, 0, 1.5], [-0.66,-0.86,0.94]]
    mean = [[-1.5, 0, 1.5], [-0.24,0.52,-0.1]]
    high = [[-1.5, 0, 1.5], [0.8,0.66,0.1]]
    input_dim = "valence"
    output_dim = "arousal"
    constant_dim = "arousal"
    x_coord = 1
    y_coord = 0
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'C')

    low = [[-1.5, 0, 1.5], [-0.52,-0.32,0.8]]
    mean = [[-1.5, 0, 1.5], [0.38,0.72,0.66]]
    high = [[-1.5, 0, 1.5], [0.44,-0.04,0.58]]
    input_dim = "valence"
    output_dim = "valence"
    constant_dim = "arousal"
    x_coord = 1
    y_coord = 1
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'D')
elif plot_leslie:
    low = [[-20, 0, 20], [-0.8,-0.94,-0.52]]
    mean = [[-20, 0, 20], [-0.72,0.04,0.8]]
    high = [[-20, 0, 20], [-0.72,-0.24,0.94]]
    input_dim = "arousal"
    output_dim = "arousal"
    constant_dim = "valence"
    x_coord = 0
    y_coord = 0
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'A')

    low = [[-20, 0, 20], [-0.8,-0.38,0.18]]
    mean = [[-20, 0, 20], [-0.8,0.1,-0.32]]
    high = [[-20, 0, 20], [-0.58,-0.52,-0.04]]
    input_dim = "arousal"
    output_dim = "valence"
    constant_dim = "valence"
    x_coord = 0
    y_coord = 1
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'B')

    low = [[-20, 0, 20], [-0.8,-0.72,-0.72]]
    mean = [[-20, 0, 20], [-0.94,0.04,-0.24]]
    high = [[-20, 0, 20], [0.52,0.8,0.94]]
    input_dim = "valence"
    output_dim = "arousal"
    constant_dim = "arousal"
    x_coord = 1
    y_coord = 0
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'C')

    low = [[-20, 0, 20], [-0.8,-0.8,-0.58]]
    mean = [[-20, 0, 20], [-0.38,0.1,-0.52]]
    high = [[-20, 0, 20], [0.18,-0.32,-0.04]]
    input_dim = "valence"
    output_dim = "valence"
    constant_dim = "arousal"
    x_coord = 1
    y_coord = 1
    plot_subplot(low, mean, high, input_dim.title(), output_dim.title(), constant_dim.title(), axarr[x_coord, y_coord], 'D')

plt.tight_layout()
plt.savefig(OUT_DIR + 'emotion_results_plots.pdf', format='pdf')
# plt.show()
plt.clf()
plt.close()

#calculate correlation value for each subplot and put on the graph
