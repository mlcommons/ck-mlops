#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, https://fursin.net
#

import os

##############################################################################
# setup environment setup

def process(i):

    cus=i.get('customize',{})
    install_env = cus.get('install_env', {})

    fp=cus.get('full_path','')
    install_root    = os.path.dirname(fp)

    env={}

    ep=cus['env_prefix']

    # Provide the installation root where all files live:
    env[ep + '_ROOT'] = install_root

    # Set universal names
    env['ML_MODEL_ROOT'] = install_root

    model_path=fp
    model_file=os.path.basename(fp)
    model_root=os.path.dirname(fp)

    if model_file=='dummy' or not os.path.isfile(fp):
       # When variations, the name can be different.
       # Then try to detect from PACKAGE_NAME
       model_file=install_env['PACKAGE_NAME']
       model_path=os.path.join(model_root, model_file)

    env['ML_MODEL_FILENAME'] = model_file
    env['ML_MODEL_FILEPATH'] = model_path

    # Init common variables, they are set for all models:
    #
    # This group should end with _FILE prefix e.g. TFLITE_FILE
    # This suffix will be cut off and prefixed by cus['env_prefix']
    # so we'll get vars like CK_ENV_TENSORFLOW_MODEL_TFLITE
    for varname in install_env.keys():
        if varname.endswith('_FILE'):
            env[ep + '_' + varname[:-len('_FILE')]] = os.path.join(install_root, install_env[varname])

    # Init model-specific variables:
    #
    # This other group should be started with MODEL_ prefix e.g. MODEL_MOBILENET_RESOLUTION
    # This prefix will be cut off as it already contained in cus['env_prefix']
    # so we'll get vars like CK_ENV_TENSORFLOW_MODEL_MOBILENET_RESOLUTION
    for varname in install_env.keys():
        if varname.startswith('MODEL_'):
            env[ep+varname[len('MODEL'):]] = install_env[varname]

    # Just copy those without any change in the name:
    #
    for varname in install_env.keys():
        if varname.startswith('ML'):
            env[varname] = install_env[varname]

    return {'return':0, 'env':env}
