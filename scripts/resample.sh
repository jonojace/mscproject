#!/bin/bash -e

#script to resample all wav files in a folder to a new sampling rate

if test "$#" -lt 2; then
    echo "################################"
    echo "Usage: "
    echo "./resample.sh <folder> <sample rate>"
    echo "################################"
    exit 1
fi

FOLDER=$1
SAMPLE_RATE=$2

for i in ${1}/*.wav; do #might need to add or remove the forward slash depending on whether u input 'folder' or 'folder/'
  	sox $i ${i%.wav}xxx.wav rate ${SAMPLE_RATE} #percentage removes the .wav from the filename
  	mv ${i%.wav}xxx.wav $i
done
