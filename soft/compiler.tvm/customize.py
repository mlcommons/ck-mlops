#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer(s):
#   * Grigori Fursin <grigori@octoml.ai>
#

import os

##############################################################################
# customize directories to automatically find and register software

def dirs(i):
    dirs=i.get('dirs', [])
    for d in extra_dirs:
        if os.path.isdir(d):
            dirs.append(d)
    return {'return':0, 'dirs':dirs}

##############################################################################
# parse software version

def version_cmd(i):

    fp=i.get('full_path','')

    ver_dir=os.path.dirname(os.path.dirname(fp))
    ver_file=os.path.join(ver_dir, 'version.py')

    ver = ''

    if os.path.isfile(ver_file):
        r=ck.load_text_file({'text_file':ver_file, 'split_to_list':'yes'})
        if r['return']>0: return r

        lst=r['lst']

        for l in lst:
            if '__version__' in l:
                 import re
                 vers=re.findall('"([^"]*)"', l)
                 ver=vers[0]

                 break

    return {'return':0, 'version':ver}


##############################################################################
# setup environment

def setup(i):

    s=''

    cus=i['customize']
    env=i['env']

    fp=cus.get('full_path','')

    ep=cus.get('env_prefix','')
    if ep!='' and fp!='':
       p1=os.path.dirname(fp)
       p2=os.path.dirname(p1)

       env[ep]=p2

       env['TVM_HOME']=p2
       env['PYTHONPATH'] = p2 + '/python:${PYTHONPATH}'

    return {'return':0, 'bat':s}
