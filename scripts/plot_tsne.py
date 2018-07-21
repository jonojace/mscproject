'''
file to plot tsne diagram
'''

import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import os, sys
from glob import glob
import re
from collections import defaultdict


'''
the filters used to color different questions on the T-SNE plot
'''
# filters = ['/UTTID'] #used to get the whole dataset and plot as one color
filters = ['/AVEC', '/BLIZ2017']

'''
get the embeddings to transform from disk
'''
#paths
projection_weights_file = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/projection_weights_backup/tokenprojection/projection_weights_acoustic_model/proj_INFERENCE_epoch_23'
label_state_align_folder = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/label_state_align_avec_and_leslie/small_data'

#load weights
with open(projection_weights_file) as f:
    projection_weights = f.readlines()

#get paths to each lab file
paths = glob(os.path.join(label_state_align_folder, '*'))

data = []

for path in paths:
    #get the contents of the lab file
    with open(path) as f:
        lines = f.readlines()

    #get the utt_id of this lab file
    utt_id = int(re.findall('/UTTID:(\d+)', lines[0])[0])

    #filter
    for filt in filters:
        if filt in lines[0]:
            #get the sentence embedding for this utt_id from the projection weights file
            sentence_embedding = projection_weights[utt_id] #get the corresponding row of weights
            sentence_embedding = [float(string) for string in sentence_embedding.split()] #convert from one string to list of floats

            #add to list of all embeddings for this filter
            data.append((sentence_embedding, filt, utt_id))

# print(data)

'''
transform and plot the embeddings
'''
#do TSNE transform
embeddings = [tup[0] for tup in data]
X_embedded = TSNE(n_components=2, random_state=None).fit_transform(np.array(embeddings))

#get list of only the filts
filts = [tup[1] for tup in data]

#get list of only utt_ids
utt_ids = [tup[2] for tup in data]

for f in filters:
    #only get the embeddings that match this filter
    filtered_data = [(embedding, utt_id) for embedding, filt, utt_id in zip(X_embedded, filts, utt_ids) if filt == f]
    filtered_embeddings = [tup[0] for tup in filtered_data]
    filtered_utt_ids = [tup[1] for tup in filtered_data]

    #get data for plotting
    X_Y = np.array(filtered_embeddings)
    Xs = X_Y[:,0]
    Ys = X_Y[:,1]
    label = f.strip('/').title()
    plt.scatter(Xs, Ys, label=label)

    #annotate scatter points with utt_id
    for utt_id, x, y in zip(filtered_utt_ids, Xs, Ys):
        plt.annotate(
            utt_id,
            xy=(x, y),
            xytext=(3,3),
            textcoords='offset points'
        )

#plot settings
plt.xlabel("T-SNE Dim 1")
plt.ylabel("T-SNE Dim 2")
plt.tight_layout()
plt.legend()

#show the plot
plt.show()
