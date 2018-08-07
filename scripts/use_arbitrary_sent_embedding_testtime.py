'''
For a given sentence embedding (located in a file on disk)

We use it to generate utterances

We do this by replacing a row in the trained model P matrix with the CV
And then generating all utts in the test set with this row in the trained model P matrix
'''

#use set_control_vector.py

#make sure u replace the model with the backup, so that projection matrix P is returned back to normal
