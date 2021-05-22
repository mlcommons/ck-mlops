#
# Copyright (c) 2017 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Convert raw dvdt prof output to the CK format.
#
# Developer(s):
#   - Grigori Fursin, cTuning foundation, 2017
#   - Anton Lokhmotov, dividiti, 2017
#

import json
import os
import re
import struct
import sys

def process(i):
    """
    Input:  {
              file_out - file with numerical vector output
              data     - dict with CK data to be updated
              env      - CK env to customize output if needed
                          CK_ADD_RAW_DVDT_PROF (if yes then add all raw data to CK pipeline)
              deps     - CK deps to get info about dvdt_prof
            }

    Output: {
              return          - return code =  0, if successful
                                            >  0, if error
              (error)         - error text if return > 0

              unpacted_output - data before finderprinting (to do sanity checks if needed)
            }

    """

    import time

    ck=i['ck_kernel']

    env=i['env']
    d=i['data']

    drts=d.get('run_time_state',{})

    file_out=i['file_out']

    correctness_output_file=d['env']['CK_OUT_RAW_DATA'] #FIXME: rt['run_correctness_output_files'][0]
    binary_format=d['env'].get('CK_OUT_RAW_DATA_BINARY_FORMAT', 'f')

    if not os.path.isfile(correctness_output_file):
       return {'return':1, 'error':'file ('+correctness_output_file+') not found'}

    unpacked_output=[]

    with open(correctness_output_file, 'rb') as output:

        dt=time.time()

        num_classes=drts['out_shape_C']
        batch_size=drts['out_shape_N']        
        w=drts['out_shape_W']
        h=drts['out_shape_H']
        num_elems=int(num_classes*batch_size*w*h)

        bits_per_elem=drts['data_bits']
        bytes_per_elem=bits_per_elem/8
        num_bytes=int(num_elems*bytes_per_elem)

        ck.out('Debug (number of bytes in vector to read): '+str(num_bytes))

        output_as_binary=output.read(num_bytes)

        ck.out('Debug time (reading vector): '+str(time.time()-dt)+' sec.')
        dt=time.time()

        unpacked_output=struct.unpack(binary_format * num_elems, output_as_binary)
        all_unpacked_output=unpacked_output # saving before fingerprinting (if needed)

        ck.out('Debug time (unpacking): '+str(time.time()-dt)+' sec.')
        dt=time.time()

        # If vector is too long, make a fingerprint
        l1=len(unpacked_output)
        l2=100000
        if l1>l2:
           fingerprinted_unpacked_output=[]
           l=0
           while l<l1:
               fingerprinted_unpacked_output.append(unpacked_output[int(l)])
               l+=float(l1)/float(l2)

           ck.out('Length of fingerprinted vector: '+str(len(fingerprinted_unpacked_output))+' instead of '+str(len(unpacked_output)))

           unpacked_output=fingerprinted_unpacked_output

           ck.out('Debug time (fingerprinting): '+str(time.time()-dt)+' sec.')
           dt=time.time()

           env['CK_VECTOR_FINGERPRINTED']='yes'

        if env.get('CK_ADD_RAW_NNTEST_OUTPUT','').lower()=='yes':
           d['output']=unpacked_output

        d['post_processed']='yes'

        # Save to json for further numerical comparison (rather than binary)
        r=ck.save_json_to_file({'json_file':file_out, 'dict':unpacked_output, 'sort_keys':'yes'})
        if r['return']>0: return r

        ck.out('Debug time (saving json): '+str(time.time()-dt)+' sec.')

    return {'return':0, 'unpacked_output':all_unpacked_output}
