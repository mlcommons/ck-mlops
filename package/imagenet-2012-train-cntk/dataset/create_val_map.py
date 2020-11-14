import os

labels = list()
images = list()

ground_truth=os.environ.get('CK_GROUND_TRUTH','')
if ground_truth=='': ground_truth='ILSVRC2012_validation_ground_truth.txt'

with open(ground_truth, 'r') as f:
	for line in f:
		labels.append(str(int(line) % 1000))

curdir = os.getcwd()

xdir=os.environ.get('CK_ENV_DATASET_IMAGENET_VAL','')
if xdir!='': curdir=xdir

filenames = os.listdir(curdir)
for filename in filenames:
	if (filename.endswith('.JPEG')):
		images.append(os.path.join(curdir, filename))

val_map=os.environ.get('CK_VAL_MAP','')
if val_map=='': val_map='../ImageNet_train/val_map.txt'

with open(val_map, 'w') as f:
	for i in range(len(images)):
		f.write(images[i] + '	' + labels[i] + '\n')

for img in images:
    print(' * '+img)

print(len(labels))
print(len(images))
