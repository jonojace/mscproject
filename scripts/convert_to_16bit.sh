source ~/.bashrc



for i in /afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/AVEC2012_clean_for_merlin/wav/*.wav; do
  #-G automatically adjusts gain to stop clipping
  	sox -G $i -b16 ${i%.wav}_16bit.wav; #percentage removes the .wav from the filename
  	rm $i
done
