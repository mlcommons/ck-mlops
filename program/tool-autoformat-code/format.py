#!/usr/bin/env python
#
# Copyright (c) 2018 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# SPDX-License-Identifier: BSD-3-Clause.
# See CK LICENSE.txt for licensing details.
#

import os
import fnmatch

CK_PROGRAM = False
FILTERS = os.getenv('CK_FILTER', 'cpp,c,h,py').split(',')

ASTYLE_PARAMETERS = [
    '--suffix=none',  # Do not retain a backup of the original file.
    '--quiet',  # Suppress all output except error messages.
    '--style=java',
    '--indent=spaces=2',
    '--indent-switches',
    '--indent-col1-comments',
    '--min-conditional-indent=0',
    '--max-instatement-indent=120',
    '--pad-oper',
    '--align-pointer=name',
    '--align-reference=name',
    '--break-closing-brackets',
    '--keep-one-line-statements',
    '--max-code-length=120',
    '--mode=c',
    '--lineend=linux',
    '--indent-preprocessor'
]

AUTOPEP8_PARAMETERS = [
    '--in-place',
    '--aggressive',  # Enable non-whitespace changes,
    '--aggressive',  # multiple options result in more aggressive changes
    '--max-line-length 120',
    '--indent-size 2',
]


def format_file(file_name):
  print('Formatting file {} ...'.format(file_name))
  if fnmatch.fnmatch(file_name, '*.py'):
    os.system('autopep8 {} {}'.format(' '.join(AUTOPEP8_PARAMETERS), file_name))
  else:
    os.system('astyle {} {}'.format(' '.join(ASTYLE_PARAMETERS), file_name))


def need_format_file(file_name):
  for pattern in FILTERS:
    if fnmatch.fnmatch(file_name, '*.' + pattern):
      return True
  return False


def format_dir(dir_name):
  file_count = 0
  print('Processing dir {} ...'.format(dir_name))
  for dir_item in os.listdir(dir_name):
    full_path = os.path.join(dir_name, dir_item)
    if os.path.isdir(full_path):
      if dir_item.startswith('.'):
        continue
      if CK_PROGRAM:
        if dir_item == 'tmp':
          continue
      file_count += format_dir(full_path)
    elif os.path.isfile(full_path):
      if need_format_file(dir_item):
        format_file(full_path)
        file_count += 1
  return file_count


if __name__ == '__main__':
  dir_name = os.getenv('CK_DIR')
  if dir_name:
    if not os.path.isdir(dir_name):
      print('\nERROR: directory does not exist: ' + dir_name)
      exit(-1)
    prog_uoa = os.getenv('CK_PROGRAM')
    if prog_uoa:
      CK_PROGRAM = True
      print('Processing program {} ...'.format(prog_uoa))
    print('Target files: {}'.format(FILTERS))
    file_count = format_dir(dir_name)
    if not file_count:
      print('\nThere are no files for formatting')
    else:
      print('\nDone.\nFiles processed: {}'.format(file_count))
    exit(0)

  file_name = os.getenv('CK_FILE')
  if file_name:
    if not os.path.isfile(file_name):
      print('\nERROR: file does not exist: ' + file_name)
      exit(-1)
    format_file(file_name)
    print('\nDone')
    exit(0)

  print('\nNothing to process. Please specify CK_FILE, CK_DIR or CK_PROGRAM')
