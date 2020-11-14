# 
# Grigori took from https://mxnet.incubator.apache.org/tutorials/python/predict_image.html
# and updated to support CK (http://cKnowledge.org/ai)
#

def get_image(fname, show=False):
    # download and show the image
    img = cv2.cvtColor(cv2.imread(fname), cv2.COLOR_BGR2RGB)

    if img is None:
         return None

    # convert into format (batch, RGB, width, height)
    img = cv2.resize(img, (224, 224))
    img = np.swapaxes(img, 0, 2)
    img = np.swapaxes(img, 1, 2)
    img = img[np.newaxis, :]

    return img

def predict(url):
    img = get_image(url, show=True)
    # compute the predict probabilities
    mod.forward(Batch([mx.nd.array(img)]))
    prob = mod.get_outputs()[0].asnumpy()
    # print the top-5
    prob = np.squeeze(prob)
    a = np.argsort(prob)[::-1]

    print ('')
    for i in a[0:5]:
        print('probability=%f, class=%s' %(prob[i], labels[i]))

#######################################################################
import mxnet as mx
import sys

# Grigori added to connect with CK artifacts
checkpoint = sys.argv[1]
labels = sys.argv[2]
fname = sys.argv[3]
gpu = (sys.argv[4]=='1')

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import cv2
import numpy as np

if gpu:
   target=mx.gpu()
else:
   target=mx.cpu()

sym, arg_params, aux_params = mx.model.load_checkpoint(checkpoint, 0)
mod = mx.mod.Module(symbol=sym, context=target, label_names=None)
mod.bind(for_training=False, data_shapes=[('data', (1,3,224,224))], 
         label_shapes=mod._label_shapes)
mod.set_params(arg_params, aux_params, allow_missing=True)
with open(labels, 'r') as f:
    labels = [l.rstrip() for l in f]

# define a simple data batch
from collections import namedtuple
Batch = namedtuple('Batch', ['data'])

predict(fname)
