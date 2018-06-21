#!/bin/bash -e

#paths appropriate for mlp cluster
BUILD_YOUR_OWN_VOICE_DIR=/home/s1785140/merlin/egs/build_your_own_voice
MSCPROJECT_DIR=/home/s1785140/mscproject
SCRATCH_DIR=/home/s1785140/SCRATCH
# SCRATCH_DIR=/disk/scratch/s1785140 #no access to this scratch folder?
AVEC2012_DIR=${SCRATCH_DIR}/AVEC2012
VOICE_NAME=avec2012
SPEAKER_ID_TO_GENERATE=1

if test "$#" -ne 1; then
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

# rsync -avu s1785140@student.ssh.inf.ed.ac.uk:/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/ /home/s1785140/mscproject/ #rsync over script files

#prep data, labels, and alignments using festival and HTK
if [ "$prepdata" = true ]; then
  mkdir -p ${AVEC2012_DIR}/recordings
  mkdir -p ${AVEC2012_DIR}/transcripts
  rsync -avu --delete s1785140@student.ssh.inf.ed.ac.uk:/group/project/disnv/AVEC2012/recordings/dialogues ${AVEC2012_DIR}/recordings #rsync over files for AVEC2012
  rsync -avu --delete s1785140@student.ssh.inf.ed.ac.uk:/group/project/disnv/AVEC2012/transcripts/original ${AVEC2012_DIR}/transcripts #rsync over files for AVEC2012
  ./prepdata.sh $BUILD_YOUR_OWN_VOICE_DIR $MSCPROJECT_DIR $SCRATCH_DIR $AVEC2012_DIR $VOICE_NAME
fi

#train models
if [ "$traindnn" = true ]; then
  ./traindnn.sh $BUILD_YOUR_OWN_VOICE_DIR $VOICE_NAME
fi

#use trained models to synthesise speech
if [ "$synth" = true ]; then
  ./synthesise.sh $BUILD_YOUR_OWN_VOICE_DIR $MSCPROJECT_DIR $VOICE_NAME $SPEAKER_ID_TO_GENERATE
fi
