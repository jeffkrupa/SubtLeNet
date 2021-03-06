#!/usr/local/bin/python2.7


from sys import exit 
from os import environ, system
environ['KERAS_BACKEND'] = 'tensorflow'
environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID" 
environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np

from keras.models import Model, load_model 
from subtlenet import config 
config.gen_default_variables=['tau3','tau2']
config.gen_default_mus=[0.5,0.5]
config.gen_default_sigmas=[0.5,0.5]

from subtlenet.generators.gen_singletons import make_coll


shallow = load_model('shallow_models/shallow_tau32.h5')

basedir = '/fastscratch/snarayan/genarrays/v_deepgen_3/'
system('rm %s/test/*shallow.npy'%basedir)
coll = make_coll(basedir + '/PARTITION/*_CATEGORY.npy')

def predict_t(data):
    inputs = data['singletons'][:,[config.gen_singletons[x] for x in config.gen_default_variables]]
    if inputs.shape[0] > 0:
        mus = np.array(config.gen_default_mus)
        sigmas = np.array(config.gen_default_sigmas)
        inputs -= mus 
        inputs /= sigmas 
        r_shallow_t = shallow.predict(inputs)[:,config.n_truth-1]
    else:
        r_shallow_t = np.empty((0,))

    return r_shallow_t 

coll.infer(['singletons'], f=predict_t, name='t32', partition='test')
