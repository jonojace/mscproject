#run this script when logged into mlp server

if test "$#" -ne 1; then
    echo "################################"
    echo "Usage: "
    echo "./copy_wav_from_mlp.sh <voice name>"
    echo "################################"
    exit 1
fi

VOICE_NAME=$1
EXAMPLE_DIR=/home/s1785140/merlin/egs/build_your_own_voice

rsync -avu ${EXAMPLE_DIR}/s1/experiments/${VOICE_NAME}/test_synthesis/wav/ /afs/inf.ed.ac.uk/user/s17/s1785140/analysis_mscproject/generated_output/${VOICE_NAME}
