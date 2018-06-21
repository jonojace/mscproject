#!/bin/bash -e

#rsync over mscproject directory
rsync -avu s1785140@student.ssh.inf.ed.ac.uk:/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/ /home/s1785140/mscproject/

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

#NB WARNING as you can't rsync in a submitted job, you may have to run
#./run_mlp_local.sh prepdata in order to copy over some necessary files such as AVEC2012 raw files

#NB as prepdata takes longer than 8 hrs on MLP cluster
#instead, run prepdata on dice machine, then rsync files to MLP cluster then run
#traindnn and synth

sbatch ./run_real_mlp_job.sh $1
