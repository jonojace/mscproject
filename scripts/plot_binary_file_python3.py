#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Oliver Watts
# owatts@inf.ed.ac.uk
# April 2016

import sys, os
import struct
import numpy as np
from argparse import ArgumentParser

try:
    from pylab import subplot, plot, show, imshow, gray, ylim
except:
    print('Trouble importing matplotlib functions -- will not try to plot anything')




def main_work():

    #################################################

    # ======== Get stuff from command line ==========

    def usage():
        print("Usage: python ./plot_matrix.py <BINARY_FILE_NAME> <DIMENSION>")
        sys.exit(1)


    try:
        param_file = sys.argv[1]
 #       param_file2 = sys.argv[2]
        dim = int(sys.argv[2])

    # try:
    #     dim = int(sys.argv[1])
    #     param_files = sys.argv[2:]


    except:
        usage()

    #################################################
    #probe_dim(param_file, 100000, remove_htk_header=False, double_precision=False)
    #sys.exit('sdv')


    # for param_file in param_files:
    #     data = get_speech(param_file, dim, remove_htk_header=False, double_precision=False)
    #     ene = data[:,0]
    #     plot(ene)
    # show()
    # sys.exit('acadv')


    data = get_speech(param_file, dim, remove_htk_header=False, double_precision=False)

    #data = np.clip(data, -50,50)

#    data2 = get_speech(param_file2, dim, remove_htk_header=False, double_precision=True)
    print(data.shape)
    #sys.exit('stop here 8887808392849028907')
    #data = data[:,0]


    #data = data - data.mean(axis=0)

#     data = data[:,783:810]
    plot(data) #  data[:,437:511])
    #plot( data[:,:1])
    print(data)
    show()
    # print( data
    # print( data[0,437:511]



#    print( np.exp(data)


    sys.exit('bsfbsfb')

#    plot(np.transpose(np.sqrt(data)))

    '''
    data = data[900:1000,:]

    plot(data[:,-9:])
    ylim(-1, 1)
    show()
    print( data.shape
    '''
    diff_data = data - data2
    plot(diff_data)
    show()

    sys.exit('stop here 888787')
    print(data.shape)
#    np.savetxt('/tmp/world.txt', data[:,0])

    #
#     print( np.sum(data, axis=1)
#     print( np.max(data, axis=1)
#     plot(np.max(data, axis=1))
#     show()
#    sys.exit('stop here....')

    imshow(np.transpose(data), interpolation='nearest')
    gray()
    show()

    ## print( data as text:
    for row in data:
        print('\t'.join([str(value) for value in row]))


def probe_dim(infile, maxdim, remove_htk_header=False, double_precision=False):

    if double_precision:
        data = read_doubles(infile)
    else:
        data = read_floats(infile)
    if remove_htk_header:
        data = data[3:]  ## 3 floats correspond to 12 byte htk header
    #print( dim
    #print( len(data)
    #print( len(data) / float(dim)
    L = len(data)
    for i in xrange(1, maxdim+1):
        if L % i == 0:
            print(i)



def get_speech(infile, dim, remove_htk_header=False, double_precision=False):

    if double_precision:
        data = read_doubles(infile)
    else:
        data = read_floats(infile)
    if remove_htk_header:
        data = data[3:]  ## 3 floats correspond to 12 byte htk header
    #print( dim
    #print( len(data)
    #print( len(data) / float(dim)
    assert len(data) % float(dim) == 0,"Bad dimension!"
    m = len(data) / dim
    data = np.array(data).reshape((m,dim))
    return data



def read_floats(infile):
    f = open(infile, "r")
    l = os.stat(infile)[6]  # length in bytes
    data = f.read(l)        # = read until bytes run out (l)
    f.close()

    m = l / 4
    format = str(m)+"f"

    unpacked = struct.unpack(format, data)
    unpacked = list(unpacked)
    return unpacked

def read_doubles(infile):
    f = open(infile, "r")
    l = os.stat(infile)[6]  # length in bytes
    data = f.read(l)        # = read until bytes run out (l)
    f.close()

    m = l / 8
    format = str(m)+"d"

    unpacked = struct.unpack(format, data)
    unpacked = list(unpacked)
    return unpacked


if __name__=="__main__":

    main_work()
