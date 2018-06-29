'''
takes in AVEC2012 continuous time emotion labels
extracts out the labels for each sentence
and stores them in files
'''

import os
import re
import sys
from helpers import process_transcript, resample

if len(sys.argv) != 3:
    print("################################")
    print("AVEC2012_clean_for_merlin usage:")
    print("python create_emotion_label_files.py <AVEC2012 main folder> <output folder>")
    print("################################")
    raise Exception

#define constants
# LABEL_DIR = '/group/project/disnv/AVEC2012/emotion labels/{}/FC_{}_labels/' #directory where emotion labels reside
# TRANSCRIPT_DIR = '/group/project/disnv/AVEC2012/transcripts/original/{}/'
# OUT_DIR = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/sentence_continuous_emotion_labels/'#directory where emotion labels for each sentence will be saved
AVEC2012_DIR = sys.argv[1]
LABEL_DIR = AVEC2012_DIR + '/emotion labels/{}/FC_{}_labels/' #directory where emotion labels reside
TRANSCRIPT_DIR = AVEC2012_DIR + '/transcripts/original/{}/'
OUT_DIR = sys.argv[2]
IN_FRAMERATE = 49.979 #framerate of AVEC2012 emotion labels
OUT_FRAMERATE = 200 #merlin is 1 frame every 5ms

INNER_FOLDERS = ['train', 'devel', 'test']

# EXCLUDE_LIST = [
#     "tests_audio011" #the transcript sent timestamps refer to times past the length of the actual file
# ]

for inner_folder in INNER_FOLDERS:
    #get list of all transcript files
    transcript_files = os.listdir(TRANSCRIPT_DIR.format(inner_folder))

    #get list of all label files
    label_files = os.listdir(LABEL_DIR.format(inner_folder, inner_folder))

    #sanity check on number of label files
    assert len(label_files) % 4 == 0, 'number of label files is incorrect'

    #for each dialog (or for each transcript file)
    for tf in transcript_files:
        #progress checker
        print('Processing emotion labels for', tf)

        #grep the dialog number from the filename
        dialog_num = re.findall('(\d+).txt', tf)[0]

        #get the matching label files from label_files
        dialog_labs = [lf for lf in label_files if dialog_num in lf] #dialog should be len 4 for each dimension in emotion

        #get the sentence timestamps
        _, sent_timestamps, _ = process_transcript(TRANSCRIPT_DIR.format(inner_folder) + tf)

        ignore_rest_of_sents = False

        for i, sent_timestamp in enumerate(sent_timestamps, start=1): #i is the sentence number

            if ignore_rest_of_sents:
                break

            #get start and end label
            start_time, end_time = sent_timestamp

            #the start frame of a sentence in the label file is equal to...
            #start_time_in_secs * framerate_of_emotion_labels = start_frame_number
            start_frame = int(start_time * IN_FRAMERATE)
            end_frame = int(end_time * IN_FRAMERATE)

            #get from line start_frame to line end_frame from the label files for each emotion
            for dl in dialog_labs:
                #grep out the emotion dimension
                emot_dim = re.findall('([a-z]+).dat', dl)[0]

                #read the data in the label file
                with open(LABEL_DIR.format(inner_folder, inner_folder) + dl) as f:
                    data = f.readlines() #each line in data is an emotion magnitude for a single video frame at 49fps

                #get the correct lines from the file
                sent_data = [float(line) for line in data[start_frame:end_frame+1]]

                if len(sent_data) == 0: #then the wav file is too short
                    ignore_rest_of_sents = True
                    break

                #NB NB NB !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                #instead of using in and out framerates that could be quite error prone,
                #just get the exact number of frames from the wav file upscale emot labels to that
                #OR!
                #just tweak the OUT_FRAMERATE until it works...

                #train_audio002_sent10 has 644 frames according to merlin (TODO where can we directly get this number from?)
                #emots has 652 after being processed by resample according to in and out frame rates
                #srikanth said num of frames should be within 5 to 644

                #if we use sox to get sampling rate and number of samples, then we can get a more accurate figure but still not same
                #number of samples * sampling rate * desired_frame_rate
                # 155610 * (1/48000) * 200
                # Out[2]: 648.375
                #NB NB NB !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                #upsample
                sent_data = resample(sent_data, IN_FRAMERATE, OUT_FRAMERATE) #returns numpy.ndarray
                # except:
                #     raise ValueError(tf, sent_timestamps, len(data), i, start_time, end_time, 'start frame', start_frame, end_frame, sent_data)

                sent_data = list(str(float(num)) for num in sent_data)

                #create filename
                #format tests_audio002_sent1_16bit.lab
                if inner_folder == 'test':
                    renamed_inner_folder = 'tests' #as folder is called 'test' but files have name 'tests'
                else:
                    renamed_inner_folder = inner_folder

                file_name = renamed_inner_folder + '_audio' + dialog_num + '_sent' + str(i) + '_16bit.' + emot_dim
                full_path_to_file = OUT_DIR + emot_dim + '/' + file_name

                os.makedirs(os.path.dirname(full_path_to_file), exist_ok=True)
                with open(full_path_to_file, "w") as f:
                    f.write('\n'.join(sent_data))
