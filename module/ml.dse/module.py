#
# Collective Knowledge (AI/ML/SW/HW Design Space Exploration API)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
##
# Developer: Grigori Fursin, https://fursin.net
#

cfg = {}  # Will be updated by CK (meta description of this module)
work = {}  # Will be updated by CK (temporal data)
ck = None  # Will be updated by CK (initialized CK kernel)

# Local settings

#import sys
#import os
#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#from ck_b5b8e2fd8894784a import ...

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

##############################################################################
# prepare DSE engine based on CK workflows

def prepare(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    ck.out('prepare DSE engine based on CK workflows')

    ck.out('')
    ck.out('Command line: ')
    ck.out('')

    import json
    cmd=json.dumps(i, indent=2)

    ck.out(cmd)

    return {'return':0}

##############################################################################
# run DSE

def run(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    ck.out('run DSE')

    ck.out('')
    ck.out('Command line: ')
    ck.out('')

    import json
    cmd=json.dumps(i, indent=2)

    ck.out(cmd)

    return {'return':0}
