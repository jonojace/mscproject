'''
Add questions for speaker ID and emotion ID to vectorise HTS format labels
'''

QUESTION_FILE_PATH = '/afs/inf.ed.ac.uk/user/s17/s1785140/merlin/misc/questions/questions-radio_dnn_416.hed'
NUM_OF_SPEAKERS = 6

#note need to double the curly braces to escape them
speaker_id_rule = '\nQS "Speaker_ID=={0:}"    {{/K:{0:}}}'

for i in range(1, NUM_OF_SPEAKERS + 1):
    with open(QUESTION_FILE_PATH, 'a') as f:
        f.write(speaker_id_rule.format(i))
