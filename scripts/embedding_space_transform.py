import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import os
import re
from glob import glob
import sys

'''
Remember to !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
source activate pytorch

Code to learn a transform from 4-dim emotion space to 10-dim sentence space

Input are like: (a, e, p, v)
Outputs are like: (sent_dim_1, sent_dim_2, sent_dim_3, ..., sent_dim_10)
'''

'''
train: train the model and then save to disk
python embedding_space_transform.py train


generate: load the model from disk, then use it to generate a sent embedding from emot embedding
python embedding_space_transform.py generate

'''

model_path = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/nnmodel_backups/transform/transform.pt'

#NB SMALL DATASET: define the files that contain input features and output features
# in_feats_filename = '/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/tokenprojection/s1/experiments/tokenprojection/acoustic_model/data/label_state_align'
# out_feats_filename = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/projection_weights_backup/tokenprojection/acoustic_model/proj_INFERENCE_epoch_24'

#NB SMALL DATASET: define the files that contain input features and output features
in_feats_filename = '/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/tokenprojection/s1/experiments/tokenprojection_alldata/acoustic_model/data/label_state_align'
out_feats_filename = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/projection_weights_backup/tokenprojection_alldata/projection_weights_acoustic_model/projection_weights/proj_INFERENCE_epoch_25'

hdims = 10
hlayers = 0

#used for generation
emot_embedding_file = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/emot_embedding_to_generate/emot_embedding'
sent_embedding_file = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/sent_embedding_to_generate/sent_embedding'


'''
define the model
'''
class Net(nn.Module):
    def __init__(self, hdims, hlayers, flip=False):
        super(Net, self).__init__()
        if not flip:
            in_dims = 4
            out_dims = 10
        elif flip:
            in_dims = 10
            out_dims = 4
        # an affine operation: y = Wx + b
        self.fc1 = nn.Linear(in_dims, hdims)
        self.fc2 = nn.Linear(hdims, hdims)
        self.fc3 = nn.Linear(hdims, out_dims)
        self.dropout = nn.Dropout(p=0.5)
        self.hlayers = hlayers

        self.nonlin = F.relu
        # self.nonlin = F.tanh
        # self.nonlin = F.sigmoid

    def forward(self, x):
        x = self.nonlin(self.fc1(x))
        x = self.dropout(x)
        for i in range(self.hlayers):
            x = self.nonlin(self.fc2(x))
            x = self.dropout(x)
        x = self.fc3(x)
        return x

