'''
File to hold all function helpers to be used in MSc Project
'''

import wave
import contextlib
import numpy as np
from scipy.interpolate import interp1d

#resamples the data from in_framerate to out_framerate
def resample(data, in_framerate, out_framerate):
    in_num_samples = len(data)
    out_num_samples = int(in_num_samples * (out_framerate / in_framerate))

    x = np.arange(0, in_num_samples) # i.e. [0, 1, 2, 3]
    y = data
    f = interp1d(x, y) # returns a function that goes from x values to y values, linearly interpolates

    #new x values that we want to calculate interpolated y values for
    new_x = np.linspace(0, in_num_samples-1, int(out_num_samples)) # i.e. [0, 0.5, 1, 1.5, 2, 2.5, 3]

    resampled_data = f(new_x)
    return resampled_data #return down or upsampled y values

#returns information about a wav file
def analyse_wav(path_to_wav):
    with contextlib.closing(wave.open(path_to_wav,'r')) as f:
        num_frames = f.getnframes()
        framerate = f.getframerate()
        duration = num_frames / float(fram)
        return num_frames, framerate, duration #framerate is sample rate of the file

#gets sentences, sentence timestamps and word timestamps from transcript file
def process_transcript(path_to_transcript):
    def convert_to_seconds(string):
        return float(string)/1000

    #read in transcript txt data as a raw string, not a list
    with open(path_to_transcript) as f:
        data = f.read()

    #split into list based on full stops
    input_sentences = data.split('.')[:-1]
    output_sentences = []
    sent_timestamps = []
    word_timestamps = []

    #get a sentence
    for s in input_sentences:
        #use filter to get rid of empty strings
        #use string slice to get rid of the utterance number
        words = list(filter(lambda x: x != '', s.split('\n')))[1:]
        output_sentence = []
        ignore_sentence = False
        begin_timestamp = 0
        end_timestamp = 0
        timestamps = []

        #ignore empty sentences
        #and when there is only one word in this sentence and its a <laugh>
        if len(words) == 0 or len(words) == 1 and '<' in words[0]:
            ignore_sentence = True
        else:
            for i, w in enumerate(words):
                if '<' not in w: #ignore adding <laugh>'s to the output sentence'
                    output_sentence.append(w.split()[2].lower())
                    timestamps.append((convert_to_seconds(w.split()[0]), convert_to_seconds(w.split()[1]))) #these will be used for emotion labels perhaps
                if i == 0: #but if <laugh> happens at the start of a turn, keep it as beginning of the turn wrt timestamps
                    begin_timestamp = convert_to_seconds(w.split()[0])
                if i == len(words) - 1:
                    end_timestamp = convert_to_seconds(w.split()[1])

        if not ignore_sentence:
            output_sentences.append(output_sentence)
            sent_timestamps.append((begin_timestamp, end_timestamp))
            word_timestamps.append(timestamps)

    return output_sentences, sent_timestamps, word_timestamps
