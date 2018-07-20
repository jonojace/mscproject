'''
Loads TPDNN model and sets the first row of P to given weights
'''

'''
for testing:
python set_control_vector.py '/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/slt_arctic/s1/experiments/slt_arctic_demo/duration_model/nnets_model/feed_forward_4_tanh.model' 0.1 0.1 0.1 0.1
'''

import sys
import pickle
from models.tpdnn import TokenProjectionDNN

if len(sys.argv) != 6:
    print("################################")
    print("python set_control_vector.py <path_to_model_file> <CV dim 1> <CV dim 2> <CV dim 3> <CV dim 4>")
    print("################################")
    raise Exception

#get command line args
path_to_model_file = sys.argv[1]
dim_1 = sys.argv[2]
dim_2 = sys.argv[3]
dim_3 = sys.argv[4]
dim_4 = sys.argv[5]

#load model
dnn_model = pickle.load(open(path_to_model_file, 'rb'))

#check if you have loaded the model correctly
print(dnn_model.get_projection_weights())

#set first row of P


#dump model back to disk
