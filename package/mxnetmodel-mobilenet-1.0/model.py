#!/usr/bin/python

#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

import os

import mxnet as mx
from mxnet import gluon
from mxnet.gluon.model_zoo.vision import get_model
from mxnet.gluon.utils import download

pi=os.environ['INSTALL_DIR']

print ('')
print ('Downloading model to '+pi+' ...')
print ('')

model_block = mx.gluon.model_zoo.vision.get_mobilenet(multiplier=1.0, pretrained=True, root=pi)
