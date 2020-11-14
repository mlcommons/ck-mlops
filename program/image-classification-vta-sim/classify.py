"""
ResNet Inference Example
========================
**Author**: `Thierry Moreau <https://homes.cs.washington.edu/~moreau/>`_

This tutorial provides an end-to-end demo, on how to run ResNet-18 inference
onto the VTA accelerator design to perform ImageNet classification tasks.

"""


######################################################################
# Import Libraries
# ----------------
# We start by importing the tvm, vta, nnvm libraries to run this example.

from __future__ import absolute_import, print_function

import os
import sys
import nnvm
import nnvm.compiler
import tvm
import vta
import vta.testing
import numpy as np
import json
import requests
import time

from nnvm.compiler import graph_attr
from tvm import rpc
from tvm.contrib import graph_runtime, util
from tvm.contrib.download import download
from vta.testing import simulator

from io import BytesIO
from matplotlib import pyplot as plt
from PIL import Image

# Load VTA parameters from the config.json file
env = vta.get_env()

# Helper to crop an image to a square (224, 224)
# Takes in an Image object, returns an Image object
def thumbnailify(image, pad=15):
    w, h = image.size
    crop = ((w-h)//2+pad, pad, h+(w-h)//2-pad, h-pad)
    image = image.crop(crop)
    image = image.resize((224, 224))
    return image

# Helper function to read in image
# Takes in Image object, returns an ND array
def process_image(image):
    # Convert to neural network input format
    image = np.array(image) - np.array([123., 117., 104.])
    image /= np.array([58.395, 57.12, 57.375])
    image = image.transpose((2, 0, 1))
    image = image[np.newaxis, :]

    return tvm.nd.array(image.astype("float32"))

# Classification helper function
# Takes in the graph runtime, and an image, and returns top result and time
def classify(m, image):
    m.set_input('data', image)
    timer = m.module.time_evaluator("run", ctx, number=1)
    tcost = timer()
    tvm_output = m.get_output(0, tvm.nd.empty((1000,), "float32", remote.cpu(0)))
    top = np.argmax(tvm_output.asnumpy())
    tcost = "t={0:.2f}s".format(tcost.mean)
    return tcost + " {}".format(synset[top])

# Helper function to compile the NNVM graph
# Takes in a path to a graph file, params file, and device target
# Returns the NNVM graph object, a compiled library object, and the params dict
def generate_graph(graph_fn, params_fn, device="vta"):

    # Measure build start time
    build_start = time.time()

    # Derive the TVM target
    target = tvm.target.create("llvm -device={}".format(device))

    # Derive the LLVM compiler flags
    # When targetting the Pynq, cross-compile to ARMv7 ISA
    if env.TARGET == "sim":
        target_host = "llvm"
    elif env.TARGET == "pynq":
        target_host = "llvm -mtriple=armv7-none-linux-gnueabihf -mcpu=cortex-a9 -mattr=+neon"

    # Load the ResNet-18 graph and parameters
    sym = nnvm.graph.load_json(open(graph_fn).read())
    params = nnvm.compiler.load_param_dict(open(params_fn, 'rb').read())

    # Populate the shape and data type dictionary
    shape_dict = {"data": (1, 3, 224, 224)}
    dtype_dict = {"data": 'float32'}
    shape_dict.update({k: v.shape for k, v in params.items()})
    dtype_dict.update({k: str(v.dtype) for k, v in params.items()})

    # Create NNVM graph
    graph = nnvm.graph.create(sym)
    graph_attr.set_shape_inputs(sym, shape_dict)
    graph_attr.set_dtype_inputs(sym, dtype_dict)
    graph = graph.apply("InferShape").apply("InferType")

    # Apply NNVM graph optimization passes
    sym = vta.graph.clean_cast(sym)
    sym = vta.graph.clean_conv_fuse(sym)
    if target.device_name == "vta":
        assert env.BLOCK_IN == env.BLOCK_OUT
        sym = vta.graph.pack(sym, shape_dict, env.BATCH, env.BLOCK_OUT)

    # Compile NNVM graph
    with nnvm.compiler.build_config(opt_level=3):
        if target.device_name != "vta":
            graph, lib, params = nnvm.compiler.build(
                sym, target, shape_dict, dtype_dict,
                params=params, target_host=target_host)
        else:
            with vta.build_config():
                graph, lib, params = nnvm.compiler.build(
                    sym, target, shape_dict, dtype_dict,
                    params=params, target_host=target_host)

    # Save the compiled inference graph library
    assert tvm.module.enabled("rpc")
    temp = util.tempdir()
    lib.save(temp.relpath("graphlib.o"))

    # Send the inference library over to the remote RPC server
    remote.upload(temp.relpath("graphlib.o"))
    lib = remote.load_module("graphlib.o")

    # Measure build time
    build_time = time.time() - build_start
    print("ResNet-18 inference graph built in {0:.2f}s!".format(build_time))

    return graph, lib, params

# Grigori added extensions for CK and ReQuEST
# returns list of pairs (prob, class_index)
def get_top5(all_probs):
  probs_with_classes = []
  for class_index in range(len(all_probs)):
    prob = all_probs[class_index]
    probs_with_classes.append((prob, class_index))
  sorted_probs = sorted(probs_with_classes, key = lambda pair: pair[0], reverse=True)
  return sorted_probs[0:5]

STAT_REPEAT=os.environ.get('STAT_REPEAT','')
if STAT_REPEAT=='' or STAT_REPEAT==None:
   STAT_REPEAT=10
STAT_REPEAT=int(STAT_REPEAT)

# get file to classify from CMD (or check all images from ImageNet is empty)
files=[]
argv=sys.argv

val={}
if len(argv)>1:
   files=[argv[1]]
else:
   ipath=os.environ.get('CK_ENV_DATASET_IMAGENET_VAL','')
   if ipath=='':
      print ('Error: path to ImageNet dataset is not set!')
      exit(1)
   if not os.path.isdir(ipath):
      print ('Error: path to ImageNet dataset was not found!')
      exit(1)

   # get all files
   d=os.listdir(ipath)
   for x in d:
       x1=x.lower()
       if x1.startswith('ilsvrc2012_val_'):
          files.append(os.path.join(ipath,x))

   files=sorted(files)

   STAT_REPEAT=1

   # Get correct labels
   ival=os.environ.get('CK_CAFFE_IMAGENET_VAL_TXT','')
   fval=open(ival).read().split('\n')

   val={}
   for x in fval:
       x=x.strip()
       if x!='':
          y=x.split(' ')
          val[y[0]]=int(y[1])

show_images=(os.environ.get('SHOW_IMAGE','').lower()=='on')

# FGG: set timers
import time
timers={}

# FGG: set model files via CK env
VTAMODEL_LABELS_FILE = os.environ['CK_ENV_MODEL_VTA_MODEL_LABELS_FULL'] # 'synset.txt'
VTAMODEL_GRAPH_FILE = os.environ['CK_ENV_MODEL_VTA_MODEL_FULL'] # 'resnet18_qt8.json'
VTAMODEL_PARAMS_FILE = os.environ['CK_ENV_MODEL_VTA_MODEL_WEIGHTS_FULL'] # 'resnet18_qt8.params'

# Read in ImageNet Categories
synset = eval(open(os.path.join(VTAMODEL_LABELS_FILE)).read())

######################################################################
# Setup the Pynq Board's RPC Server
# ---------------------------------
# Build the RPC server's VTA runtime and program the Pynq FPGA.

# Measure build start time
reconfig_start = time.time()

# We read the Pynq RPC host IP address and port number from the OS environment
host = os.environ.get('CK_MACHINE_HOST','')
if host=='':
   host = os.environ.get("VTA_PYNQ_RPC_HOST", "192.168.2.99")

port = os.environ.get('CK_MACHINE_PORT','')
if port=='':
   port = os.environ.get("VTA_PYNQ_RPC_PORT", "9091")
port=int(port)

# We configure both the bitstream and the runtime system on the Pynq
# to match the VTA configuration specified by the config.json file.
if env.TARGET == "pynq":

    # try init
    if os.environ.get('INIT_PYNQ','').lower()=='yes':
       print ('')
       print ('Initializing board ...')

       from tvm import rpc
       from vta import get_bitstream_path, download_bitstream, program_fpga, reconfig_runtime

       assert tvm.module.enabled("rpc")
       remote = rpc.connect(host, port)
       program_fpga(remote, None) # None -> path
#       remote = rpc.connect(host, port)
       reconfig_runtime(remote)

       print ('')

    # Make sure that TVM was compiled with RPC=1
    assert tvm.module.enabled("rpc")
    remote = rpc.connect(host, port)

    dt=time.time()

    # Reconfigure the JIT runtime
    vta.reconfig_runtime(remote)

    # Program the FPGA with a pre-compiled VTA bitstream.
    # You can program the FPGA with your own custom bitstream
    # by passing the path to the bitstream file instead of None.
    vta.program_fpga(remote, bitstream=None)

    timers['execution_time_prepare_fpga']=time.time()-dt

    # Report on reconfiguration time
    reconfig_time = time.time() - reconfig_start
    print("Reconfigured FPGA and RPC runtime in {0:.2f}s!".format(reconfig_time))

# In simulation mode, host the RPC server locally.
elif env.TARGET == "sim":
    remote = rpc.LocalSession()


######################################################################
# Build the ResNet Runtime
# ------------------------
# Build the ResNet graph runtime, and configure the parameters.

# Set ``device=cpu`` to run inference on the CPU,
# or ``device=vtacpu`` to run inference on the FPGA.
device = "vta"

# Device context
ctx = remote.ext_dev(0) if device == "vta" else remote.cpu(0)

# Build the graph runtime
dt=time.time()
graph, lib, params = generate_graph(VTAMODEL_GRAPH_FILE,
                                    VTAMODEL_PARAMS_FILE,
                                    device)
timers['execution_time_prepare_graph']=time.time()-dt

dt=time.time()
m = graph_runtime.create(graph, lib, ctx)
timers['execution_time_create_run_time_graph']=(time.time()-dt)

# Set the parameters
m.set_input(**params)


######################################################################
# Run ResNet-18 inference on a sample image
# -----------------------------------------
# Perform image classification on test image.
# You can change the test image URL to any image of your choosing.

total_images=0
correct_images_top1=0
correct_images_top5=0

# Shuffle files and pre-read JSON with accuracy to continue aggregating it
# otherwise if FPGA board hangs, we can continue checking random images ...

import random
random.shuffle(files)

if len(files)>1 and os.path.isfile('aggregate-ck-timer.json'):
   x=json.load(open('aggregate-ck-timer.json'))

   if 'total_images' in x:
      total_images=x['total_images']
   if 'correct_images_top1' in x:
      correct_images_top1=x['correct_images_top1']
   if 'correct_images_top5' in x:
      correct_images_top5=x['correct_images_top5']

dt1=time.time()
for f in files:
    total_images+=1

    print ('===============================================================================')
    print ('Image '+str(total_images)+' of '+str(len(files))+' : '+f)

    dt=time.time()
    image = Image.open(os.path.join(f)).resize((224, 224))
    if image.mode!='RGB': image=image.convert('RGB')
    if 'execution_time_load_image' not in timers:
       timers['execution_time_load_image']=time.time()-dt

    if show_images:
       plt.imshow(image)
       plt.show()

    # Set the input
    dt=time.time()
    image = process_image(image)
    if 'execution_time_transform_image' not in timers:
       timers['execution_time_transform_image']=time.time()-dt

    m.set_input('data', image)

    # Perform inference
    print ('')
    print ("run ("+str(STAT_REPEAT)+" statistical repetitions)")
    timer = m.module.time_evaluator("run", ctx, number=STAT_REPEAT)
    dt=time.time()
    tcost = timer()
    timers['execution_time_classify']=(time.time()-dt)/STAT_REPEAT

    # Get classification results
    tvm_output = m.get_output(0, tvm.nd.empty((1000,), "float32", remote.cpu(0)))

#    top_categories = np.argsort(tvm_output.asnumpy())
#
#    # Report top-5 classification results
#    print("ResNet-18 Prediction #1:", synset[top_categories[-1]])
#    print("                     #2:", synset[top_categories[-2]])
#    print("                     #3:", synset[top_categories[-3]])
#    print("                     #4:", synset[top_categories[-4]])
#    print("                     #5:", synset[top_categories[-5]])
#    print("Performed inference in {0:.2f}s".format(tcost.mean))

    top1 = np.argmax(tvm_output.asnumpy())

    top5=[]
    atop5 = get_top5(tvm_output.asnumpy())

    print ('')
    print('TVM prediction Top1:', top1, synset[top1])

    print ('')
    print('TVM prediction Top5:')
    for q in atop5:
        x=q[1]
        y=synset[x]
        top5.append(x)
        print (x,y)

    print ('')
    print("Internal T-cost: %g" % tcost.mean)

    # Check correctness if available
    if len(val)>0:
       top=val[os.path.basename(f)]

       correct_top1=False
       if top==top1:
          correct_top1=True
          correct_images_top1+=1

       print ('')
       if correct_top1:
          print ('Current prediction Top1: CORRECT')
       else:
          print ('Current prediction Top1: INCORRECT +('+str(top)+')')

       accuracy_top1=float(correct_images_top1)/float(total_images)
       print ('Current accuracy Top1:   '+('%.5f'%accuracy_top1))

       correct_top5=False
       if top in top5:
          correct_top5=True
          correct_images_top5+=1

       print ('')
       if correct_top5:
          print ('Current prediction Top5: CORRECT')
       else:
          print ('Current prediction Top5: INCORRECT +('+str(top)+')')

       accuracy_top5=float(correct_images_top5)/float(total_images)
       print ('Current accuracy Top5:   '+('%.5f'%accuracy_top5))

       print ('')
       print ('Total elapsed time: '+('%.1f'%(time.time()-dt1))+' sec.')

       timers['total_images']=total_images
       timers['correct_images_top1']=correct_images_top1
       timers['accuracy_top1']=accuracy_top1
       timers['correct_images_top5']=correct_images_top5
       timers['accuracy_top5']=accuracy_top5

    timers['execution_time_classify_internal']=tcost.mean
    timers['execution_time']=tcost.mean

    with open ('tmp-ck-timer.json', 'w') as ftimers:
         json.dump(timers, ftimers, indent=2)

    with open ('aggregate-ck-timer.json', 'w') as ftimers:
         json.dump(timers, ftimers, indent=2)

    sys.stdout.flush()