def train():
    # create class that can generate datasets from our files
    class TransformDataset(Dataset):
        '''
        in_feats_filename: list of input features. usually a lab file from htk with emotio labels and utt_id
        out_feats_filename: projection weights matrix file
        train_or_test: get the training set or the test set
        flip: whether to flip around input and targets
        '''
        def __init__(self, in_feats_filename, out_feats_filename, train_or_test, flip=False):
            #read in whole list of files inside in_feats_filename
            paths = glob(os.path.join(in_feats_filename, '*'))

            #only keep paths that are from AVEC2012 and thus have emotion ids
            paths = [p for p in paths if '_sent' in p]

            assert train_or_test == 'train' or train_or_test == 'test'
            threshold = int(len(paths)*0.8) #where to divide train and test set
            if train_or_test == 'train':
                paths = paths[:threshold]
            elif train_or_test == 'test':
                paths = paths[threshold:]

            emot_dict = {}

            print(len(paths))

            #iterate over each file/utt
            for p in paths:
                #hold counts so we can find avg
                all_a = []
                all_e = []
                all_p = []
                all_v = []

                with open(p) as f:
                    lines = f.readlines()

                for line in lines:
                    # no scientific notation
                    # a, e, p, v, utt_id = re.findall('/L:([\d.-]+)/M:([\d.-]+)/N:([\d.-]+)/O:([\d.-]+)/UTTID:(\d+)', line)[0]

                    #scientific notation
                    a, e, p, v, utt_id = re.findall('/L:([\d.e-]+)/M:([\d.e-]+)/N:([\d.e-]+)/O:([\d.e-]+)/UTTID:(\d+)', line)[0]

                    #append val to totals
                    all_a.append(float(a))
                    all_e.append(float(e))
                    all_p.append(float(p))
                    all_v.append(float(v))

                #get the average emotion val for each emotion dimension
                avg_a = np.mean(all_a)
                avg_e = np.mean(all_e)
                avg_p = np.mean(all_p)
                avg_v = np.mean(all_v)

                # print('utt_id', utt_id)

                emot_dict[int(utt_id)] = (avg_a, avg_e, avg_p, avg_v)

            self.datarows = []

            with open(out_feats_filename) as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                #only get lines from the out_feats_filename that were AVEC2012, i.e. those that are in emot_dict
                if i in emot_dict:
                    emotions = torch.tensor(emot_dict[i], dtype=torch.float)
                    controlvector = torch.tensor([float(string) for string in line.split()])
                    assert len(emotions) == 4
                    assert len(controlvector) == 10
                    if not flip:
                        self.datarows.append((emotions, controlvector))
                    elif flip:
                        self.datarows.append((controlvector, emotions))


            # print(len(self.datarows), self.datarows[0])

        def __len__(self):
            return len(self.datarows)

        def __getitem__(self, idx):
            #tuple of input features and targets
            #((a, e, p, v), (sent_dim_1, sent_dim_2, sent_dim_3, ..., sent_dim_10))
            return self.datarows[idx]

    #set seed so we can get reproducible results
    torch.manual_seed(1337)
    FLIP = False

    '''
    load the data into dataloader
    '''
    trainset = TransformDataset(in_feats_filename, out_feats_filename, 'train', flip=FLIP)
    testset = TransformDataset(in_feats_filename, out_feats_filename, 'test', flip=FLIP)

    trainloader = torch.utils.data.DataLoader(trainset, batch_size=2,
                                              shuffle=True, num_workers=2)
    testloader = torch.utils.data.DataLoader(testset, batch_size=2,
                                             shuffle=False, num_workers=2)

    '''
    construct model the model
    '''
    net = Net(hdims=hdims, hlayers=hlayers, flip=FLIP)
    print(net)

    '''
    define loss and optimiser
    '''
    criterion = nn.MSELoss()
    # optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
    optimizer = optim.Adam(net.parameters(), lr=0.001)

    '''
    train the model
    '''
    for epoch in range(10):

        running_loss = 0.0

        for i, data in enumerate(trainloader):
            #get the inputs
            inputs, targets = data

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
            num_mini = 500
            #print every n minibatches
            if i % num_mini == num_mini-1:
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / num_mini))
                running_loss = 0.0

    print('Finished Training')

    '''
    test the model
    '''
    print('Testing the model')
    net.eval() #need this so that dropout isn't applied during forward passes
    with torch.no_grad():
        print('Number of mini-batches in testdata', len(testloader))
        losses = []
        for data in testloader:
            inputs, targets = data
            outputs = net(inputs)
            loss = criterion(outputs, targets)
            losses.append(loss.item())
        print('average mini-batch loss is', np.mean(losses))

    '''
    save the model to disk
    '''
    torch.save(net.state_dict(), model_path)

def generate():
    try:
        amp_factor = float(sys.argv[2])
    except LookupError:
        amp_factor = 1

    # print('amp factor is', amp_factor)

    '''load the model'''
    net = Net(hdims=hdims, hlayers=hlayers)
    net.load_state_dict(torch.load(model_path))

    '''load the emot embedding'''
    with open(emot_embedding_file) as f:
        emot_embedding = f.readline()
    emot_embedding = [float(string) for string in emot_embedding.split()]
    print('emot_embedding IN is', emot_embedding)
    emot_embedding = torch.tensor(emot_embedding, dtype=torch.float)

    '''pass emot embedding through the network'''
    net.eval()
    with torch.no_grad():
        sent_embedding = net(emot_embedding)
        # print(net(torch.Tensor([100,0,100,0])))
        # print(net(torch.Tensor([0,100,0,100])))
        # print(net(torch.Tensor([5,3,12,6])))
        # print(net(torch.Tensor([10444,2222222,18,333])))
        # print(net(torch.Tensor([-0.0833411,34.140556,0.375480657,0.06304983773])))
        # print(net(torch.Tensor([-5,50,5,5])))
        # print(net(torch.Tensor([1000000,34.140556,0.375480657,0.06304983773])))


    '''wrangle into string'''
    sent_embedding = sent_embedding.tolist()
    print('emot_embedding OUT is', sent_embedding)
    sent_embedding = ' '.join([str(amp_factor * num) for num in sent_embedding])

    '''save sent embedding '''
    with open(sent_embedding_file, 'w') as f:
        f.write(sent_embedding)

if sys.argv[1] == 'train':
    train()
elif sys.argv[1] == 'generate':
    generate()
