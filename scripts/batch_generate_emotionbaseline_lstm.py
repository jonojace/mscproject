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
experiment_output_dir = "/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/emotionbaseline/s1/experiments/emotionbaseline_alldata_lstm/test_synthesis/wav/"

#where you want to put files
listening_test_output_dir = "/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/listening_test_files/emotionbaseline_lstm/"

speaker_id = 0

arousal_mean = -0.083341168
expectancy_mean = 34.1405567
power_mean = 0.375480657
valence_mean = 0.06304983773

arousal_var = 2
valence_var = 2

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

                    #run the synthesis
                    # cmd = subprocess.Popen(["./run_dice.sh synth " + str(a) + ' ' + str(e) + ' ' + str(p) + ' ' + str(v)], shell=True, stdout=subprocess.PIPE).wait()
                    print(subprocess.check_output("./run_dice.sh synth " + str(speaker_id) + ' ' + str(a) + ' ' + str(e) + ' ' + str(p) + ' ' + str(v), shell=True))
                    #print out output in real time
                    # for i in cmd.stdout.readline():
                    #     print(i)
                    #     sys.stdout.flush()

                    #copy the generated files into
                    subprocess.Popen(["cp " + experiment_output_dir + '*.wav ' + out_dir], shell=True).wait()
