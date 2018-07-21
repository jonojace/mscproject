#!/bin/bash -e

#perform full process of training a merlin model using AVEC2012 data
#with speaker and emotion labels
#and then synthesise test utterances

echo "---INSIDE prepdata.sh"

if test "$#" -ne 6; then
    echo "################################"
    echo "Usage: "
    echo "./train.sh <path/to/build_your_own_voice> <path/to/mscproject> <path/to/scratch_dir> <path/to/AVEC2012> <voice name> <LESLIE_DATA>"
    echo "################################"
    exit 1
fi

echo "Setting up command line args"
#get command line args
EXAMPLE_DIR=$1 #path to the build_your_own_voice where we will be running files
MSCPROJECT_DIR=$2 #path to mscproject directory that holds various small files
SCRATCH_DIR=$3 #should be a place LARGE enough to store processed audio files
LABEL_STATE_ALIGN_FOLDER=$4 #path to label state align folder already been processed by appendSentenceEmbeddingToLabels
VOICE_NAME=$5
LESLIE_DATA=$6

#create additional dirs
MERLIN_DIR=${EXAMPLE_DIR}/../..
COPY_OVER_DIR=${MSCPROJECT_DIR}/copy_over

#folders in mscproject directory
SCRIPT_DIR=${MSCPROJECT_DIR}/scripts #holds all scripts
# FRESH_EXAMPLE_DIR=${MSCPROJECT_DIR}/merlin-master/egs/${VOICE_NAME} #fresh copy of merlin for resetting directories
# TEXT_TO_GENERATE_FOLDER=${MSCPROJECT_DIR}/text_to_generate #contains txt files to generate

CLEANED_DATA_DIR=${SCRATCH_DIR}/AVEC2012_clean_for_merlin

echo "Setting up vars"
# MIN_WAV_FILE_SIZE=100000 #in bytes
VAL_AND_TEST_PERCENT=5 #does this greatly affect DNN training quality?
SAMPLING_FREQUENCY=48000

#source the conda environment
# source ~/.bashrc #NB is this really needed for sox?? or something else??? only needed on MLP cluster? I think this should only be done once after logging into the MLP cluster
source activate msc

#NB!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#The code below only cleans the build your own voice directory
#if you want to clean the merlin folder you'll will have to delete and reinstall it yourself
################################################





#YOU SHOULD DO THIS BY HAND!!!
##########################################WARNING - UNCOMMENT AT YOUR OWN RISK
##########################################WARNING - UNCOMMENT AT YOUR OWN RISK
##########################################WARNING - UNCOMMENT AT YOUR OWN RISK
# # delete build your own voice dir NB don't want to clear out all our saved models!
# echo "DELETING AND REPLACING EXAMPLE_DIR"
# if [ -d "${EXAMPLE_DIR}" ]; then
#   rm -r ${EXAMPLE_DIR}
# fi
#
# # replace with fresh version
# echo "REPLACING WITH FRESH VERSION"
# cp -r ${FRESH_EXAMPLE_DIR} ${EXAMPLE_DIR}
##########################################WARNING - UNCOMMENT AT YOUR OWN RISK
##########################################WARNING - UNCOMMENT AT YOUR OWN RISK
##########################################WARNING - UNCOMMENT AT YOUR OWN RISK






echo "Removing cleaned data dir"
if [ -d "${CLEANED_DATA_DIR}" ]; then
  rm -r ${CLEANED_DATA_DIR}
fi

echo "Copying over edited files"
#copy over edited files
echo copying over files from copy_over to relevant destinations
cp ${COPY_OVER_DIR}/questions-radio_dnn_416_leslie.hed ${MERLIN_DIR}/misc/questions #questions file
cp ${COPY_OVER_DIR}/label_normalisation.py ${MERLIN_DIR}/src/frontend #label normalisation for ([\d\.-]+)
cp ${COPY_OVER_DIR}/forced_alignment.py ${MERLIN_DIR}/misc/scripts/alignment/state_align #for python3 and for larger datasets

#cd into the correct directory for running the merlin step by step scripts
cd ${EXAMPLE_DIR}/s1

# step 1: run setup
./01_setup.sh ${VOICE_NAME}

#sed in the correct questions file
sed -i "s/QuestionFile=questions-radio_dnn_416.hed/QuestionFile=questions-radio_dnn_416_leslie.hed/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg

#check if txt and wav folders in  clean data folder exist, if they do, delete and recreate them
#txt folder
echo "Cleaning out the cleaned data dir for wav and txt"
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

