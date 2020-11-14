#!/usr/bin/env python
#
# Copyright (c) 2017-2018 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#
# Reads shape data from CSV file and creates a list of respective dataset files
#

import ck.kernel as ck
import csv
import json
import os
from collections import OrderedDict

########################################################################


def prepare_avgpool(row):
  net = row[0].replace(' ', '-')
  c, h, w = [int(x) for x in row[1].replace(' ', '').split('x')]
  kernel = int(row[5])
  stride = int(row[6])
  layer = row[8]
  pad = 0         # no padding for now
  pad_scheme = 2  # VALID pad scheme for now

  name = '-'.join(map(str, ['shape', c, h, w, kernel, stride]))

  instr = 'x'.join(map(str, [w, h, c]))
  desc = ' '.join(map(str, [net, layer, 'input', instr, 'kernel', kernel, 'stride', stride]))

  data = OrderedDict([
      ('CK_IN_SHAPE_C', c),
      ('CK_IN_SHAPE_H', h),
      ('CK_IN_SHAPE_W', w),
      ('CK_POOL_KERNEL', kernel),
      ('CK_POOL_STRIDE', stride),
      ('CK_POOL_PAD', pad),
      ('CK_POOL_PAD_SCHEME', pad_scheme)
  ])

  return name, desc, data

########################################################################


def prepare_conv(row):
  net = row[0]
  w = int(row[1])
  h = int(row[2])
  c_in = int(row[3])
  k = int(row[4])
  c_out = int(row[5])
  stride = int(row[6])
  pad = int(row[7])
  layer = row[9]

  name = 'shape-' + '-'.join(map(str, [c_in, h, w, k, c_out, stride, pad]))

  instr = 'x'.join(map(str, [w, h, c_in]))
  filterstr = 'x'.join(map(str, [k, k, c_out]))
  desc = ' '.join(map(str, [net, layer, 'input', instr, 'filter', filterstr, 'stride', stride, 'pad', pad]))

  data = OrderedDict([
      ('CK_IN_SHAPE_C', c_in),
      ('CK_IN_SHAPE_H', h),
      ('CK_IN_SHAPE_W', w),
      ('CK_OUT_SHAPE_C', c_out),
      ('CK_CONV_KERNEL', k),
      ('CK_CONV_STRIDE', stride),
      ('CK_CONV_PAD', pad)
  ])
  return name, desc, data

########################################################################


def prepare_depthwiseconv(row):
  net = row[0]
  w = int(row[1])
  h = int(row[2])
  c = int(row[3])
  stride = int(row[4])
  pad = int(row[5])
  layer = row[7]

  name = 'shape-' + str(c) + '-' + str(h) + '-' + str(w) + '-' + str(stride) + '-' + str(pad)

  instr = 'x'.join(map(str, [w, h, c]))
  desc = ' '.join(map(str, [net, layer, 'input', instr, 'stride', stride, 'pad', pad]))

  data = OrderedDict([
      ('CK_IN_SHAPE_C', c),
      ('CK_IN_SHAPE_H', h),
      ('CK_IN_SHAPE_W', w),
      ('CK_DEPTHWISE_STRIDE', stride),
      ('CK_DEPTHWISE_PAD', pad)
  ])

  return name, desc, data

########################################################################

# This variable is used to generate description of the dataset
# e.g. "Inception v3 fc1 input 1x1x2048 output 1x1x1000" (fullyconnected_net_name = 'Inception').
# All calls of `prepare_fullyconnected` will describe the created dataset with this name
# or will update this name when shifting to a section of shapes related to another network.
fullyconnected_net_name = None

def prepare_fullyconnected(row):
  global fullyconnected_net_name
  try:
    layer = row[0].strip()
    c = int(row[2])
    h, w = [int(x) for x in row[3].replace(' ', '').split('x')]
    c_out = int(row[4])
    h_out, w_out = [int(x) for x in row[5].replace(' ', '').split('x')]

    name = 'shape-' + '-'.join(map(str, [c, h, w, c_out, h_out, w_out]))

    instr = 'x'.join(map(str, [w, h, c]))
    outstr = 'x'.join(map(str, [w_out, h_out, c_out]))
    desc = ' '.join(map(str, [fullyconnected_net_name, layer, 'input', instr, 'output', outstr]))

    data = OrderedDict([
        ('CK_IN_SHAPE_C', c),
        ('CK_IN_SHAPE_H', h),
        ('CK_IN_SHAPE_W', w),
        ('CK_OUT_SHAPE_C', c_out),
        ('CK_OUT_SHAPE_H', h_out),
        ('CK_OUT_SHAPE_W', w_out)
    ])

    return name, desc, data

  except Exception as e:
    # If we can't parse the row then it's header row (e.g.: "Inception v3,,,,,,,")
    # and the layer name (parsed from the first column) gives a network name.
    # Store it in order to reuse during parsing of subsequent rows:
    if layer:
      fullyconnected_net_name = layer
    raise e

