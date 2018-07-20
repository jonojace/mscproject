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

if len(sys.argv) != 7:
    print("################################")
    print("python set_control_vector.py <path_to_model_file> <row_to_change> <CV dim 1> <CV dim 2> <CV dim 3> <CV dim 4>")
    print("################################")
    raise Exception

#get command line args
path_to_model_file = sys.argv[1]
row_to_change = int(sys.argv[2])
dim_1 = float(sys.argv[3])
dim_2 = float(sys.argv[4])
dim_3 = float(sys.argv[5])
dim_4 = float(sys.argv[6])

#load model
dnn_model = pickle.load(open(path_to_model_file, 'rb'))

#check if you have loaded the model correctly
# print('dnn_model.get_projection_weights().shape =', dnn_model.get_projection_weights().shape)
print('In projection matrix P, weights in row', row_to_change, 'are', dnn_model.get_projection_weights()[row_to_change])

#set first row of P
print('Attempting to change those weights to', [dim_1, dim_2, dim_3, dim_4])
dnn_model.set_projection_weights(row=row_to_change, values=[dim_1, dim_2, dim_3, dim_4])

print('In projection matrix P, weights in row', row_to_change, 'are now', dnn_model.get_projection_weights()[row_to_change])

#dump model back to disk
print('Overwriting previous model')
pickle.dump(dnn_model, open(path_to_model_file, 'wb'))
