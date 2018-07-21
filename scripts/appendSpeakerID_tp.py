import os
import re
import sys
from helpers import process_transcript
import math
import numpy as np

'''
Appends speaker+emotion IDs to HTS formatted label
Doesn't append emotion IDs to lab files for leslie simms data

If you want to ignore the emotion ids just don't add those questions to the questions file
'''

#check for correct number of args
if len(sys.argv) != 3:
    print("################################")
    print("appendSpeakerIDToLabels usage:")
    print("python appendSpeakerIDToLabels.py <build your own voice folder> <AVEC2012 main folder>")
    print("EG: /afs/inf.ed.ac.uk/user/s17/s1785140/merlin/egs/build_your_own_voice")
    print("################################")
    raise Exception

#create path to folder of state aligned labels created by HMM alignment
LABEL_FOLDER = sys.argv[1] + '/s1/database/labels/label_state_align/'
AVEC2012_DIR = sys.argv[2]
LABEL_DIR = AVEC2012_DIR + '/emotion labels/{}/FC_{}_labels/' #directory where emotion labels reside
TRANSCRIPT_DIR = AVEC2012_DIR + '/transcripts/original/{}/'
TIME_DIVISOR = 10000000 #divide the timestamp in HTS label files by this to get to seconds
VIDEO_FRAMERATE = 49.979 #merlin is 1 frame every 5ms

# SENT_AVG_OUTPUT_FOLDER = '/afs/inf.ed.ac.uk/user/s17/s1785140/analysis_mscproject/sent_emotion_avg'

#NB REMEMBER TO RSYNC OVER THE QUESTIONS FILE FROM DICE MACHINE TO MLP OR EDDIE CLUSTER

#given an audio file number, returns a specific speaker id
def get_speaker_id_and_sex(dataset, audio_file_num):
    if dataset == 'train':
        if audio_file_num in range(2,8):
            return 1, 'girl'
        elif audio_file_num in range(8,12):
            return 2, 'guy'
        elif audio_file_num in range(12,16):
            return 3, 'girl'
        elif audio_file_num in range(16,20):
            return 4, 'guy'
        elif audio_file_num in range(20,24):
            return 5, 'girl'
        elif audio_file_num in range(28,32):
            return 6, 'guy'
        else:
            raise LookupError('Tried to use an audio file which is not associated with a speaker ID. Please check that you are using the correct audio files.')
    elif dataset == 'devel':
        if audio_file_num in range(1,5):
            return 1, 'guy'
        elif audio_file_num in range(5,9):
            return 2, 'guy'
        elif audio_file_num in range(9,13):
            return 7, 'girl'
        elif audio_file_num in range(13,17):
            return 8, 'guy'
        elif audio_file_num in range(17,21):
            return 9, 'girl'
        elif audio_file_num in range(21,25):
            return 10, 'girl'
        elif audio_file_num in range(25,29):
            return 11, 'girl'
        elif audio_file_num in range(29,31):
            return 12, 'girl'
        else:
            raise LookupError('Tried to use an audio file which is not associated with a speaker ID. Please check that you are using the correct audio files.')
    elif dataset == 'tests':
        if audio_file_num in range(1,5):
            return 13, 'girl'
        elif audio_file_num in range(5,8):
            return 14, 'guy'
        elif audio_file_num in range(8,12):
            return 15, 'girl'
        elif audio_file_num in range(12,16):
            return 16, 'guy'
        elif audio_file_num in range(16,20):
            return 17, 'girl'
        elif audio_file_num in range(20,25):
            return 18, 'guy'
        elif audio_file_num in range(25,29):
            return 19, 'girl'
        elif audio_file_num in range(29,33):
            return 20, 'girl'
        else:
            raise LookupError('Tried to use an audio file which is not associated with a speaker ID. Please check that you are using the correct audio files.')
    else:
        raise ValueError('"Dataset" is not train, devel or tests.')

#get list of all label files in the label_state_align folder
label_files = sorted(os.listdir(LABEL_FOLDER))

memo = {} #prevent recomputation of sentence timestamps

