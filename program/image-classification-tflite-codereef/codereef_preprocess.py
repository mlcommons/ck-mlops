#
# Copyright (c) 2018 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#

import os
import shutil

def ck_preprocess(i):

    cur_dir=os.getcwd()

    # Force clean input/output dirs (otherwise webcam processing is stuck)
    p1=os.path.join(cur_dir, 'input')
    if os.path.isdir(p1):
       ck.out('Cleaning directory: '+p1)
       shutil.rmtree(p1)
    os.makedirs(p1)

    p2=os.path.join(cur_dir, 'output')
    if os.path.isdir(p2):
       ck.out('Cleaning directory: '+p2)
       shutil.rmtree(p2)
    os.makedirs(p2)

    return {'return': 0}
