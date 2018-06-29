#!/bin/bash -e

#perform full process of training a merlin model using AVEC2012 data
#with speaker and emotion labels
#and then synthesise test utterances

echo "---INSIDE prepdata.sh"

if test "$#" -ne 5; then
    echo "################################"
    echo "Usage: "
    echo "./train.sh <path/to/build_your_own_voice> <path/to/mscproject> <path/to/scratch_dir> <path/to/AVEC2012> <voice name>"
    echo "################################"
    exit 1
fi

EXAMPLE_DIR=$1 #path to the build_your_own_voice where we will be running files
MSCPROJECT_DIR=$2 #path to mscproject directory that holds various small files
SCRATCH_DIR=$3 #should be a place LARGE enough to store processed audio files
AVEC2012_DIR=$4
VOICE_NAME=$5
MERLIN_DIR=${EXAMPLE_DIR}/../..
COPY_OVER_DIR=${MSCPROJECT_DIR}/copy_over

#folders in mscproject directory
SCRIPT_DIR=${MSCPROJECT_DIR}/scripts #holds all scripts
FRESH_EXAMPLE_DIR=${MSCPROJECT_DIR}/merlin-master/egs/build_your_own_voice #fresh copy of merlin for resetting directories
# TEXT_TO_GENERATE_FOLDER=${MSCPROJECT_DIR}/text_to_generate #contains txt files to generate

CLEANED_DATA_DIR=${SCRATCH_DIR}/AVEC2012_clean_for_merlin

MIN_WAV_FILE_SIZE=100000 #in bytes
VAL_AND_TEST_PERCENT=10 #does this greatly affect DNN training quality?
SAMPLING_FREQUENCY=48000

#source the conda environment
# source ~/.bashrc #NB is this really needed for sox?? or something else??? only needed on MLP cluster? I think this should only be done once after logging into the MLP cluster
source activate msc

#delete contents of folders
if [ -d "${EXAMPLE_DIR}" ]; then
  rm -r ${EXAMPLE_DIR}
fi
if [ -d "${CLEANED_DATA_DIR}" ]; then
  rm -r ${CLEANED_DATA_DIR}
fi

#replace with fresh version
cp -r ${FRESH_EXAMPLE_DIR} ${EXAMPLE_DIR}

#copy over edited files
echo copying ${COPY_OVER_DIR}/questions-radio_dnn_416.hed to ${MERLIN_DIR}/misc/questions
cp ${COPY_OVER_DIR}/questions-radio_dnn_416.hed ${MERLIN_DIR}/misc/questions #questions file
#BELOW ARE ONLY NEEDED IF U WANT TO USE CONTINUOUS LABELS AS SRIKANTH DETAILED
# cp ${COPY_OVER_DIR}/prepare_config_files.sh ${EXAMPLE_DIR}/s1/scripts #${MERLIN_DIR} # merlin/egs/build_your_own_voice/s1/scripts/prepare_config_files.sh , you added a line for additional features
# cp ${COPY_OVER_DIR}/prepare_config_files_for_synthesis.sh ${EXAMPLE_DIR}/s1/scripts
# cp ${COPY_OVER_DIR}/duration_demo.conf ${MERLIN_DIR}/misc/recipes # merlin/misc/recipes/duration_demo.conf #you added additional_features = None
# cp ${COPY_OVER_DIR}/acoustic_demo.conf ${MERLIN_DIR}/misc/recipes # merlin/misc/recipes/acoustic_demo.conf #you added additional_features = None

#cd into the correct directory for running the merlin step by step scripts
cd ${EXAMPLE_DIR}/s1

# step 1: run setup
./01_setup.sh ${VOICE_NAME}

#check if txt and wav folders in  clean data folder exist, if they do, delete and recreate them
#txt folder
mkdir -p ${CLEANED_DATA_DIR}/txt
if [ -d "${CLEANED_DATA_DIR}/txt" ]; then
  rm -r ${CLEANED_DATA_DIR}/txt
  mkdir ${CLEANED_DATA_DIR}/txt
else
  mkdir -p ${CLEANED_DATA_DIR}/txt
fi
#wav folder
mkdir -p ${CLEANED_DATA_DIR}/wav
if [ -d "${CLEANED_DATA_DIR}/wav" ]; then
  rm -r ${CLEANED_DATA_DIR}/wav
  mkdir ${CLEANED_DATA_DIR}/wav
else
  mkdir -p ${CLEANED_DATA_DIR}/wav
fi

# clean data for this experiment, and transfer to the clean data folder
python ${SCRIPT_DIR}/AVEC2012_clean_for_merlin.py ${AVEC2012_DIR}/ ${CLEANED_DATA_DIR}/ ${MIN_WAV_FILE_SIZE}

