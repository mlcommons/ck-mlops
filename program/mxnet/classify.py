# 
# Grigori Fursin took from https://mxnet.incubator.apache.org/tutorials/python/predict_image.html
# and updated to support CK (http://cKnowledge.org/ai)
# Grigori Fursin later updated based on ReQuEST at ASPLOS'18 tournament
#

import mxnet as mx
import numpy as np

import sys
import os
import json
from PIL import Image

def transform_image(image):
    image = np.array(image) - np.array([123., 117., 104.])
    image /= np.array([58.395, 57.12, 57.375])
    image = image.transpose((2, 0, 1))
    image = image[np.newaxis, :]
    return image

# returns list of pairs (prob, class_index)
def get_top5(all_probs):
  probs_with_classes = []
  for class_index in range(len(all_probs)):
    prob = all_probs[class_index]
    probs_with_classes.append((prob, class_index))
  sorted_probs = sorted(probs_with_classes, key = lambda pair: pair[0], reverse=True)
  return sorted_probs[0:5]

######################################################################
# Convert Gluon Block to MXNet Symbol
# See https://github.com/apache/incubator-mxnet/issues/9374
######################################################################
def block2symbol(block):
    data = mx.sym.Variable('data')
    sym = block(data)
    args = {}
    auxs = {}
    for k, v in block.collect_params().items():
        args[k] = mx.nd.array(v.data().asnumpy())
        auxs[k] = mx.nd.array(v.data().asnumpy())
    return sym, args, auxs

# Grigori added to connect with CK artifacts
fname = sys.argv[1]

gpu = (sys.argv[2]=='1')

if gpu:
   target=mx.gpu()
else:
   target=mx.cpu()

batch_size=1

# FGG: set model files via CK env
CATEG_FILE = '../synset.txt'
synset = eval(open(os.path.join(CATEG_FILE)).read())

image = Image.open(os.path.join(fname)).resize((224, 224))
if image.mode!='RGB': image=image.convert('RGB')

img = transform_image(image)

from mxnet.gluon.model_zoo.vision import get_model
from mxnet.gluon.utils import download

model_path=os.environ['CK_ENV_MODEL_MXNET']
model_id=os.environ['MXNET_MODEL_ID']

block = get_model(model_id, pretrained=True, root=model_path)

sym, arg_params, aux_params = block2symbol(block)

sym = mx.sym.SoftmaxOutput(data=sym, name='softmax')

mod = mx.mod.Module(symbol=sym, context=target, label_names = ['softmax_label'])

eval_iter = mx.io.NDArrayIter(img, np.array([0.0]), batch_size, shuffle=False)

mod.bind(data_shapes = eval_iter.provide_data, label_shapes = eval_iter.provide_label)

mod.set_params(arg_params, aux_params)

from collections import namedtuple
Batch = namedtuple('Batch', ['data'])

# set inputs
eval_iter = mx.io.NDArrayIter(img, np.array([0.0]), batch_size, shuffle=False)

prob = mod.predict(eval_iter)

top1 = np.argmax(prob.asnumpy())

print ('')
print('MXNet prediction Top1:', top1, synset[top1])

top5=[]
atop5 = get_top5(prob.asnumpy()[0])

print ('')
print('MXNet prediction Top5:')
for q in atop5:
    x=q[1]
    y=synset[x]
    top5.append(x)
    print (x,y)
