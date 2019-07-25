#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import os
import struct
import h5py
import encoder_init as encoder
import decoder_init as decoder
import time


# In[2]:


def write_hdf5(x,filename):
    with h5py.File(filename, 'w') as h:
        h.create_dataset('data', data=x, shape=x.shape)


# In[3]:


def show_data(x_in, pre_in):
    mean = np.mean(x_in)
    std = np.std(x_in)
    Max = np.max(x_in)
    Min = np.min(x_in)
    dtype = x_in.dtype

    print(pre_in + ' shape: ' + str(x_in.shape) + ' , type: ' + str(dtype) + ' , mean = ' + str(mean)
          + ' , std = ' + str(std) + ' , Max = ' + str(Max) + ' , Min = ' + str(Min))


# In[4]:


fname = '../H5_tmp/comp_3chan_10bit_floor.h5'
ftmp=h5py.File(fname,'r')
dt=ftmp['data'][:]
dt=dt.astype(np.int64)
show_data(dt, 'dt')


# In[5]:


for i in range(3):
    print('\nchannel %d'%(i))
    a = dt[:,:,i].flatten()
    show_data(a, 'a')
    
    start = time.clock()
    encoder.encode_data(a,'./TMP_files/encode_data.txt')
    end = time.clock()
    print('encode_run_time : ' + str(end-start))

    fsize = os.path.getsize('./TMP_files/encode_data.txt')
    print('fsize= ' + str(fsize))
    
    start = time.clock()
    ee = decoder.decode_data('./TMP_files/encode_data.txt','./TMP_files/decode_data.txt')
    end = time.clock()
    print('decode_run_time : ' + str(end-start))
    rec = np.array(ee)

    show_data(rec,'rec')

    mse = np.mean(np.square(rec-a))
    print('mse= ' + str(mse))

    ratio = float(fsize)/float(len(a))
    print('ratio= ' + str(ratio))


# ## Together

# In[6]:


# fname = '../H5_tmp/comp_3chan_10bit_floor.h5'
# ftmp=h5py.File(fname,'r')
# dt=ftmp['data'][:]
# dt=dt.astype(np.int64)
# show_data(dt, 'dt')
a = dt.flatten()
show_data(a, 'a')


# In[7]:


start = time.clock()
encoder.encode_data(a,'./TMP_files/encode_data.txt')
end = time.clock()
print('encode_run_time : ' + str(end-start))

fsize = os.path.getsize('./TMP_files/encode_data.txt')
print('fsize= ' + str(fsize))


# In[8]:


start = time.clock()
ee = decoder.decode_data('./TMP_files/encode_data.txt','./TMP_files/decode_data.txt')
end = time.clock()
print('decode_run_time : ' + str(end-start))
rec = np.array(ee)

show_data(rec,'rec')

mse = np.mean(np.square(rec-a))
print('mse= ' + str(mse))

ratio = float(fsize)/float(len(a))
print('ratio= ' + str(ratio))


# In[ ]:




