#
# Copyright (c) 2018 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#

def ck_preprocess(i):
    env = i['env']
    new_env = {}
    files_to_push = []
    if i['target_os_dict'].get('remote','') == 'yes' and env.get('CK_PUSH_LIBS_TO_REMOTE', 'yes').lower() == 'yes':
        lib_dir = i['deps']['library']['dict']['env'].get('CK_ENV_LIB_ARMCL')
        lib_name = i['deps']['library']['dict']['env'].get('CK_ENV_LIB_ARMCL_DYNAMIC_CORE_NAME')
        new_env['CK_ENV_ARMCL_CORE_LIB_PATH'] = os.path.join(lib_dir, 'lib', lib_name)
        files_to_push.append("$<<CK_ENV_ARMCL_CORE_LIB_PATH>>$")
        files_to_push.append("$<<CK_ENV_LIB_STDCPP_DYNAMIC>>$")

    return {'return': 0, 'new_env': new_env, 'run_input_files': files_to_push}

