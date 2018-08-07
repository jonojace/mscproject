import os
import subprocess
import sys

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    print(file_path, directory)
    if not os.path.exists(directory):
        os.makedirs(directory)

#runs run_dice.sh for desired emotion values and moves output to folder

#where files are output to by the synth
experiment_output_dir = "/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/leslie/s1/experiments/leslie_alldata/test_synthesis/wav/"

#where you want to put files
listening_test_output_dir = "/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/listening_test_files/leslie_emotionids/"

#the desired emot embedding to use to generate, we overwrite this file with new emotion values
emot_embedding_file = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/emot_embedding_to_generate/emot_embedding'

amp_factor = 1

arousal_mean = -0.083341168
expectancy_mean = 34.1405567
power_mean = 0.375480657
valence_mean = 0.06304983773

arousal_var = 30
valence_var = 30

# arousals = [arousal_mean]
arousals = [arousal_mean - arousal_var, arousal_mean, arousal_mean + arousal_var]
expectancys = [expectancy_mean]
powers = [power_mean]
# valences = [valence_mean]
valences = [valence_mean - valence_var, valence_mean, valence_mean + valence_var]



for a in arousals:
    for e in expectancys:
        for p in powers:
            for v in valences:
                #check for scientific notation
                assert 'e' not in str(a) and 'e' not in str(e) and 'e' not in str(p) and 'e' not in str(v)

                #make directory name
                out_dir = listening_test_output_dir + str(a) + '_' + str(e) + '_' + str(p) + '_' + str(v) + '/'

                #if this directory exists then we have already generated! so skip
                if not os.path.exists(out_dir):
                    #make dir
                    ensure_dir(out_dir)

                    #overwrite what is in the emot embedding file
                    with open(emot_embedding_file, 'w') as f:
                        f.write(' '.join([str(a), str(e), str(p), str(v)]))

                    #run command
                    print(subprocess.check_output("./run_dice_leslie_transform.sh synth " + str(amp_factor), shell=True))

                    #copy the generated files into
                    subprocess.Popen(["cp " + experiment_output_dir + '*.wav ' + out_dir], shell=True).wait()
                else:
                    print(out_dir, 'exists, skipping...')
