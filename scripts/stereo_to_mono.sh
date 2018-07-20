#!/bin/bash -e

#script to reduce all wav files in folder from stereo to mono

#keep the left channel

if test "$#" -lt 1; then
    echo "################################"
    echo "Usage: "
    echo "./stereo_to_mono.sh <folder>"
    echo "################################"
    exit 1
fi

FOLDER=$1

for i in ${1}/*.wav; do #might need to add or remove the forward slash depending on whether u input 'folder' or 'folder/'
  	sox $i ${i%.wav}xxx.wav remix 1 #percentage removes the .wav from the filename
  	mv ${i%.wav}xxx.wav $i
done
