'''
file to plot tsne diagram
'''

import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import os, sys
import matplotlib.colors as colors
from glob import glob
import re
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import copy



def get_avg_emotion_values(lines):
    for line in lines:
        # no scientific notation
        # a, e, p, v, utt_id = re.findall('/L:([\d.-]+)/M:([\d.-]+)/N:([\d.-]+)/O:([\d.-]+)/UTTID:(\d+)', line)[0]

        #scientific notation
        a, e, p, v= re.findall('/L:([\d.e-]+)/M:([\d.e-]+)/N:([\d.e-]+)/O:([\d.e-]+)', line)[0]

        all_a, all_e, all_p, all_v = [], [], [], []

        #append val to totals
        all_a.append(float(a))
        all_e.append(float(e))
        all_p.append(float(p))
        all_v.append(float(v))

    #get the average emotion val for each emotion dimension
    avg_a = np.mean(all_a)
    avg_e = np.mean(all_e)
    avg_p = np.mean(all_p)
    avg_v = np.mean(all_v)

    # print(avg_a, avg_e, avg_p, avg_v)

    return avg_a, avg_e, avg_p, avg_v


'''
the filters used to color different questions on the T-SNE plot
'''
filters = ['/UTTID'] #used to get the whole dataset and plot as one color
# filters = ['/AVEC', '/BLIZ2017'] #used to plot datasets as different colors
# filters = ['/AVEC']

'''
get the embeddings to transform from disk
'''
#NB SMALL DATA paths
# projection_weights_file = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/projection_weights_backup/tokenprojection/projection_weights_acoustic_model/proj_INFERENCE_epoch_23'
# label_state_align_folder = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/label_state_align_avec_and_leslie/small_data'

#NB BIG DATA paths
projection_weights_file = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/projection_weights_backup/tokenprojection_alldata/projection_weights_acoustic_model/projection_weights/proj_INFERENCE_epoch_25'
label_state_align_folder = '/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/tokenprojection/s1/experiments/tokenprojection_alldata/acoustic_model/data/label_state_align'

#where to output the plot
output_dir = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/plots_and_figures/sent_embedding_TSNE'

#load weights
with open(projection_weights_file) as f:
    projection_weights = f.readlines()

#get paths to each lab file
paths = glob(os.path.join(label_state_align_folder, '*'))

data = []

print('Constructing lab and weights data from disk')
for path in paths:
    #get the contents of the lab file
    with open(path) as f:
        lines = f.readlines()

    #get the utt_id of this lab file
    utt_id = int(re.findall('/UTTID:(\d+)', lines[0])[0])
    print(utt_id)

    #filter
    for filt in filters:
        if filt in lines[0]:
            if not filters == ['/AVEC']:
                #get the sentence embedding for this utt_id from the projection weights file
                sentence_embedding = projection_weights[utt_id] #get the corresponding row of weights
                sentence_embedding = [float(string) for string in sentence_embedding.split()] #convert from one string to list of floats

                #add to list of all embeddings for this filter
                data.append((sentence_embedding, filt, utt_id))
            elif filters == ['/AVEC']:
                '''additionally extract the avg value for each emotion dimension from this lab file'''
                #get the sentence embedding for this utt_id from the projection weights file
                sentence_embedding = projection_weights[utt_id] #get the corresponding row of weights
                sentence_embedding = [float(string) for string in sentence_embedding.split()] #convert from one string to list of floats

                avg_a, avg_e, avg_p, avg_v = get_avg_emotion_values(lines)
                data.append((sentence_embedding, filt, utt_id, avg_a, avg_e, avg_p, avg_v))


#get list of only the filts
filts = [tup[1] for tup in data]
#get list of only utt_ids
utt_ids = [tup[2] for tup in data]

#get the emotion data
if filters == ['/AVEC']:
    arousals = [tup[3] for tup in data]
    expectancys = [tup[4] for tup in data]
    powers = [tup[5] for tup in data]
    valences = [tup[6] for tup in data]

'''
transform and plot the embeddings
'''
#do TSNE transform
print('Running TSNE transform')
embeddings = [tup[0] for tup in data]
X_embedded = TSNE(n_components=2, random_state=1337).fit_transform(np.array(embeddings))

#find out the largest distances from the center
X_temp = copy.deepcopy(X_embedded)
distances = []
def distance(x, y):
    '''returns distance of point x,y from the origin'''
    return (x**2 + y**2)**(1.0/2.0)
for x,y in X_temp:
    distances.append(distance(x,y))
