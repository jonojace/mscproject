import os
import re
import sys

'''
Appends speaker IDs to HTS formatted labels
Also adds appropriate questions to the questions file
'''

if len(sys.argv) != 2:
    print("################################")
    print("appendSpeakerIDToLabels usage:")
    print("python appendSpeakerIDToLabels.py <build your own voice folder>")
    print("EG: /afs/inf.ed.ac.uk/user/s17/s1785140/merlin/egs/build_your_own_voice")
    print("################################")
    raise Exception

LABEL_FOLDER = sys.argv[1] + '/s1/database/labels/label_state_align/'

#NB REMEMBER TO RSYNC OVER THE QUESTIONS FILE FROM DICE MACHINE TO MLP OR EDDIE CLUSTER

#given an audio file number, returns a specific speaker id
def get_speaker_id(dataset, audio_file_num):
    if dataset == 'train':
        if audio_file_num in range(2,8):
            return 1
        elif audio_file_num in range(8,12):
            return 2
        elif audio_file_num in range(12,16):
            return 3
        elif audio_file_num in range(16,20):
            return 4
        elif audio_file_num in range(20,24):
            return 5
        elif audio_file_num in range(28,32):
            return 6
        else:
            raise LookupError('Tried to use an audio file which is not associated with a speaker ID. Please check that you are using the correct audio files.')
    elif dataset == 'devel':
        if audio_file_num in range(1,5):
            return 1
        elif audio_file_num in range(5,9):
            return 2
        elif audio_file_num in range(9,13):
            return 7
        elif audio_file_num in range(13,17):
            return 8
        elif audio_file_num in range(17,21):
            return 9
        elif audio_file_num in range(21,25):
            return 10
        elif audio_file_num in range(25,29):
            return 11
        elif audio_file_num in range(29,31):
            return 12
        else:
            raise LookupError('Tried to use an audio file which is not associated with a speaker ID. Please check that you are using the correct audio files.')
    elif dataset == 'tests':
        if audio_file_num in range(1,5):
            return 1
        elif audio_file_num in range(5,8):
            return 2
        elif audio_file_num in range(8,12):
            return 7
        elif audio_file_num in range(12,16):
            return 8
        elif audio_file_num in range(16,20):
            return 9
        elif audio_file_num in range(20,25):
            return 10
        elif audio_file_num in range(25,29):
            return 11
        elif audio_file_num in range(29,33):
            return 12
        else:
            raise LookupError('Tried to use an audio file which is not associated with a speaker ID. Please check that you are using the correct audio files.')
    else:
        raise ValueError('"Dataset" is not train, devel or tests.')


#get list of all label files
label_files = sorted(os.listdir(LABEL_FOLDER))

#iterate over each one
for lf in label_files:
    #identify speaker ID from this file
    dataset = re.findall('(\w+)_audio', lf)[0]
    audio_file_num = int(re.findall('audio(\d+)', lf)[0])
    s_id = get_speaker_id(dataset, audio_file_num)
    s_id_label = '/K:' + str(s_id)

    #read in their data into list of lines
    with open(LABEL_FOLDER + lf) as f:
        data = f.readlines()

    #instantiate list to hold output to write to file
    output = []

    #for each line in the data, append speaker ID to end of line just before state indicator
    for line in data:
        state_indicator_idx = line.index('[')
        output.append(line[:state_indicator_idx] + s_id_label + line[state_indicator_idx:])

    #overwrite the file with the new lines in the label file that now include a speaker id
    with open(LABEL_FOLDER + lf, 'w') as f:
        f.write(''.join(output))
