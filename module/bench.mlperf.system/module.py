#
# Collective Knowledge (MLPerf benchmark system (SUT))
#
# 
# 
##
# Developer: 
#

cfg = {}  # Will be updated by CK (meta description of this module)
work = {}  # Will be updated by CK (temporal data)
ck = None  # Will be updated by CK (initialized CK kernel)

# Local settings

#import sys
#import os
#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#from ck_4edfa6cce73e7297 import ...

##############################################################################
# Initialize module


def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return': 0}
