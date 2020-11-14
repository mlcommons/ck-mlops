#
# CK configuration script for CNTK package
#
# Developer(s): 
#  * Grigori Fursin, dividiti/cTuning foundation
#

import os
import sys
import json

##############################################################################
# customize installation

def setup(i):
    # Reuse custom from master entry

    ck=i['ck_kernel']

    return ck.access({'action':'run',
                      'module_uoa':'script',
                      'script_module_uoa':'package',
                      'data_uoa':'cc81d4c8da7a472e', # lib-cntk-2.2-cpu
                      'code':'custom',
                      'func':'setup',
                      'dict':i})
