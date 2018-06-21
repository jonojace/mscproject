#!/bin/bash -e

#perform full process of training a merlin model using AVEC2012 data
#with speaker and emotion labels
#and then synthesise test utterances

echo "---INSIDE synthesise.sh"

if test "$#" -ne 4; then
    echo "################################"
    echo "Usage: "
    echo "./synthesise.sh <path/to/build_your_own_voice> <path/to/mscproject> <voice name> <speaker_id_to_generate>"
    echo ""
    echo "Enter a speaker id, such as 1 or 2"
    echo "################################"
    exit 1
fi

EXAMPLE_DIR=$1 #path to the build_your_own_voice where we will be running files
MSCPROJECT_DIR=$2 #path to mscproject directory that holds various small files
VOICE_NAME=$3
SPEAKER_ID_TO_GENERATE=$4

SCRIPT_DIR=${MSCPROJECT_DIR}/scripts
TEXT_TO_GENERATE_FOLDER=${MSCPROJECT_DIR}/text_to_generate #contains txt files to generate

#copy text files to generate into appropriate folder

cd ${EXAMPLE_DIR}/s1

cp -r ${TEXT_TO_GENERATE_FOLDER}/. experiments/${VOICE_NAME}/test_synthesis/txt/

# echo ${SPEAKER_ID_TO_GENERATE}

# step 7: run text to speech
#take all the text files in /txt/ and store file names in test_id_list.scp
basename --suffix=.txt -- experiments/${VOICE_NAME}/test_synthesis/txt/* > experiments/${VOICE_NAME}/test_synthesis/test_id_list.scp
#use sed to inject code into 07_run_merlin.sh so that we can add speaker labels to festival lab files
#NB using ? as delimited in sed instead of /
sed -i "29s?.*?python ${SCRIPT_DIR}/appendSpeakerIDToLabels_TestTime.py ${EXAMPLE_DIR} ${SPEAKER_ID_TO_GENERATE}?" 07_run_merlin.sh
#synthesis speech from test sentences
./07_run_merlin.sh experiments/${VOICE_NAME}/test_synthesis/txt conf/test_dur_synth_${VOICE_NAME}.conf conf/test_synth_${VOICE_NAME}.conf

#rsync the files from mlp cluster to dice machine
# rsync -avu ${EXAMPLE_DIR}/s1/experiments/${VOICE_NAME}/test_synthesis/wav /afs/inf.ed.ac.uk/user/s17/s1785140/analysis_mscproject/generated_output

#open the folder with output wav files (only do this when running on dice)
# nautilus ${EXAMPLE_DIR}/s1/experiments/${VOICE_NAME}/test_synthesis/wav
