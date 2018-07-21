'''
Only to be used with leslie simms data

for test time

appends a given sent embedding onto end of prompt-lab files
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
    print("python appendSentenceEmbeddingToLabels_Test.py <prompt-lab folder> <sent embedding file>")
    print("################################")
    raise Exception

'''
for testing

python appendSentenceEmbeddingToLabels.py /group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/tokenprojection/s1/experiments/tokenprojection/acoustic_model/data/label_state_align /afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/projection_weights_backup/tokenprojection/projection_weights_acoustic_model/proj_INFERENCE_epoch_23
'''

prompt_lab_folder = sys.argv[1]
sent_embedding_file = sys.argv[2]

#load the sent embedding file in
with open(sent_embedding_file) as f:
    line = f.readline()  #just get one line as the file only has one line
sent_embedding = [float(string) for string in line.split()]

#NB HARDCODED
#check that we have 10 dimensions
assert len(sent_embedding) == 10

#get paths to each lab files
paths = glob(os.path.join(prompt_lab_folder, '*'))

for path in paths:
    #get the contents of the file
    with open(path) as f:
        lines = f.readlines()

    #create the string that will be appended on the end of the lab file for leslie simms
    to_append = []
    for i, dim in enumerate(sent_embedding, 1):
        assert 'e' not in str(dim) #check for scientific notation
        feat = '/DIM' + str(i) + ':' + str(dim)
        to_append.append(feat)
    to_append = ''.join(to_append)

    #append to_append to each line in the lab file
    modified_output = []
    for line in lines:
        idx = line.find('/DIM1') if line.find('/DIM1') != -1 else -1
        modified_output.append(line[:idx] + to_append + line[-1:])

    #overwrite the lab file with the new contents
    with open(path, 'w') as f:
        f.write(''.join(modified_output))
