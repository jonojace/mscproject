'''
For implementing Oliver's sentence level control vectors

For all .lab files in a folder

Gets the whole list of them (n of them)

Assigns them each an utterance ID
From 0 to n-1

i.e.
if we have n=5 label files, they will have Utt id as follows
'arctic_a0001.lab', utt_id=0
'arctic_a0002.lab', utt_id=1
'arctic_a0003.lab', utt_id=2
'arctic_a0004.lab', utt_id=3
'arctic_a0005.lab', utt_id=4

Then append this utt ID to the end of the .lab file
'''

'''
path for testing:

/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/slt_arctic/s1/experiments/slt_arctic_demo/acoustic_model/data/label_state_align
'''

import os
import re
import sys

if len(sys.argv) != 4:
    print("################################")
    print("python appendUtteranceIDToLabels.py <path_to_lab_state_align_folder> <has_state_indicator> <start of test set>")
    print("################################")
    raise Exception

#NB <start of test set> is used so we know which sentences correspond to the test set
#this is because we want the test set lab files to have an utt_id of 0
#this is so at test time we can change the 0th row of P and use this
#0th row as the control vector for EVERY test file.
#in slt arctic example
#1-50 train
#51-55 valid
#56-60 test
#so <start of test set> should be ***56***
#utt 56-60 will receive utt_id of 0
#utt 1 will get utt_id of 0
#utt 2 will get utt_id of 1
#...
#utt 55 will get utt_id of 54 VALIDATION SET
#utt 56 will get utt_id of 55 TEST SET
#call this script as python appendUtteranceIDToLabels.py <path_to_folder> 1 56

LABEL_FOLDER = sys.argv[1]

#TODO instead of using has_state_indicator, use regex to find out where feature ends
#i.e./P:(\d+), use this to find where to start and where to begin

#has_state_indicator should be either '0' or '1'
#'0' indicates label file doesn't have state indicator
#otherwise '1'
has_state_indicator = int(sys.argv[2])
assert has_state_indicator == 1 or has_state_indicator == 0

start_of_test_set = int(sys.argv[3])

#get list of all label files
label_files = sorted(os.listdir(LABEL_FOLDER))

#get total number of label files
n = len(label_files)

#iterate over each label file
for utt_id, label_file in zip(range(n), label_files):
    #set utt_id to 0 if this utt is in the test set.
    if utt_id >= start_of_test_set - 1:
        utt_id = 0
    print(utt_id, label_file)

    #read in data from label_file
    with open(os.path.join(LABEL_FOLDER, label_file)) as f:
        # print(f.readlines()[0])

        data = f.readlines()
        #instantiate list to hold output to write to file
        output = []

        #for each line in the data, append utt ID to end of line just before end of line char/state indicator
        for line in data:
            #get the str index to use if we haven't appended utt id to this file before
            if has_state_indicator:
                #place new label just before state indicator
                end_idx = line.index('[')
            else:
                #place new label just before end of line symbol '\n'
                end_idx = -1

            if line.find('/P') != -1: #if we have appended utt ID before to this line
                start_idx = line.find('/P')
            else: #we haven't appended utt ID before to this line
                start_idx = end_idx

            # print('end_idx', end_idx, 'start_idx', start_idx)

            #if label file has no additional features just add to end of line
            #otherwise delete additional features from previous synthesis
            to_add = '/UTTID:' + str(utt_id)
            output.append(line[:start_idx] + to_add + line[end_idx:])
            # print(line[:start_idx] + to_add + line[end_idx:])

            # 'G:0_0/H:7=5@1=2|L-L%/I:7=3/J:14+8-2/P:123[3]'
            # 'G:0_0/H:7=5@1=2|L-L%/I:7=3/J:14+8-2[3]'
            # idx = line.find('/P') if line.find('/P') != -1 else -1

        #overwrite the file with the new lines in the label file that now include a speaker id
        with open(os.path.join(LABEL_FOLDER, label_file), 'w') as f:
            f.write(''.join(output))