# # clean data for this experiment, and transfer to the clean data folder
# echo "Running AVEC2012_clean_for_merlin.py"
# python ${SCRIPT_DIR}/AVEC2012_clean_for_merlin.py ${AVEC2012_DIR}/ ${CLEANED_DATA_DIR}/ ${MIN_WAV_FILE_SIZE}
# #ython ${SCRIPT_DIR}/AVEC2012_clean_for_merlin_test.py ${AVEC2012_DIR}/ ${CLEANED_DATA_DIR}/ ${MIN_WAV_FILE_SIZE}

#NB TESTING! just removing all AVEC2012 data so we can see if we can align only on leslie's data
# rm ${CLEANED_DATA_DIR}/wav/*
# rm ${CLEANED_DATA_DIR}/txt/*

#NB leslie simms utts are 16 bit 44100Hz 2-channel, avec2012 is 16bit 48000Hz 1-channel
#copy over leslie simms wavs and txt files
echo "Copying leslies data over"
cp -r ${LESLIE_DATA}/wav/* ${CLEANED_DATA_DIR}/wav
cp -r ${LESLIE_DATA}/txt/* ${CLEANED_DATA_DIR}/txt

#convert bit rate and sample rate (does nothing to avec2012, upsamples blizzard2017 to match avec2012)
for i in ${CLEANED_DATA_DIR}/wav/*.wav; do
  #-G automatically adjusts gain to stop clipping
  #-r 48000 resamples
  #-b16 changes bit depth
  #remix 1 changes from stereo to mono
  	sox -G $i -r 48000 -b16 ${i%.wav}_temp.wav remix 1; #percentage removes the .wav from the filename
  	rm $i #remove the original file
    mv ${i%.wav}_temp.wav $i #remove _temp from the name of the modified file
done

#copy cleaned data into database folder
echo "Copying cleaned data into merlin dir"
cp -r ${CLEANED_DATA_DIR}/wav ${EXAMPLE_DIR}/s1/database
cp -r ${CLEANED_DATA_DIR}/txt ${EXAMPLE_DIR}/s1/database

#sed uses regex to replace what's in a file, without having to create a new file, it does it 'inplace'
#example: sed -i 's/original/new/g' file.txt
#s:substitute, g:global
#NB when using a bash variable in a string, only works correct in double quotes "${VAR}" not single quotes '${VAR}'
sed -i "s/SamplingFreq=\([0-9]\+\)/SamplingFreq=${SAMPLING_FREQUENCY}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg

# step 2: prepare labels
# mkdir -p database/labels/label_state_align

echo "copying lab files over"
#instead of preparing labels from scratch using
#./02_prepare_labels.sh database/wav database/txt database/labels
#we just use the ones made by the token projection model
#and have been processed by appendSentenceEmbeddingToLabels.py
duration_data_dir=experiments/${VOICE_NAME}/duration_model/data
acoustic_data_dir=experiments/${VOICE_NAME}/acoustic_model/data
cp -r $LABEL_STATE_ALIGN_FOLDER $duration_data_dir
cp -r $LABEL_STATE_ALIGN_FOLDER $acoustic_data_dir
ls $LABEL_STATE_ALIGN_FOLDER > $duration_data_dir/${VOICE_NAME}.scp
ls $LABEL_STATE_ALIGN_FOLDER > $acoustic_data_dir/${VOICE_NAME}.scp
sed -i 's/\.lab//g' $duration_data_dir/${VOICE_NAME}.scp
sed -i 's/\.lab//g' $acoustic_data_dir/${VOICE_NAME}.scp

#since we may not be able to align properly for all the data, we need to update the number of utterances
num_utts=$(ls -1q ${acoustic_data_dir}/label_state_align | wc -l) #number of files that successfully get state alignments
VAL_AND_TEST_SIZE=$(($num_utts*$VAL_AND_TEST_PERCENT/100))
train_size=$(expr $num_utts - $VAL_AND_TEST_SIZE - $VAL_AND_TEST_SIZE) #expr is bash's way of doing math
val_size=$VAL_AND_TEST_SIZE
test_size=$VAL_AND_TEST_SIZE
echo "Train size is ${train_size}"
echo "Val size is ${val_size}"
echo "Test size is ${test_size}"
sed -i "s/Train=\([0-9]\+\)/Train=${train_size}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg
sed -i "s/Valid=\([0-9]\+\)/Valid=${val_size}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg
sed -i "s/Test=\([0-9]\+\)/Test=${test_size}/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg
#TODO if you change code so the amount data copied over to duration and acoustic model dirs is different (file_id_list too)
#TODO then will need to change these numbers appropriate for them

#sed in the ${VOICE_NAME}.scp file list id into the config file
sed -i "s/FileIDList=.*/FileIDList=${VOICE_NAME}.scp/g" ${EXAMPLE_DIR}/s1/conf/global_settings.cfg

# step 3: extract acoustic features
./03_prepare_acoustic_features.sh database/wav database/feats

# step 4: prepare config files for training and testing
./04_prepare_conf_files.sh conf/global_settings.cfg
