import os
import re
import sys
from helpers import resample_samples

'''
Appends speaker IDs to HTS formatted labels
'''

#NB this variable script is for when u want to vary the emotion values over the duration of each utt

if len(sys.argv) != 11:
    print("################################")
    print("appendSpeakerIDToLabels_TestTime usage:")
    print("python appendSpeakerIDToLabels_TestTime.py <build_your_own_voice> <speaker id to generate> <from_arousal> <to_arousal> <from_expectancy> <to_expectancy> <from_power> <to_power> <from_valence> <to_valence>")
    print("EG: /afs/inf.ed.ac.uk/user/s17/s1785140/merlin/egs/build_your_own_voice/s1/database/labels/label_state_align/ 1")
    print("################################")
    raise Exception

LABEL_FOLDER = sys.argv[1] + '/s1/experiments/avec2012/test_synthesis/prompt-lab/'
SPEAKER_ID = sys.argv[2]

for i, val in enumerate(sys.argv):
    print(i, val)

from_arousal = float(sys.argv[3])
to_arousal = float(sys.argv[4])
from_expectancy = float(sys.argv[5])
to_expectancy = float(sys.argv[6])
from_power = float(sys.argv[7])
to_power = float(sys.argv[8])
from_valence = float(sys.argv[9])
to_valence = float(sys.argv[10])


#get list of all label files
label_files = sorted(os.listdir(LABEL_FOLDER))

#iterate over each one
for lf in label_files:
    #get desired speaker ID to generate at test time from command line argument
    s_id = SPEAKER_ID
    s_id_label = '/K:' + str(s_id) + '='

    #read in their data into list of lines
    with open(LABEL_FOLDER + lf) as f:
        data = f.readlines()

    #instantiate list to hold output to write to file
    output = []

    #get the emotion vals for each line in data using resample
    n = len(data) #num of lines in data
    arousal_vals = resample_samples([from_arousal, to_arousal], n)
    expectancy_vals = resample_samples([from_expectancy, to_expectancy], n)
    power_vals = resample_samples([from_power, to_power], n)
    valence_vals = resample_samples([from_valence, to_valence], n)

    #for each line in the data, append speaker ID to end of line just before end of line char
    #(no state indicators as before as we haven't predicted durations for HMM states)
    for line, arousal_val, expectancy_val, power_val, valence_val in zip(data, arousal_vals, expectancy_vals, power_vals, valence_vals):

        arousal = '/L:' + str(arousal_val)
        expectancy = '/M:' + str(expectancy_val)
        power = '/N:' + str(power_val)
        valence = '/O:' + str(valence_val)
        to_add = s_id_label + arousal + expectancy + power + valence

        idx = line.find('/K') if line.find('/K') != -1 else -1
        output.append(line[:idx] + to_add + line[-1:])

    #overwrite the file with the new lines in the label file that now include a speaker id
    with open(LABEL_FOLDER + lf, 'w') as f:
        f.write(''.join(output))
