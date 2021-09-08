#! /bin/bash

# Based on https://coral.ai/docs/accelerator/get-started/#pycoral-on-linux

git clone https://github.com/google-coral/pycoral.git

cd pycoral

bash examples/install_requirements.sh classify_image.py

${CK_ENV_COMPILER_PYTHON_FILE} examples/classify_image.py \
 --model test_data/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
 --labels test_data/inat_bird_labels.txt \
 --input test_data/parrot.jpg
