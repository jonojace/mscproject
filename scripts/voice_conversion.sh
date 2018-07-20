'''
Use sprocket to train voice converter from AVM trained on AVEC2012 to leslie simms voice

Usage:
./voice_conversion.sh <path to file with list of utts to include>
'''

#####################################################################################
#NB need to ensure that sample rate and number of channels is same for all files
#NB for source and target speaker
#use scripts resample.sh and stereo_to_mono.sh to handle that!
#####################################################################################

#load the list of utts to include

#select subset of leslie's utts for AVM to synthesise

#copy the text files into mscproject/text_to_generate

#synthesise these text files as wavs using AVM

#move these files into correct folder for sprocket

#move leslie simms original wavs for these utts into the correct folder for sprocket

#train sprocket

#run sprocket on test txt files

#open folder with generated wav files