#iterate over each label file
for lf in label_files:
    #identify speaker ID from the filename
    matches = re.findall('(\w+)_audio', lf)
    if matches:
        dataset = matches[0]
        audio_file_num = int(re.findall('audio(\d+)', lf)[0])
        sent_num = int(re.findall('sent(\d+)', lf)[0])
        s_id, sex = get_speaker_id_and_sex(dataset, audio_file_num)
        leslie = False
    else: #leslie simms data
        s_id = 21
        sex = 'girl'
        leslie = True

    #create HTS style answer for speaker ID question
    s_id_label = '/K:' + str(s_id) + '=' #note that = is so that we don't match /K:1 when we hav /K:10 or /K:11 etc
    if sex == 'girl':
        sex_id = '/GIRL'
    else:
        sex_id = '/MALE'
    if leslie:
        dataset_id = '/BLIZ2017'
    else:
        dataset_id = '/AVEC'

    #get the emotion data
    if not leslie:
        #make transcript file name
        tf = dataset + '_transcript' + str(audio_file_num).zfill(3) + '.txt'
        # print(lf)

        #correct inconsistent naming
        if dataset == 'tests':
            inner_folder = 'test'
        else:
            inner_folder = dataset

        #get sent timestamps (use memoisation to save too much disk access)
        if TRANSCRIPT_DIR.format(inner_folder) + tf in memo:
            sent_timestamps = memo[TRANSCRIPT_DIR.format(inner_folder) + tf]
        else:
            _, sent_timestamps, _ = process_transcript(TRANSCRIPT_DIR.format(inner_folder) + tf)
            memo[TRANSCRIPT_DIR.format(inner_folder) + tf] = sent_timestamps

        #get start timestamp for this utterance (in seconds)
        #note we probs won't need end_time
        #(but can use it to sanity check that we have the correct file if u want...)
        utt_start, _ = sent_timestamps[sent_num-1]
        # print(sent_num-1, sent_timestamps, utt_start, '\n')

        #use dict to keep the data for this dialog file for each emotion
        #key='arousal' value=[0.3004, 0.3005, 0.3006, ...]
        emotion_data = {}

        #load emotion data in for this dialog
        for emotion in ['arousal', 'expectancy', 'power', 'valence']:
            #get the continuous emotion feature file paths
            emotion_filepath = LABEL_DIR.format(inner_folder, inner_folder) + 'labels_continuous_{}{}_{}.dat'.format(inner_folder, str(audio_file_num).zfill(3), emotion)
            #open the file
            with open(emotion_filepath) as f:
                data = f.readlines()
            emotion_data[emotion] = data

    #get label files
    with open(LABEL_FOLDER + lf) as f:
        label_data = f.readlines()

    modified_output = [] #holds the modified lines inc. emotion/speajer id which will be used to overwrite the label file

    #each line is a state-time alignment
    for line_idx, line in enumerate(label_data):
        to_add_to_lab_line = s_id_label + sex_id + dataset_id #we add the emotion labels onto the end of this

        if not leslie:
            #get the start and end value for the state
            state_start, state_end = re.findall('^(\d+) (\d+)', line)[0]

            # print('XXX',state_start, state_end)

            #get the start time of this state relative to dialog file times not utt times (will be in seconds)
            state_start = utt_start + int(state_start) / TIME_DIVISOR
            state_end = utt_start + int(state_end) / TIME_DIVISOR
            # print(lf, state_start, state_end)

            # print('YYY',state_start, state_end)

            # print('ZZZ', VIDEO_FRAMERATE * state_start, VIDEO_FRAMERATE * state_end)

            #convert from seconds to video framerate
            #use floor and ceiling as we want to get at least one frame
            state_start = math.floor(VIDEO_FRAMERATE * state_start)
            state_end = math.ceil(VIDEO_FRAMERATE * state_end)

            #NB this is for getting average emotion value over the entire sentence
            if line_idx == 0:
                sent_start = state_start
            if line_idx == len(label_data)-1:
                sent_end = state_end

            #get the lines from the emotion files corresponding to these time stamps
            for emotion, data in emotion_data.items():
                # print('XXX', emotion.keys())
                #get the continuous emotion arcs corresponding to start and end timestamps
                state_values = [float(val) for val in data[state_start:state_end]] #TODO state_start and end_start aren't inside the data

                #for each emotion, get the average value for the duration of the state
                state_avg = np.mean(state_values)

                # if rv == 0:
                #     print(state_start, state_end, len(data), line, emotion, l, rv, data[:10],'\n')

                #create HTS style answer for each emotion ID
                if emotion == 'arousal': letter = 'L'
                if emotion == 'expectancy': letter = 'M'
                if emotion == 'power': letter = 'N'
                if emotion == 'valence': letter = 'O'

                #use this string formatting rather than just str(state_avg) as that can output
                #scientific notation that might be confusing the merlin regular expressions perhaps.
                to_add_to_lab_line = to_add_to_lab_line + '/' + letter + ':' + '{:.10f}'.format(state_avg)

        #append answers onto the end of each line in the lab file in label_state_align
        #for each line in the data, append speaker ID and emotion ID to end of line just before state indicator
        state_indicator_idx = line.index('[')
        modified_output.append(line[:state_indicator_idx] + to_add_to_lab_line + line[state_indicator_idx:])

    #overwrite the file with the new lines in the label file that now include a speaker id
    with open(LABEL_FOLDER + lf, 'w') as f:
        f.write(''.join(modified_output))

    # #get the sentence-level emotion value for oliver watts model using sent_start and sent_end
    # to_write = ''
    # for emotion, data in emotion_data.items():
    #     sent_values = [float(val) for val in data[sent_start:sent_end]]
    #     sent_avg = np.mean(sent_values)
    #     to_write += emotion + ':' + str(sent_avg) + ' '
    # with open(SENT_AVG_OUTPUT_FOLDER + '/' + lf.rstrip('.lab') + '.avg', 'w') as f:
    #     f.write(to_write)
