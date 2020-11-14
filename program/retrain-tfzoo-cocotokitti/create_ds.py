import os

from object_detection.dataset_tools.create_kitti_tf_record import convert_kitti_to_tfrecords as convert





if __name__ == '__main__':
  params = {}
  params["DATA_DIR"] = os.getenv("CK_ENV_DATASET_KITTI",'')
  params["PIPELINE_DIR"] = os.getenv("CK_ENV_TENSORFLOW_MODEL_FROZEN_GRAPH",'')
  params["OUTPUT_PATH"] = os.getenv("CK_OUTPATH",'')
  params["CLASSES"] = os.getenv("CK_CLASSES",'car,van,truck,pedestrian,person_sitting,cyclist,tram')
  params["LABELMAP_PATH"] = os.getenv("CK_LABELMAP",'../kitti_label_map.pbtxt')
  params["VALIDATION_SIZE"] =int(os.getenv("CK_VALIDATION_SIZE",'500'))
  print ("creating dataset")
  convert(params["DATA_DIR"],params["OUTPUT_PATH"],params["CLASSES"],params["LABELMAP_PATH"],params["VALIDATION_SIZE"])
   
  print ("creation of the dataset done!")
  print (" ######################################################################## ")

  print ("copying pipeline.config")
  print (" ATTENTION: THIS FILE NEEDS TO BE MANUALLY EDITED BY THE USER")
  print ("this is due to the fact that the tarballs downloadable from tensorflow are not always updated, so there may be some wrong pipelines.config. It is usually enough to google the error to find how to fix it")
  print ("moreover, some paths need to be fixed, the image resizing too")
  print ("######################################################################### ")
  from shutil import copyfile
  file_name =os.path.join( os.path.dirname(params["PIPELINE_DIR"]),'pipeline.config')
  copyfile(file_name, 'pipeline.config')
  
