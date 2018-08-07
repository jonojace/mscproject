'''
Loads TPDNN model and sets the first row of P to given weights

Copy me from mscproject/scripts folder to merlin/src folder and run there.
'''

'''
for testing:
python set_control_vector.py '/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/slt_arctic/s1/experiments/slt_arctic_demo/duration_model/nnets_model/feed_forward_4_tanh.model' 0 0.1 0.1 0.1 0.1
'''

import sys
import pickle
from models.tpdnn import TokenProjectionDNN

if len(sys.argv) != 5:
    print("################################")
    print("python set_control_vector.py <path_to_model_file> <row_to_change> <path_to_input_file> <input_row>")
    print("################################")
    raise Exception

'''
<path_to_model_file>    the nn model that we will modify weights of in projection matrix
<row_to_change>         the row in the P matrix that we will modify
<path_to_input_file>    an input file containing rows of weights
<input_row>             the row in the input file that we want to use to overwrite what is in <row_to_change>

testing use

python /group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/src/set_control_vector.py /group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/tokenprojection/s1/experiments/tokenprojection/acoustic_model/nnets_model/feed_forward_6_tanh.model 0 /group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/tokenprojection/s1/projection_weights_small_data_acoustic_model/proj_INFERENCE_epoch_24 0
'''

#get command line args
path_to_model_file = sys.argv[1]
row_to_change = int(sys.argv[2])
path_to_input_file = sys.argv[3]
input_row = int(sys.argv[4])

#load model
dnn_model = pickle.load(open(path_to_model_file, 'rb'))

#check if you have loaded the model correctly
# print('dnn_model.get_projection_weights().shape =', dnn_model.get_projection_weights().shape)
print('\nIn projection matrix P, weights in row', row_to_change, 'are', dnn_model.get_projection_weights()[row_to_change])

#get the desired row that we want to use to overwrite what is in our nn model
with open(path_to_input_file) as f:
    input_file = f.readlines()
line = input_file[input_row]
line = [float(string) for string in line.split()]
print('\nThe data you want to insert', line)

#set first row of P
print('Attempting to change those weights to', line)
dnn_model.set_projection_weights(row=row_to_change, values=line)

print('In projection matrix P, weights in row', row_to_change, 'are now', dnn_model.get_projection_weights()[row_to_change])

# #dump model back to disk
# print('Overwriting previous model')
# pickle.dump(dnn_model, open(path_to_model_file, 'wb'))
