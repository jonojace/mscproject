import os
import re
import sys

'''
Appends:
    Speaker ID to generate average voice
    Emotion IDs equal to average values
    Female sex ID, to make it better for VC to leslie simms voice
'''

if len(sys.argv) != 2:
    print("################################")
    print("appendSpeakerIDToLabels_TestTime usage:")
    print("python append_TP_feats_TestTime.py <prompt-lab folder>")
    print("EG: /afs/inf.ed.ac.uk/user/s17/s1785140/merlin/egs/build_your_own_voice/s1/database/labels/label_state_align/ 1")
    print("################################")
    raise Exception

PROMPT_LAB_FOLDER = sys.argv[1]

'''
all added questions for reference

QS "Speaker_ID==1"    {/K:1=}
QS "Speaker_ID==2"    {/K:2=}
QS "Speaker_ID==3"    {/K:3=}
QS "Speaker_ID==4"    {/K:4=}
QS "Speaker_ID==5"    {/K:5=}
QS "Speaker_ID==6"    {/K:6=}
QS "Speaker_ID==7"    {/K:7=}
QS "Speaker_ID==8"    {/K:8=}
QS "Speaker_ID==9"    {/K:9=}
QS "Speaker_ID==10"    {/K:10=}
QS "Speaker_ID==11"    {/K:11=}
QS "Speaker_ID==12"    {/K:12=}
QS "Speaker_ID==13"    {/K:13=}
QS "Speaker_ID==14"    {/K:14=}
QS "Speaker_ID==15"    {/K:15=}
QS "Speaker_ID==16"    {/K:16=}
QS "Speaker_ID==17"    {/K:17=}
QS "Speaker_ID==18"    {/K:18=}
QS "Speaker_ID==19"    {/K:19=}
QS "Speaker_ID==20"    {/K:20=}
CQS "arousal"    {/LXXX:([\d\.-]+)}
CQS "expectancy"    {/MXXX:([\d\.-]+)}
CQS "power"    {/NXXX:([\d\.-]+)}
CQS "valence"    {/OXXX:([\d\.-]+)}
CQS "Utterance_ID"    {/UTTID:(\d+)}
QS "Speaker_ID==Leslie"    {/K:21=}
QS "Female"    {/GIRL}
QS "Male"    {/MALE}
QS "AVEC2012"    {/AVEC}
QS "Blizzard2017"    {/BLIZ2017}
'''

#get list of all label files
label_files = sorted(os.listdir(PROMPT_LAB_FOLDER))

'''speaker id'''
#get desired speaker ID to generate at test time from command line argument
#first way of generating average speaker (don't trigger any speaker id question)
# s_id_label = '/K:0='
#second way of generating average speaker (trigger only female speaker ids)
# s_id_label = '/K:1=' + '/K:3=' + '/K:5=' + '/K:7=' + '/K:9=' + '/K:10=' + '/K:11=' + '/K:12=' + '/K:13=' + '/K:15=' + '/K:17=' + '/K:19=' + '/K:20='

s_id_label = '/K:21='

'''gender'''
sex_id = '/GIRL'
# sex_id = '/MALE'

'''dataset'''
# dataset_id = '/AVEC'
dataset_id = '/BLIZ2017'

'''utt_id''' #selects the row of the projection matrix to use as input
utt_num = 0
utt_id = '/UTTID:' + str(utt_num)

#iterate over each one
for lf in label_files:
    to_add = s_id_label + sex_id + dataset_id + utt_id

    #read in their data into list of lines
    with open(os.path.join(PROMPT_LAB_FOLDER, lf)) as f:
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
    with open(os.path.join(PROMPT_LAB_FOLDER, lf), 'w') as f:
        f.write(''.join(output))
