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

#copy the projection weights folder so it doesn't get overwritten when we train the acoustic model
cp -r projection_weights/ projection_weights_duration_model

# step 6: train acoustic model
./06_train_acoustic_model.sh conf/acoustic_${VOICE_NAME}.conf

#rename folder
mv projection_weights/ projection_weights_acoustic_model
