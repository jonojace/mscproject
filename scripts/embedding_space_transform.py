import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import os
import re
from glob import glob

'''
Code to learn a transform from 4-dim emotion space to 10-dim sentence space

Input are like: (a, e, p, v)
Outputs are like: (sent_dim_1, sent_dim_2, sent_dim_3, ..., sent_dim_10)
'''

'''
handle the dataset from files on disk
'''
#define the files that contain input features and output features
in_filename = '/group/project/cstr1/mscslp/2017-18/s1785140_Jason_Fong/merlin/egs/tokenprojection/s1/experiments/tokenprojection/acoustic_model/data/label_state_align'
out_filename = '/afs/inf.ed.ac.uk/user/s17/s1785140/mscproject/projection_weights_backup/tokenprojection/acoustic_model/proj_INFERENCE_epoch_24'

# create class that can generate datasets from our files
class TransformDataset(Dataset):
    '''
    in_filename: list of input features. usually a lab file from htk with emotio labels and utt_id
    out_filename: projection weights matrix file
    train_or_test: get the training set or the test set
    flip: whether to flip around input and targets
    '''
    def __init__(self, in_filename, out_filename, train_or_test, flip=False):
        #read in whole list of files inside in_filename
        paths = glob(os.path.join(in_filename, '*'))

        #only keep paths that are from AVEC2012 and thus have emotion ids
        paths = [p for p in paths if 'sent' in p]

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
            avg_a = sum(all_a) / len(lines)
            avg_e = sum(all_e) / len(lines)
            avg_p = sum(all_p) / len(lines)
            avg_v = sum(all_v) / len(lines)

            # print('utt_id', utt_id)

            emot_dict[int(utt_id)] = (avg_a, avg_e, avg_p, avg_v)

        self.datarows = []

        with open(out_filename) as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            #only get lines from the out_filename that were AVEC2012, i.e. those that are in emot_dict
            if i in emot_dict:
                emotions = torch.tensor(emot_dict[i], dtype=torch.float)
                controlvector = torch.tensor([float(string) for string in line.split()])
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
trainset = TransformDataset(in_filename, out_filename, 'train', flip=FLIP)
testset = TransformDataset(in_filename, out_filename, 'test', flip=FLIP)

trainloader = torch.utils.data.DataLoader(trainset, batch_size=2,
                                          shuffle=False, num_workers=2)
testloader = torch.utils.data.DataLoader(testset, batch_size=2,
                                         shuffle=False, num_workers=2)

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
        self.dropout = nn.Dropout(p=0.2)
        self.hlayers = hlayers

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        for i in range(self.hlayers):
            x = F.relu(self.fc2(x))
            x = self.dropout(x)
        x = self.fc3(x)
        return x

net = Net(hdims=50, hlayers=5, flip=FLIP)
print(net)

'''
define loss and optimiser
'''
criterion = nn.MSELoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

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
        if i % 10 == 9:    # print every 10 mini-batches
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i + 1, running_loss / 10))
            running_loss = 0.0

print('Finished Training')

'''
test the model
'''
print('Testing the model')
net.eval() #need this so that dropout isn't applied during forward passes
with torch.no_grad():
    print('Number of mini-batches in testdata', len(testloader))
    for data in testloader:
        inputs, targets = data
        outputs = net(inputs)
        loss = criterion(outputs, targets)
        print(loss.item())
