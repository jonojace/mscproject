import subprocess
import datetime
import os
import sys
from helpers import process_transcript

#WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#need to do source activate msc! or it won't find ffmpeg
#WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#get input and output folders from command line arguments
if len(sys.argv) != 4:
    print("################################")
    print("AVEC2012_clean_for_merlin usage:")
    print("python AVEC2012_clean_for_merlin.py <input folder> <output folder> <min wav file size>")
    print("################################")
    raise Exception

INPUT_FOLDER = sys.argv[1] #path to AVEC2012 raw data folder
OUTPUT_FOLDER = sys.argv[2] #path to folder where processed audio and text files will be placed
MIN_WAV_FILE_SIZE = int(sys.argv[3])

#check for existance of group folder, if not then we are in eddie
# if os.path.exists('/group/project/disnv/AVEC2012/'):
#     INPUT_FOLDER = '/group/project/disnv/AVEC2012/'
#     OUTPUT_FOLDER = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/AVEC2012_clean_for_merlin/'
# else:
#     INPUT_FOLDER = '/exports/eddie/scratch/s1785140/AVEC2012/'
#     OUTPUT_FOLDER = '/exports/eddie/scratch/s1785140/AVEC2012_clean_for_merlin'

#these are relative paths and should be portable
TRANSCRIPT_FOLDER = 'transcripts/original/'
WAV_FOLDER = 'recordings/dialogues/'

inner_folders = ['train/'] # folders to explore inside INPUT_FOLDER

# inner_folders = [
#     'train/',
#     'devel/', #NB WARNING You need to exclude broken dialogues for devel and test in the same way you did for train
#     'test/'
# ]

#optionally control how much data you want to convert, rather than converting all of the data in the folder
INCLUDE_LIST = None #takes all the data from the folder

#NB MAYBE NOT GOOD FOR TESTING AS FALLS DOWN WHEN TRAINING HMM MODELS???
# e.g. Force-alignment unsucessful!! Please check /home/s1785140/merlin/misc/scripts/alignment/state_align/forced_alignment.py
# INCLUDE_LIST = [ #one dialog from first speaker (faster for testing)
# 'train_transcript001.txt'
# ]

# INCLUDE_LIST = [ #one dialog per speaker
# 'train_transcript002.txt',
# 'train_transcript008.txt',
# 'train_transcript012.txt',
# 'train_transcript016.txt',
# 'train_transcript020.txt',
# 'train_transcript028.txt'
# ]

# INCLUDE_LIST = [ #all dialogs per speaker
# 'train_transcript002.txt',
# 'train_transcript003.txt',
# 'train_transcript004.txt',
# 'train_transcript005.txt',
# 'train_transcript006.txt',
# 'train_transcript007.txt',
# 'train_transcript008.txt',
# 'train_transcript009.txt',
# 'train_transcript010.txt',
# 'train_transcript011.txt',
# 'train_transcript012.txt',
# 'train_transcript013.txt',
# 'train_transcript014.txt',
# 'train_transcript015.txt',
# 'train_transcript016.txt',
# 'train_transcript017.txt',
# 'train_transcript018.txt',
# 'train_transcript019.txt',
# 'train_transcript020.txt',
# 'train_transcript021.txt',
# 'train_transcript022.txt',
# 'train_transcript023.txt',
# 'train_transcript028.txt',
# 'train_transcript029.txt',
# 'train_transcript030.txt',
# 'train_transcript031.txt'
# ]

EXCLUDE_LIST = None

EXCLUDE_LIST = [
    'train_transcript001.txt',
    'train_transcript024.txt',
    'train_transcript025.txt',
    'train_transcript026.txt',
    'train_transcript027.txt',
    'devel_transcript031.txt',
    'devel_transcript032.txt'
]

SENT_EXCLUDE_LIST = [
    'devel_audio023_sent062',
    'tests_audio011_sent017',
    'tests_audio011_sent018',
    'tests_audio011_sent019',
    'tests_audio011_sent020',
    'tests_audio011_sent021',
    'tests_audio011_sent022',
    'tests_audio011_sent023',
    'tests_audio011_sent024',
    'tests_audio011_sent025',
    'tests_audio011_sent026',
    'tests_audio011_sent027',
    'tests_audio011_sent028',
    'tests_audio011_sent029',
    'tests_audio011_sent030',
    'tests_audio011_sent031',
    'tests_audio011_sent032',
    'tests_audio011_sent033'
]

