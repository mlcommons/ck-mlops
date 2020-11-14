# 
# Grigori Fursin took from http://blog.outcome.io/pytorch-quick-start-classifying-an-image
# and updated to support CK (http://cKnowledge.org/ai)
# Grigori Fursin later updated based on ReQuEST at ASPLOS'18 tournament
#

import io
import sys
import os
import requests
import numpy as np
from PIL import Image

from torchvision import models, transforms
from torch.autograd import Variable

LABELS_URL = 'https://s3.amazonaws.com/outcome-blog/imagenet/labels.json'

# returns list of pairs (prob, class_index)
def get_top5(all_probs):
  probs_with_classes = []
  for class_index in range(len(all_probs)):
    prob = all_probs[class_index]
    probs_with_classes.append((prob, class_index))
  sorted_probs = sorted(probs_with_classes, key = lambda pair: pair[0], reverse=True)
  return sorted_probs[0:5]

# Grigori added to connect with CK artifacts
fname = sys.argv[1]
fmodel = sys.argv[2]

if fmodel=='squeezenet-1.1':
   model=models.squeezenet1_1(pretrained=True)
else:
   print ('Model name is not recognized')
   exit(1)

normalize = transforms.Normalize(
   mean=[0.485, 0.456, 0.406],
   std=[0.229, 0.224, 0.225]
)
preprocess = transforms.Compose([
   transforms.Scale(256),
   transforms.CenterCrop(224),
   transforms.ToTensor(),
   normalize
])

img_pil = Image.open(os.path.join(fname))
if img_pil.mode!='RGB': img_pil=img_pil.convert('RGB')

img_tensor = preprocess(img_pil)
img_tensor.unsqueeze_(0)

img_variable = Variable(img_tensor)
fc_out = model(img_variable)

labels = {int(key):value for (key, value)
          in requests.get(LABELS_URL).json().items()}

prob = fc_out.data.numpy()

top1 = prob.argmax()

print ('')
print('PyTorch prediction Top1:', top1, labels[top1])

top5=[]
atop5 = get_top5(prob[0])

print ('')
print('PyTorch prediction Top5:')
for q in atop5:
    x=q[1]
    y=labels[x]
    top5.append(x)
    print (x,y)
