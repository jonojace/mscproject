'''
takes in AVEC2012 continuous time emotion labels
extracts out the labels for each sentence
and stores them in files
'''

import os
import re
import sys
from helpers import process_transcript, resample
import matplotlib.pyplot as plt

#define constants
# LABEL_DIR = '/group/project/disnv/AVEC2012/emotion labels/{}/FC_{}_labels/' #directory where emotion labels reside
# TRANSCRIPT_DIR = '/group/project/disnv/AVEC2012/transcripts/original/{}/'
# OUT_DIR = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/sentence_continuous_emotion_labels/'#directory where emotion labels for each sentence will be saved
AVEC2012_DIR = '/group/project/disnv/AVEC2012'
LABEL_DIR = AVEC2012_DIR + '/emotion labels/{}/FC_{}_labels/' #directory where emotion labels reside
TRANSCRIPT_DIR = AVEC2012_DIR + '/transcripts/original/{}/'
OUT_DIR = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/plots_and_figures/emotion_arcs' #where all the plots go
IN_FRAMERATE = 49.979 #framerate of AVEC2012 emotion labels
OUT_FRAMERATE = 200 #merlin is 1 frame every 5ms

# INNER_FOLDERS = ['train', 'devel', 'test']
INNER_FOLDERS = ['train']


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

            plot_data = {}

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

                #create filename
                #format tests_audio002_sent1_16bit.lab
                if inner_folder == 'test':
                    renamed_inner_folder = 'tests' #as folder is called 'test' but files have name 'tests'
                else:
                    renamed_inner_folder = inner_folder

                plot_data[emot_dim] = sent_data #add data to dict for plotting

            #make the plot
            def plot_arc(emotion, subplot):
                #make histograms for each emotion in 4 subplots
                subplot.plot(plot_data[emotion])
                # print(min(data[emotion]), max(data[emotion]))
                # round_to_n = lambda x, n: round(x, -int(floor(log10(abs(x)))) + (n - 1))
                # subplot.set_xticks([round_to_n(x,2) for x in np.arange(min(data[emotion]),max(data[emotion]), (max(data[emotion])-min(data[emotion]))/5 )])
                # std = np.std(data[emotion])
                # mean = np.mean(data[emotion])
                # upper = mean + 2*std
                # lower = mean - 2*std
                # print(emotion, 'lower bound is', lower, 'upper is', upper)
                # subplot.axvline(mean, color='k', linestyle='dashed', linewidth=1) #plot the mean as a line
                # subplot.axvspan(lower, upper, alpha=0.25, color='grey')
                subplot.set_title(emotion.title())

            f, axarr = plt.subplots(2, 2)
            plot_arc('arousal', axarr[0,0])
            plot_arc('expectancy', axarr[0,1])
            plot_arc('power', axarr[1,0])
            plot_arc('valence', axarr[1,1])

            #make filename for the plot figure to save to disk
            file_name = renamed_inner_folder + '_audio' + dialog_num + '_sent' + str(i) + '_16bit.eps'
            plt.tight_layout()
            plt.savefig(OUT_DIR + '/' + file_name, format='eps')
            plt.close()