########################################################################


def prepare_reshape(row):
  in_c = int(row[0])
  in_h = int(row[1])
  in_w = int(row[2])
  out_c = int(row[0])
  out_h = int(row[1])
  out_w = int(row[2])

  name = 'shape-' + '-'.join(map(str, [in_c, in_h, in_w, out_c, out_h, out_w]))
  desc = '{}x{}x{} -> {}x{}x{}'.format(in_c, in_h, in_w, out_c, out_h, out_w)
  data = OrderedDict([
      ('CK_IN_SHAPE_C', in_c),
      ('CK_IN_SHAPE_H', in_h),
      ('CK_IN_SHAPE_W', in_w),
      ('CK_OUT_SHAPE_C', out_c),
      ('CK_OUT_SHAPE_H', out_h),
      ('CK_OUT_SHAPE_W', out_w)
  ])

  return name, desc, data

########################################################################


if __name__ == '__main__':
  dataset_dir = os.getenv('CK_NNTEST_DATASET_PATH')
  ck.out('Processing dataset in {} ...'.format(dataset_dir))

  # Load meta
  meta_file = os.path.join(dataset_dir, '.cm', 'meta.json')
  if not os.path.isfile(meta_file):
    raise Exception('Dataset meta not found')
  with open(meta_file) as f:
    meta = json.load(f)

  # Select appropriate preparation mode
  prepare_func = None
  tags = meta.get('tags')
  if 'tensor-avgpool' in tags:
    prepare_func = prepare_avgpool
  elif 'tensor-conv' in tags:
    prepare_func = prepare_conv
  elif 'tensor-depthwiseconv' in tags:
    prepare_func = prepare_depthwiseconv
  elif 'tensor-fullyconnected' in tags:
    prepare_func = prepare_fullyconnected
  elif 'tensor-reshape' in tags:
    prepare_func = prepare_reshape
  else:
    raise Exception('Unsupported dataset')

  # Load tensor shape descriptions from csv
  csv_file_name = meta.get('dataset_descr_file', 'data.csv')
  csv_file = os.path.join(dataset_dir, csv_file_name)
  if not os.path.isfile(csv_file):
    ck.out('\nShape descriptions file "{}" not found.'.format(csv_file_name))
    ck.out('It seems this dataset was prepared manually and does not need to be updated by this program.')
    exit(0)
  rows = []
  with open(csv_file) as f:
    for row in csv.reader(f):
      rows.append(row)

  net_name = ''
  dataset_files = []
  desc_dataset_files = {}
  for row in rows:
    # Column 0 defines network name but not all rows have it
    try:
      if row[0]:
        net_name = row[0]
      else:
        row[0] = net_name
    except:
      ck.out('Skip row {}'.format(row))
      continue

    # Run preparation func
    try:
      name, desc, data = prepare_func(row)
    except ValueError:
      ck.out('Skip row {}'.format(row))
      continue

    if name in dataset_files:
      ck.out('Duplicated shape: {}, second is skipped'.format(name))
      continue

    dataset_files.append(name)
    desc_dataset_files[name] = {'name': desc}

    # Save dataset files
    ck.out('Saving file {} ...'.format(name))
    # TODO I'm not sure why this empty file, it was in original script. Comment needed.
    fn = os.path.join(dataset_dir, name)
    with open(fn, 'w') as f:
      pass
    fn = os.path.join(dataset_dir, name + '.json')
    with open(fn, 'w') as f:
      json.dump(data, f, indent=2)

  # Remove files that no more needed
  old_files = meta.get('dataset_files', [])
  for old_file in old_files:
    if old_file not in dataset_files:
      ck.out('Removing file {} ...'.format(old_file))
      fn = os.path.join(dataset_dir, old_file)
      if os.path.isfile(fn):
        os.remove(fn)
      fn = os.path.join(dataset_dir, old_file + '.json')
      if os.path.isfile(fn):
        os.remove(fn)

  # Update meta
  meta['dataset_files'] = dataset_files
  meta['desc_dataset_files'] = desc_dataset_files
  with open(meta_file, 'w') as f:
    json.dump(meta, f, indent=2)

  ck.out('\nDone')
