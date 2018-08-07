import os
import re
import sys

'''
Appends speaker IDs to HTS formatted labels
'''

if len(sys.argv) != 8:
    print("################################")
    print("appendSpeakerIDToLabels_TestTime usage:")
    print("python appendSpeakerIDToLabels_TestTime.py <build_your_own_voice> <speaker id to generate> <arousal> <expectancy> <power> <valence> <voice name>")
    print("EG: /afs/inf.ed.ac.uk/user/s17/s1785140/merlin/egs/build_your_own_voice/s1/database/labels/label_state_align/ 1")
    print("################################")
    raise Exception

voice_name = sys.argv[7]

SPEAKER_ID = sys.argv[2]
LABEL_FOLDER = sys.argv[1] + '/s1/experiments/{}/test_synthesis/prompt-lab/'.format(voice_name)

arousal_val = sys.argv[3]
expectancy_val = sys.argv[4]
power_val = sys.argv[5]
valence_val = sys.argv[6]


#get list of all label files
label_files = sorted(os.listdir(LABEL_FOLDER))

#iterate over each one
for lf in label_files:
    #get desired speaker ID to generate at test time from command line argument
    s_id = SPEAKER_ID
    s_id_label = '/K:' + str(s_id) + '='
    arousal = '/L:' + arousal_val
    expectancy = '/M:' + expectancy_val
    power = '/N:' + power_val
    valence = '/O:' + valence_val
    sex = '/GIRL'

    to_add = s_id_label + arousal + expectancy + power + valence + sex

    #read in their data into list of lines
    with open(LABEL_FOLDER + lf) as f:
        data = f.readlines()

    #instantiate list to hold output to write to file
    output = []

    #for each line in the data, append speaker ID to end of line just before end of line char
    #(no state indicators as before as we haven't predicted durations for HMM states)
    for line in data:
        ############################################################################
        #TODO, instead of simply appending speaker id, make it replace the previous one
        #if it exists, else append. so we don't get a bug if we run the script twice
        #also means we can generate different speakers easily with one trained model
        #############################################################################
        #if label file has no additional features just add to end of line
        #otherwise delete additional features from previous synthesis
        idx = line.find('/K') if line.find('/K') != -1 else -1
        output.append(line[:idx] + to_add + line[-1:])

    #overwrite the file with the new lines in the label file that now include a speaker id
    with open(LABEL_FOLDER + lf, 'w') as f:
        f.write(''.join(output))
