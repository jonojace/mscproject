'''
Only to be used with leslie simms data

Gets the label_state_align lab files for leslie's data trained on the
tokenprojection model and appends the trained sentence embeddings as features onto end of file
'''

import os
import re
import sys
from helpers import process_transcript
import math
import numpy as np
from glob import glob

#check for correct number of args
if len(sys.argv) != 3:
    print("################################")
    print("python appendSentenceEmbeddingToLabels.py <label_state_align folder> <projection weights file>")
    print("################################")
    raise Exception

'''
for testing

python appendSentenceEmbeddingToLabels.py /group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/tokenprojection/s1/experiments/tokenprojection/acoustic_model/data/label_state_align /afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/projection_weights_backup/tokenprojection/projection_weights_acoustic_model/proj_INFERENCE_epoch_23
'''

'''
for all data

python appendSentenceEmbeddingToLabels.py /afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/leslie_label_state_align/all_data/label_state_align /afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/projection_weights_backup/tokenprojection_alldata/projection_weights_acoustic_model/projection_weights/proj_INFERENCE_epoch_25
'''

label_state_align_folder = sys.argv[1]
projection_weights_file = sys.argv[2]

#load the projection weights file in
with open(projection_weights_file) as f:
    projection_weights = f.readlines()

#get paths to each lab files
paths = glob(os.path.join(label_state_align_folder, '*'))

#only keep paths that are from AVEC2012 and thus have emotion ids
paths = [path for path in paths if '_sent' not in path]

# print(paths, len(paths))

for path in paths:
    #get the contents of the file
    with open(path) as f:
        lines = f.readlines()

    #get the utt_id of this file
    utt_id = int(re.findall('/UTTID:(\d+)', lines[0])[0])

    print('utt_id', utt_id)

    #get the sentence embedding for this utt_id from the projection weights file
    sentence_embedding = projection_weights[utt_id] #get the corresponding row of weights
    sentence_embedding = [float(string) for string in sentence_embedding.split()] #convert from one string to list of floats

    #create the string that will be appended on the end of the lab file for leslie simms
    to_append = []
    for i, dim in enumerate(sentence_embedding, 1):
        #check for scientific notation
        assert 'e' not in '{:.10f}'.format(dim), '{:.10f}'.format(dim) + 'has scientific notation'
        feat = '/DIM' + str(i) + ':' + '{:.10f}'.format(dim)
        to_append.append(feat)
    to_append = ''.join(to_append)

    #append to_append to each line in the lab file
    modified_output = []
    for line in lines:
        state_indicator_idx = line.index('[')
        modified_output.append(line[:state_indicator_idx] + to_append + line[state_indicator_idx:])

    #overwrite the lab file with the new contents
    with open(path, 'w') as f:
        f.write(''.join(modified_output))