distances.sort()
print('top 20 distances', distances[-20:])

#set distance threshold, we label any points that are above this threshold
distance_threshold = 22.0


print('Plotting the data')
for f in filters:
    #only get the embeddings that match this filter
    if not filters == ['/AVEC']:
        filtered_data = [(embedding, utt_id) for embedding, filt, utt_id in zip(X_embedded, filts, utt_ids) if filt == f]
        filtered_embeddings = [tup[0] for tup in filtered_data]
        filtered_utt_ids = [tup[1] for tup in filtered_data]

        utt_ids_edges = [6747, 7176, 3363, 4476,
                         3362, 8256, 6309, 2167,
                         4987, 6678, 3476, 8060,
                         7661, 8679, 9371, 6685,
                          796, 7176, 3363, 4476,
                         7192, 6794, 1621, 4488,
                         7739, 2921, 1981, 6993,
                         2588, 5780, 8751, 2622]
        filtered_data_edges = [(embedding, utt_id) for embedding, filt, utt_id in zip(X_embedded, filts, utt_ids) if filt == f and utt_id in utt_ids_edges]
        filtered_embeddings_edges = [tup[0] for tup in filtered_data_edges]
        filtered_utt_ids_edges = [tup[1] for tup in filtered_data_edges]
    elif filters == ['/AVEC']:
        filtered_data = [(embedding, utt_id, a, e, p, v) for embedding, filt, utt_id, a, e, p, v in zip(X_embedded, filts, utt_ids, arousals, expectancys, powers, valences) if filt == f]
        filtered_embeddings = [tup[0] for tup in filtered_data]
        filtered_utt_ids = [tup[1] for tup in filtered_data]
        filtered_arousals = [tup[2] for tup in filtered_data]
        filtered_expectancys = [tup[3] for tup in filtered_data]
        filtered_powers = [tup[4] for tup in filtered_data]
        filtered_valences = [tup[5] for tup in filtered_data]

    #get data for plotting
    X_Y = np.array(filtered_embeddings)
    Xs = X_Y[:,0]
    Ys = X_Y[:,1]
    if filters == ['/AVEC']: #if we only have one filter
        # colour_values = filtered_arousals
        # emotion = 'Arousal'
        # colour_values = filtered_expectancys
        # emotion = 'Expectancy'
        # colour_values = filtered_powers
        # emotion = 'Power'
        colour_values = filtered_valences
        emotion = 'Valence'
        cmap="seismic"
        print('MAX', np.max(colour_values), 'MIN', np.min(colour_values))
    else:
        colour_values = None
        cmap=None
    label = f.strip('/').title()
    # width = 12
    # height = 8
    width = 12
    height = 8
    plt.figure(figsize=(width, height))
    plt.scatter(Xs, Ys,
               c=colour_values, #array of values to map to colors using colormap
            #    cmap="viridis", #which color map to use
               cmap=cmap, #which color map to use
            #    norm=colors.PowerNorm(gamma=1/2), #used to redistribute numbers so fewer are centered around the centre
            #    norm=colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=-1.0, vmax=1.0),
               alpha=1,
               s=15, #size of points
               label=label #label of given dataset
    )

    plot_utt_ids = True
    if plot_utt_ids:
        #annotate scatter points with utt_id
        for utt_id, x, y in zip(filtered_utt_ids, Xs, Ys):
            # if distance(x,y) > distance_threshold:
            plt.annotate(
                utt_id,
                xy=(x, y),
                xytext=(3,3),
                textcoords='offset points',
            )

    plot_edges = True
    if plot_edges:
        '''plot the points that will be used in listening test for Q3 as a different color'''
        X_Y = np.array(filtered_embeddings_edges)
        Xs = X_Y[:,0]
        Ys = X_Y[:,1]
        if filters != ['/AVEC']:
            label = 'Edge points'
            plt.scatter(Xs, Ys,
                       alpha=1,
                       s=15, #size of points
                       label=label) #label of given dataset



#plot settings
if filters == ['/AVEC']:
    title = "T-SNE Transformed Sentence Embeddings with {} Value Heatmap".format(emotion)
else:
    title = 'test'

plt.xlabel("T-SNE Dim 1")
plt.ylabel("T-SNE Dim 2")
plt.title(title)
plt.tight_layout()
plt.legend()
# plt.colorbar() #used for legend for the colour map!

plt.savefig(os.path.join(output_dir, title + '.eps'), format='eps')

#show the plot
plt.show()

plt.clf()
plt.close()
