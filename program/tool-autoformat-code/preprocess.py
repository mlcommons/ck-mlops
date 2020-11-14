#!/usr/bin/env python
#
# Copyright (c) 2018 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#


def ck_preprocess(i):
  ck = i['ck_kernel']
  env = i['env']

  prog_uoa = env.get('CK_PROGRAM')
  if not prog_uoa:
    return {'return': 0}

  res = ck.access({'action': 'search',
                   'module_uoa': 'program',
                   'data_uoa': prog_uoa})
  if res['return'] > 0:
    return res

  selected_prog = None

  progs = res['lst']
  if len(progs) > 0:
    if len(progs) == 1:
      selected_prog = progs[0]
    else:
      ck.out('\nMore than one program is found:\n')
      res = ck.access({'action': 'select_uoa',
                       'module_uoa': 'choice',
                       'choices': progs})
      if res['return'] > 0:
        return res

      for d in progs:
        if d['data_uid'] == res['choice']:
          selected_prog = d
          break

  if not selected_prog:
    ck.out('\nERROR: No such program: {}\n'.format(prog_uoa))
    return {'return': 1, 'error': 'Program not found'}

  env['CK_DIR'] = selected_prog['path']
  env['CK_PROGRAM'] = selected_prog['data_uoa']

  return {'return': 0, 'new_env': env}
