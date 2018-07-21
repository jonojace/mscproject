#!/bin/bash -e

#paths appropriate for dice
# BUILD_YOUR_OWN_VOICE_DIR=/afs/inf.ed.ac.uk/user/s17/s1785140/merlin/egs/build_your_own_voice #this directory is running out of space
BUILD_YOUR_OWN_VOICE_DIR=/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/tokenprojection
MSCPROJECT_DIR=/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject
# SCRATCH_DIR=/afs/inf.ed.ac.uk/group/msc-projects/s1785140 #this directory can max hold 20 gigs
SCRATCH_DIR=/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/data_for_tokenprojection #perhaps use this place has TBs!, but its not backed up!

#NB All the data!!!!
AVEC2012_DIR=/group/project/disnv/AVEC2012
LESLIE_DATA=/afs/inf.ed.ac.uk/group/cstr/projects/blizzard_entries/blizzard2017/parametric_synthesis/benchmark-merlin-data
VOICE_NAME=tokenprojection_alldata

# #NB use below for testing as smaller amount of data
# AVEC2012_DIR=/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/small_data_for_testing/AVEC2012
# LESLIE_DATA=/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/small_data_for_testing/benchmark-merlin-data
# VOICE_NAME=tokenprojection

##############################
#Additional features when synthesising
SPEAKER_ID_TO_GENERATE=$2
AROUSAL=$3
EXPECTANCY=$4
POWER=$5
VALENCE=$6

if test "$#" -lt 1; then
    echo "################################"
    echo "Usage: "
    echo "./train.sh <command>"
    echo "Available commands:"
    echo "  prepdata - only prep data"
    echo "  traindnn - only train dnn"
    echo "  synth - only synthesise test utts"
    echo "  buildvoice - prep data then train dnn"
    echo "  all - prep data, train dnn, then synthesise test utts"
    echo "################################"
    exit 1
fi

#set appropriate flags
if [ $1 == "prepdata" ]; then prepdata=true; fi
if [ $1 == "traindnn" ]; then traindnn=true; fi
if [ $1 == "synth" ]; then synth=true; fi
if [ $1 == "buildvoice" ]; then prepdata=true; traindnn=true; fi
if [ $1 == "all" ]; then prepdata=true; traindnn=true; synth=true; fi

#prep data, labels, and alignments using festival and HTK
if [ "$prepdata" = true ]; then
  ./prepdata_tp.sh $BUILD_YOUR_OWN_VOICE_DIR $MSCPROJECT_DIR $SCRATCH_DIR $AVEC2012_DIR $VOICE_NAME $LESLIE_DATA
fi

#train DNN models
if [ "$traindnn" = true ]; then
  ./traindnn_tp.sh $BUILD_YOUR_OWN_VOICE_DIR $VOICE_NAME
fi

#use trained models to synthesise speech
if [ "$synth" = true ]; then
  ./synthesise_tp.sh $BUILD_YOUR_OWN_VOICE_DIR $MSCPROJECT_DIR $VOICE_NAME $SPEAKER_ID_TO_GENERATE $AROUSAL $EXPECTANCY $POWER $VALENCE
fi
