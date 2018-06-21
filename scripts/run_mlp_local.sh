#!/bin/bash -e

#rsync over mscproject directory
rsync -avu s1785140@student.ssh.inf.ed.ac.uk:/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/ /home/s1785140/mscproject/

./run_real_mlp.sh $1
