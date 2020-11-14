import json
import os
import re

#FIXME GET FILENAME 
def ck_postprocess(i):
    ck=i['ck_kernel']
    d={}
    env=i.get('env',{})    
    rt=i['run_time']
#    for ii in i.keys():
#        print ii
    d['program_name'] = i['meta']['data_name']
    rf1=rt['run_cmd_out1']
    r=ck.load_text_file({'text_file':rf1,'split_to_list':'yes'})
    if r['return']>0: return

#  PARSER GOES HERE
    keys_allowed = ['backend', 'model', 'conv_method', 'dtype', 'cost']
    for line in r['lst']:
        ls = line.split('\t')
        for l in ls:
            keyvalue = l.split(':')
            if keyvalue[0] in keys_allowed:
                if keyvalue[0] == 'dtype': 
                    keyvalue[0] = 'precision'
                    if keyvalue[1] == 'float32':
                        keyvalue[1] = 'fp32'
                    else:
                        keyvalue[1] = 'fp16'
                else:
                    keyvalue[1] = keyvalue[1][1:]
                if keyvalue[0] == 'cost':  
                    keyvalue[0] = 'prediction_time_s'
                    keyvalue[1] = float(keyvalue[1])
                d[keyvalue[0]] = keyvalue[1]
# END 

    if d.has_key('prediction_time_s'):
        d['post_processed'] = 'yes'
    rr={}
    rr['return']=0
    if d.get('post_processed','')=='yes':
        r=ck.save_json_to_file({'json_file':'tmp-ck-output.json', 'dict':d})
        if r['return']>0: return r
    else:
       rr['return']=1
       rr['error']='failed to find the time in output'

    return rr
# Do not add anything here!
   
