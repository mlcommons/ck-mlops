#
# Collective Knowledge (classify image using various models such as DNN)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, https://fursin.net
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings
import json

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# show dashboard

def show(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import shutil
    import time
    import copy

    form_name='ck_web_service_demo'

    sh=i.get('skip_html','')

    # State reset
    dar=False
    if 'dnn_action_reset' in i: 
       dar=True

    # Start HTML
    h=''
    st=''

    h+='<center>\n'
    h+='\n\n<script language="JavaScript">function copyToClipboard (text) {window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);}</script>\n\n' 

    # Check host URL prefix and default module/action
    rx=ck.access({'action':'form_url_prefix',
                  'module_uoa':'wfe',
                  'host':i.get('host',''), 
                  'port':i.get('port',''), 
                  'template':''})
    if rx['return']>0: return rx
    url0=rx['url']
    template=rx['template']

    url=url0
    action=i.get('action','')
    muoa=i.get('module_uoa','')

    url+='action='+action+'&'+'module_uoa='+muoa
    url1=url

    # Start form
    r=ck.access({'action':'start_form',
                 'module_uoa':cfg['module_deps']['wfe'],
                 'url':url1,
                 'name':form_name})
    if r['return']>0: return r
    h+=r['html']

    url=url0
    onchange='document.'+form_name+'.submit();'

    warning=''
    prediction=''

    # Header
    h+='<h2>CK web service demo to classify image using ONNX and TVM</h2>\n'

    # Select engine
    dt=[
        {'name':'TVM','value':'tvm'},
        {'name':'ONNX runtime', 'value':'onnx'}
       ]

    engine=i.get('dnn_engine','')
    if engine=='': engine='onnx'

    ii={'action':'create_selector',
        'module_uoa':cfg['module_deps']['wfe'],
        'data':dt,
        'name':'dnn_engine',
        'onchange':onchange, 
        'skip_sort':'yes',
        'selected_value':engine}
    r=ck.access(ii)
    if r['return']>0: return r
    x=r['html']

    h+='<br>Select engine: '+x
    h+='<br><br><br>'
          
    fc=i.get('file_content_base64','')
    fcu=i.get('file_content_uploaded','')

    if dar: 
       fc=''
       fcu=''

    if fc=='' and fcu=='':
       # Select image
       h+='Your JPEG image: <input type="file" name="file_content"><br><br>'
       h+='<input type="submit" value="Classify"><br><br>'
    else:
       # Gen tmp file
       rx=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':'.jpg'})
       if rx['return']>0: return rx
       ftmp=rx['file_name']

       if fcu=='':
          # Save user image
          rx=ck.convert_upload_string_to_file({'file_content_base64':fc,
                                               'filename':ftmp})
          if rx['return']>0: return rx
       else:
          shutil.copy(fcu,ftmp)

       h+='<input type="hidden" name="dnn_saved_image_file" value="'+ftmp+'">\n'

       # Classify
       ii={'action':'run',
           'module_uoa':cfg['module_deps']['program'],
           'data_uoa':'ml-task-image-classification-tvm-onnx-cpu',
           'cmd_key':'api-'+engine,
           'quiet':'yes',
           'env':{'CK_IMAGE':ftmp}}
       r=ck.access(ii)
       if r['return']>0:
          warning='Problem running AI engine: '+r['error']+'!'
          h+='<b>WARNING:</b> '+warning+'!<br><br>'
       else:
          ch=r.get('characteristics',{})

          if ch.get('run_success','')!='yes':
             warning='Problem running AI engine: '+ch.get('fail_reason','')
             h+='<b>WARNING:</b> '+warning+'!<br><br>'
          else:
             td=r.get('tmp_dir','')
             deps=r.get('deps',{})

             p1=os.path.join(td,'stdout.log')
             p2=os.path.join(td,'stderr.log')

             s1=''
             s2=''

             r=ck.load_text_file({'text_file':p1})
             if r['return']==0: 
                s1=r['string'].strip()

             r=ck.load_text_file({'text_file':p2})
             if r['return']==0:
                s2=r['string']

             h+='<h2>Prediction:</h2><br>\n'

             h+='<table><tr><td>\n'
             h+='<pre>\n'
             h+=s1+'\n'
             h+='</pre>\n'
             h+='</td></tr></table>\n'

    h+='<br><br>'
    h+='<button type="submit" name="dnn_action_reset">Start again</button>\n'
    h+='<br><br>'

    if sh=='yes':
       h=''
       st=''

    return {'return':0, 'html':h, 'style':st, 'warning':warning, 'prediction':prediction}

##############################################################################
# open dashboard

def dashboard(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    i['action']='browser'
    i['cid']=''
    i['module_uoa']=''
    i['extra_url']='native_action=show&native_module_uoa=model.image.classification'

    return ck.access(i)

##############################################################################
# return json instead of html

def show_json(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    r=show(i)

    if 'html' in r: del(r['html'])
    if 'style' in r: del(r['style'])

    return r
