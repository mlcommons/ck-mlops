#!/bin/sh

# Collective Knowledge (program)
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developers:
# - Grigori Fursin, Grigori.Fursin@cTuning.org

export PYTHONPATH=${CK_ENV_DEMO_MVNC_YOLO}/py_examples:${PYTHONPATH}

python3 ${CK_ENV_DEMO_MVNC_YOLO}/py_examples/yolo_example.py $1

return 0
