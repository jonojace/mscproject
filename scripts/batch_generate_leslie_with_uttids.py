import os
import subprocess
import sys

def ensure_dir(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)

#path to the sentence embedding file that controls the generation
sent_embedding_file = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/sent_embedding_to_generate/sent_embedding'

#the file from where we will get the trained sentence embeddings from
projection_weights_file = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/projection_weights_backup/tokenprojection_alldata/projection_weights_acoustic_model/projection_weights/proj_INFERENCE_epoch_25'

#load the projection weights file in
with open(projection_weights_file) as f:
    projection_weights = f.readlines()

#where files are output to by the synth
experiment_output_dir = "/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/leslie/s1/experiments/leslie_alldata/test_synthesis/wav/"

#where you want to put files
listening_test_output_dir = "/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/listening_test_files/leslie_uttids/"


#all the utt_ids we want to generate

# #HALF
# utt_ids = [
#     6747,
#     7176,
#     3362,
#     8256,
#     4987,
#     6678,
#     7661,
#     8679,
#     796,
#     9320,
#     7192,
#     6794,
#     7739,
#     2921,
#     2588,
#     5780
# ]

#FULL
utt_ids = [
    6747,
    7176,
    3363,
    4476,
    3362,
    8256,
    6309,
    2167,
    4987,
    6678,
    3476,
    8060,
    7661,
    8679,
    9371,
    6685,
    796,
    9320,
    1178,
    6243,
    7192,
    6794,
    1621,
    4488,
    7739,
    2921,
    1981,
    6993,
    2588,
    5780,
    8751,
    2622
]

#best amp factors are 6 and 8
amp_factors = [6, 8]

for amp_factor in amp_factors:
    for utt_id in utt_ids:
        #get the sentence embedding for this utt_id from the projection weights file
        sentence_embedding = projection_weights[utt_id] #get the corresponding row of weights
        sentence_embedding = ['{:.15f}'.format(amp_factor * float(string)) for string in sentence_embedding.split()] #convert from one string to list of floats
        sentence_embedding = ' '.join(sentence_embedding)
        assert 'e' not in sentence_embedding #check for scientific notation

        #make directory name
        out_dir = listening_test_output_dir + 'amp_factor=' + str(amp_factor) + '/' + str(utt_id) + '/'

        #if this directory exists then we have already generated! so skip
        if not os.path.exists(out_dir):
            #make dir
            ensure_dir(out_dir)

            # overwrite what is in the sent embedding file
            with open(sent_embedding_file, 'w') as f:
                f.write(sentence_embedding)

            #run command
            print(subprocess.check_output("./run_dice_leslie.sh synth", shell=True))

            #copy the generated files into
            subprocess.Popen(["cp " + experiment_output_dir + '*.wav ' + out_dir], shell=True).wait()
        else:
            print(out_dir, 'exists, skipping...')
