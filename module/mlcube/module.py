#
# Collective Knowledge (CK front-end for MLCube(tm))
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
import json

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
# configure MLCube instance

def configure(i):
    """
    Input:  {
              data_uoa - MLCube instance
              (target) - Target platform
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    duoa=i.get('data_uoa','')
    if duoa=='':
        return {'return':1, 'error':'MLCube instance is not specified'}

    # Load instance meta
    r=ck.access({'action':'load',
                 'module_uoa':work['self_module_uid'],
                 'data_uoa':duoa})
    if r['return']>0: return r

    mlcube_meta=r['dict']

    print ('')
    ck.out('MLCube instance meta:')

    print ('')
    print (json.dumps(mlcube_meta, indent=2))

    # Check target
    target_meta={}

    target=i.get('target','')
    if target!='':
       # Load instance meta
       r=ck.access({'action':'load',
                    'module_uoa':'target',
                    'data_uoa':target})
       if r['return']>0: return r

       target_meta=r['dict']

       print ('')
       ck.out('Target meta:')

       print ('')
       print (json.dumps(target_meta, indent=2))


    print ('')
    print ('TBD')


    return {'return':0}

##############################################################################
# run MLCube instance

def run(i):
    """
    Input:  {
              data_uoa - MLCube instance
              (target) - Target platform
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    duoa=i.get('data_uoa','')
    if duoa=='':
        return {'return':1, 'error':'MLCube instance is not specified'}

    # Load instance meta
    r=ck.access({'action':'load',
                 'module_uoa':work['self_module_uid'],
                 'data_uoa':duoa})
    if r['return']>0: return r

    mlcube_meta=r['dict']

    print ('')
    ck.out('MLCube instance meta:')

    print ('')
    print (json.dumps(mlcube_meta, indent=2))

    # Check target
    target_meta={}

    target=i.get('target','')
    if target!='':
       # Load instance meta
       r=ck.access({'action':'load',
                    'module_uoa':'target',
                    'data_uoa':target})
       if r['return']>0: return r

       target_meta=r['dict']

       print ('')
       ck.out('Target meta:')

       print ('')
       print (json.dumps(target_meta, indent=2))


    print ('')
    print ('TBD')


    return {'return':0}