#NB using wait() ensures that the rest of the python code waits for the commands
#to finish executing and doesn't simply just start the subprocesses in the background
#clear out output folder
command = "rm -R " + OUTPUT_FOLDER + "txt"
subprocess.Popen(command, shell=True).wait()
command = "rm -R " + OUTPUT_FOLDER + "wav"
subprocess.Popen(command, shell=True).wait()
command = "mkdir " + OUTPUT_FOLDER + "txt"
subprocess.Popen(command, shell=True).wait()
command = "mkdir " + OUTPUT_FOLDER + "wav"
subprocess.Popen(command, shell=True).wait()

for inner_folder in inner_folders:
    #get list of all transcript and wav files
    transcript_files = sorted(os.listdir(INPUT_FOLDER + TRANSCRIPT_FOLDER + inner_folder))
    wav_files = sorted(os.listdir(INPUT_FOLDER + WAV_FOLDER + inner_folder))
    # all_file_names = [] #was used to keep track of all the filenames for storing in file_id_list.scp file

    # print(transcript_files, wav_files)

    #work through each dialog one at a time
    for transcript_file, wav_file in zip(transcript_files, wav_files):

        if INCLUDE_LIST:
            if transcript_file not in INCLUDE_LIST:
                print(transcript_file, "NOT IN INCLUDE LIST")
                continue #will skip over any files which aren't in the include list
        if EXCLUDE_LIST:
            if transcript_file in EXCLUDE_LIST:
                print(transcript_file, "IN EXCLUDE LIST")
                continue

        #read in transcript file and get sentences, sent and word time stamps
        output_sentences, sent_timestamps, word_timestamps = process_transcript(INPUT_FOLDER + TRANSCRIPT_FOLDER + inner_folder + transcript_file)

        #use sentence timestamps to segment the dialog wav files into wav files only containing sentences
        #also create txt files that contain transcriptions for each sentence
        i = 1
        for sentence, timestamps in zip(output_sentences, sent_timestamps):
            begin = str(datetime.timedelta(seconds=timestamps[0]))
            end = str(datetime.timedelta(seconds=timestamps[1]))

            file_name = wav_file[:-4] #get rid of .wav extension
            file_name = file_name + '_sent{}'.format(str(i).zfill(3))

            #if a filename is in the exclude sent list, then continue this for loop
            if file_name in SENT_EXCLUDE_LIST:
                print(file_name, 'in SENT_EXCLUDE_LIST')
            else:
                #NOTE PCM signed 16-bit little-endian is required by HTK's HCOPY,
                #ffmpeg by default outputs 24bit...
                command = "ffmpeg -i {} -ss {} -to {} -c copy {} > /dev/null 2>&1 < /dev/null".format(INPUT_FOLDER + WAV_FOLDER + inner_folder + wav_file, begin, end, OUTPUT_FOLDER + 'wav/' + file_name + '.wav')
                subprocess.Popen(command, shell=True).wait()
                if os.path.getsize(OUTPUT_FOLDER + 'wav/' + file_name + '.wav') < MIN_WAV_FILE_SIZE:
                    print(file_name + '.wav', 'too small! Less than', MIN_WAV_FILE_SIZE ,' bytes. Skipping this file...')
                    os.remove(OUTPUT_FOLDER + 'wav/' + file_name + '.wav')
                    #delete wav file
                else:
                    with open(OUTPUT_FOLDER + 'txt/' + file_name + '.txt', 'w') as f:
                        f.write(' '.join(sentence))

            i = i + 1

# with open(OUTPUT_FOLDER + 'file_id_list.scp', 'w') as f:
#     f.write('\n'.join(all_file_names))



    #ffmpeg -i train_audio002.wav -ss 00:00:11.050 -to 00:00:14.210 -c copy firstturn.wav
