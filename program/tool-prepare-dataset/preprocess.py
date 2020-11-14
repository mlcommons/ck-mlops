#! /usr/bin/env python

#
# Copyright (c) 2018 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#

import os


def ck_preprocess(i):
  ck = i['ck_kernel']

  dataset_uoa = i['env'].get('CK_DATASET', '')

  res = ck.access({'action': 'search',
                   'module_uoa': 'dataset',
                   'data_uoa': dataset_uoa,
                   'tags': 'nntest'})
  if res['return'] > 0:
    return res

  selected_dataset = None

  datasets = res['lst']
  if len(datasets) > 0:
    if len(datasets) == 1:
      selected_dataset = datasets[0]
    else:
      ck.out('')
      ck.out('More than one dataset entry is found for this program:')
      ck.out('')

      res = ck.access({'action': 'select_uoa',
                       'module_uoa': 'choice',
                       'choices': datasets})
      if res['return'] > 0:
        return res

      for d in datasets:
        if d['data_uid'] == res['choice']:
          selected_dataset = d
          break

  if not selected_dataset:
    return {'return': 1, 'error': 'No related datasets found'}

  os.environ['CK_NNTEST_DATASET_PATH'] = selected_dataset['path']

  return {'return': 0}
