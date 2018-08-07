#!/bin/bash -e

#perform full process of training a merlin model using AVEC2012 data
#with speaker and emotion labels
#and then synthesise test utterances

echo "---INSIDE synthesise.sh"

if test "$#" -ne 3; then
    echo "################################"
    echo "Usage: "
    echo "./synthesise.sh <path/to/build_your_own_voice> <path/to/mscproject> <voice name>"
    echo ""
    echo "Enter a speaker id, and values for arousal expectancy power and valence that you want to generate"
    echo "################################"
    exit 1
fi

EXAMPLE_DIR=$1 #path to the build_your_own_voice where we will be running files
MSCPROJECT_DIR=$2 #path to mscproject directory that holds various small files
VOICE_NAME=$3

SCRIPT_DIR=${MSCPROJECT_DIR}/scripts
TEXT_TO_GENERATE_FOLDER=${MSCPROJECT_DIR}/text_to_generate #contains txt files to generate
SENT_EMBEDDING_FILE=${MSCPROJECT_DIR}/sent_embedding_to_generate/sent_embedding

#go into correct dir
cd ${EXAMPLE_DIR}/s1

#clean out files from previous generation
rm -f experiments/${VOICE_NAME}/test_synthesis/txt/* #using f switch ignores error if the dir is empty
rm -f experiments/${VOICE_NAME}/test_synthesis/wav/*
rm -rf experiments/${VOICE_NAME}/test_synthesis/prompt-lab/*
rm -f experiments/${VOICE_NAME}/test_synthesis/prompt-utt/*
rm -f experiments/${VOICE_NAME}/test_synthesis/gen-lab/*

PROMPT_LAB_FOLDER=experiments/${VOICE_NAME}/test_synthesis/prompt-lab

#copy over the txt files you wish to generate now
cp -r ${TEXT_TO_GENERATE_FOLDER}/. experiments/${VOICE_NAME}/test_synthesis/txt/

# step 7: run text to speech
#take all the text files in /txt/ and store file names in test_id_list.scp
basename --suffix=.txt -- experiments/${VOICE_NAME}/test_synthesis/txt/* > experiments/${VOICE_NAME}/test_synthesis/test_id_list.scp

##########################################################################
#NB Following commands copied from 07_run_merlin.sh to here to make easier
##########################################################################
global_config_file=conf/global_settings.cfg
source $global_config_file

inp_txt=experiments/${VOICE_NAME}/test_synthesis/txt
test_dur_config_file=conf/test_dur_synth_${VOICE_NAME}.conf
test_synth_config_file=conf/test_synth_${VOICE_NAME}.conf

echo "Step 7:"
echo "synthesizing speech from text..."

echo "preparing full-contextual labels using Festival frontend..."
lab_dir=$(dirname $inp_txt)
./scripts/prepare_labels_from_txt.sh $inp_txt $lab_dir $global_config_file

# echo "appending features to labels..."
python ${SCRIPT_DIR}/appendSentenceEmbeddingToLabels_Test.py ${PROMPT_LAB_FOLDER} ${SENT_EMBEDDING_FILE}

echo "synthesizing durations..."
./scripts/submit.sh ${MerlinDir}/src/run_merlin.py $test_dur_config_file

echo "synthesizing speech..."
./scripts/submit.sh ${MerlinDir}/src/run_merlin.py $test_synth_config_file

echo "deleting intermediate synthesis files..."
./scripts/remove_intermediate_files.sh $global_config_file

echo "synthesized audio files are in: experiments/${Voice}/test_synthesis/wav"
echo "All successfull!! Your demo voice is ready :)"

# #rsync the files from mlp cluster to dice machine
# # rsync -avu ${EXAMPLE_DIR}/s1/experiments/${VOICE_NAME}/test_synthesis/wav /afs/inf.ed.ac.uk/user/s17/s1785140/analysis_mscproject/generated_output

#open the folder with output wav files (only do this when running on dice)
# nautilus ${EXAMPLE_DIR}/s1/experiments/${VOICE_NAME}/test_synthesis/wav






#TODO change scripts so that it looks in a different folder for test time emotion labels
#delete all files in experiments/avec2012/acoustic_model/data/{arousal, expectancy, power, valence}
# for emotion in arousal expectancy power valence; do
#   rm ${EXAMPLE_DIR}/s1/experiments/avec2012/acoustic_model/data/${emotion}/*
# done
#TODO add line so that u can run a script that makes the emotion label files of the correct dimensions
# python ${SCRIPT_DIR}/create_emotion_label_files_test.py ${EXAMPLE_DIR}/s1/experiments/avec2012/test_synthesis/gen-lab ${EXAMPLE_DIR}/s1/experiments/avec2012/acoustic_model/data

#overwrite file_id_list.scp file with test_id_list.scp

#edit config file so it has correct number of files train test or valid?
#test_synth_avec2012.conf