#convert bit rate
for i in ${CLEANED_DATA_DIR}/wav/*.wav; do
  #-G automatically adjusts gain to stop clipping
  	sox -G $i -b16 ${i%.wav}_16bit.wav; #percentage removes the .wav from the filename
  	rm $i
done

#copy cleaned data into database folder
cp -r ${CLEANED_DATA_DIR}/wav ${EXAMPLE_DIR}/s1/database
cp -r ${CLEANED_DATA_DIR}/txt ${EXAMPLE_DIR}/s1/database

#perhaps add code to update the emotion labels
#in ${MSCPROJECT_DIR}/sentence_continuous_emotion_labels/
#IF we need to.

#NB following code not in use as we are now not using fully continuous emotion labels, just state level
# #deal with continuous emotion labels
# mkdir -p ${EXAMPLE_DIR}/s1/database/feats #create location to store continuous emotion labels
# #create continuous emotion labels
# python ${SCRIPT_DIR}/create_emotion_label_files.py ${AVEC2012_DIR} ${SCRATCH_DIR}/sentence_continuous_emotion_labels/
# #move continuous emotion labels to the correct folder
# cp -r ${SCRATCH_DIR}/sentence_continuous_emotion_labels/* ${EXAMPLE_DIR}/s1/database/feats

#get number of utterances created (info needed for config file)
#$(.) is used to store results of command in variable
#ls -1q lists files in directory line by line
num_utts=$(ls -1q ${EXAMPLE_DIR}/s1/database/wav | wc -l) #total number of files

#modify config file with appropriate settings for your data
VAL_AND_TEST_SIZE=$(($num_utts*$VAL_AND_TEST_PERCENT/100))
train_size=$(expr $num_utts - $VAL_AND_TEST_SIZE - $VAL_AND_TEST_SIZE) #expr is bash's way of doing math
val_size=$VAL_AND_TEST_SIZE
test_size=$VAL_AND_TEST_SIZE
#sed uses regex to replace what's in a file, without having to create a new file, it does it 'inplace'
#example: sed -i 's/original/new/g' file.txt
#s:substitute, g:global
#NB when using a bash variable in a string, only works correct in double quotes "${VAR}" not single quotes '${VAR}'
sed -i "s/SamplingFreq=\([0-9]\+\)/SamplingFreq=${SAMPLING_FREQUENCY}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg
# sed -i "s/Train=\([0-9]\+\)/Train=${train_size}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg
# sed -i "s/Valid=\([0-9]\+\)/Valid=${val_size}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg
# sed -i "s/Test=\([0-9]\+\)/Test=${test_size}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg

# step 2: prepare labels
mkdir -p database/labels/label_state_align
./02_prepare_labels.sh database/wav database/txt database/labels

#since we may not be able to align properly for all the data, we need to update the number of utterances
num_utts=$(ls -1q ${EXAMPLE_DIR}/s1/database/labels/label_state_align | wc -l) #number of files that successfully get state alignments
VAL_AND_TEST_SIZE=$(($num_utts*$VAL_AND_TEST_PERCENT/100))
train_size=$(expr $num_utts - $VAL_AND_TEST_SIZE - $VAL_AND_TEST_SIZE) #expr is bash's way of doing math
val_size=$VAL_AND_TEST_SIZE
test_size=$VAL_AND_TEST_SIZE
# sed -i "s/SamplingFreq=\([0-9]\+\)/SamplingFreq=${SAMPLING_FREQUENCY}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg
sed -i "s/Train=\([0-9]\+\)/Train=${train_size}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg
sed -i "s/Valid=\([0-9]\+\)/Valid=${val_size}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg
sed -i "s/Test=\([0-9]\+\)/Test=${test_size}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg

#add speaker and emotion id labels
#add emotion id labels (state level emotion labels after meeting with oliver on wed 27th june)
python ${SCRIPT_DIR}/appendSpeakerAndEmotionIDToLabels.py ${EXAMPLE_DIR} ${AVEC2012_DIR}
#do not need to add the addQuestions script here, as the questions file is located within the merlin dir, not specific to each experiment

# step 3: extract acoustic features
./03_prepare_acoustic_features.sh database/wav database/feats

# step 4: prepare config files for training and testing
./04_prepare_conf_files.sh conf/global_settings.cfg

#BELOW only needed if using continuous emotion labels I think
# #copy over emotion labels to the experiments/avec2012/duration_model/data directory (they already get copied over to the acoustic one for some reason)
# cp -r ${SCRATCH_DIR}/sentence_continuous_emotion_labels/* ${EXAMPLE_DIR}/s1/experiments/avec2012/duration_model/data
