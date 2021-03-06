#!/usr/bin/env python2.7

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('--nepoch',type=int,default=20)
parser.add_argument('--version',type=int,default=4)
parser.add_argument('--trunc',type=int,default=4)
parser.add_argument('--limit',type=int,default=50)
parser.add_argument('--adv',type=str,default='categorical_cross_entropy')
parser.add_argument('--train_baseline',action='store_true')
args = parser.parse_args()

from subtlenet.models import particles as train
from os import path

train.NEPOCH = args.nepoch
train.VERSION = args.version
#train.OPTIMIZER = 'RMSprop'
data, dims = train.instantiate(args.trunc, args.limit)

clf_gen = train.setup_data(data)
adv_gen = train.setup_adv_data(data)

opts = {
        'loss' : args.adv,
        'scale' : 0.05,
        'w_clf' : 0.005,
        'w_adv' : 10,
        }

if args.adv == 'emd':
    opts['loss'] = train.emd
#    opts['w_adv'] = 500
#    opts['scale'] = 1

clf = train.build_classifier(dims)
if args.adv is not None:
    adv = train.build_adversary(clf=clf, **opts)

preload = '%s/%s/baseline_best.h5'%(train.MODELDIR, train._APOSTLE)
if path.isfile(preload):
    print 'Pre-loading weights from',preload
    tmp_ = train.load_model(preload)
    clf.set_weights(tmp_.get_weights())
if args.train_baseline or not(path.isfile(preload)):
    train.NEPOCH = 2
    train.train(clf, 'baseline', clf_gen['train'], clf_gen['validation'])
    train.NEPOCH = args.nepoch

if args.adv:
    print 'Training the full adversarial stack:'
    callback_params = {
            'partial_model' : clf,
            'monitor' : lambda x : opts['w_clf'] * x.get('val_y_hat_loss') - opts['w_adv'] * x.get('val_adv_loss'), # semi-arbitrary
            }
    train.train(adv, args.adv, adv_gen['train'], adv_gen['validation'], callback_params)
