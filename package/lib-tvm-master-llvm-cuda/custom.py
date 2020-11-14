#
# Collective Knowledge workflow framework
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

##############################################################################
# customize installation (via redirect)

def setup(i):
    ck=i['ck_kernel']

    return ck.access({'action':'run', 'module_uoa':'script',
                      'script_module_uoa':'package', 'data_uoa':'fdda38b07c848ec8',
                      'code':'custom', 'func':'setup',
                      'dict':i})
