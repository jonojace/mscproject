import os
import re
import sys

'''
Appends:
    Speaker ID to generate average voice
    Emotion IDs equal to average values
    Female sex ID, to make it better for VC to leslie simms voice
'''

if len(sys.argv) != 3:
    print("################################")
    print("appendSpeakerIDToLabels_TestTime usage:")
    print("python appendSpeakerIDToLabels_TestTime_sprocket.py <build_your_own_voice> <voice_name>")
    print("EG: /afs/inf.ed.ac.uk/user/s17/s1785140/merlin/egs/build_your_own_voice/s1/database/labels/label_state_align/ 1")
    print("################################")
    raise Exception

VOICE_NAME = sys.argv[2]
LABEL_FOLDER = sys.argv[1] + '/s1/experiments/{}/test_synthesis/prompt-lab/'.format(VOICE_NAME)

#these values are the average from each emotion dimension
arousal_val = -0.083341168
expectancy_val = 34.1405567
power_val = 0.375480657
valence_val = 0.06304983773

#vary a dimension if u want...
# arousal_val = 1

print('appending:', arousal_val, expectancy_val, power_val, valence_val)

#get list of all label files
label_files = sorted(os.listdir(LABEL_FOLDER))

#get desired speaker ID to generate at test time from command line argument
#first way of generating average speaker (don't trigger any speaker id question)
# s_id_label = '/K:0='
#second way of generating average speaker (trigger only female speaker ids)
# s_id_label = '/K:1=' + '/K:3=' + '/K:5=' + '/K:7=' + '/K:9=' + '/K:10=' + '/K:11=' + '/K:12=' + '/K:13=' + '/K:15=' + '/K:17=' + '/K:19=' + '/K:20='

s_id_label = '/K:0='

sex_id = '/GIRL'

arousal = '/L:' + str(arousal_val)
expectancy = '/M:' + str(expectancy_val)
power = '/N:' + str(power_val)
valence = '/O:' + str(valence_val)

#iterate over each one
for lf in label_files:
    to_add = s_id_label + sex_id + arousal + expectancy + power + valence

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
