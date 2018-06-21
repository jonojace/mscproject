#!/bin/bash -e

#perform full process of training a merlin model using AVEC2012 data
#with speaker and emotion labels
#and then synthesise test utterances

echo "---INSIDE traindnn.sh"

if test "$#" -ne 2; then
    echo "################################"
    echo "Usage: "
    echo "./train.sh <path/to/build_your_own_voice> <voice name>"
    echo "################################"
    exit 1
fi

EXAMPLE_DIR=$1 #path to the build_your_own_voice where we will be running files
VOICE_NAME=$2

#cd into the correct directory for running the merlin step by step scripts
cd ${EXAMPLE_DIR}/s1

# step 5: train duration model
./05_train_duration_model.sh conf/duration_${VOICE_NAME}.conf

# step 6: train acoustic model
./06_train_acoustic_model.sh conf/acoustic_${VOICE_NAME}.conf

# #copy text files to generate into appropriate folder
# cp -r ${TEXT_TO_GENERATE_FOLDER}/. experiments/${VOICE_NAME}/test_synthesis/txt/

# # step 7: run text to speech
# basename --suffix=.txt -- experiments/${VOICE_NAME}/test_synthesis/txt/* > experiments/${VOICE_NAME}/test_synthesis/test_id_list.scp
# ./07_run_merlin.sh experiments/${VOICE_NAME}/test_synthesis/txt conf/test_dur_synth_${VOICE_NAME}.conf conf/test_synth_${VOICE_NAME}.conf
#
# #open the folder with output wav files
# nautilus ${EXAMPLE_DIR}/s1/experiments/avec2012/test_synthesis/wav
