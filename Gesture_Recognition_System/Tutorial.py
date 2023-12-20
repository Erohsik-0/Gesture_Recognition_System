#Create default paths to use it frequently
WORKSPACE_PATH = 'C:\KISHORE\Sde_Projects\Using Tensorflow\RealTimeObjectDetection\Tensorflow\workspace'
SCRIPTS_PATH = 'C:\KISHORE\Sde_Projects\Using Tensorflow\RealTimeObjectDetection\Tensorflow\scripts'
APIMODEL_PATH = ''
ANNOTATION_PATH = WORKSPACE_PATH+'/annotations'
IMAGE_PATH = WORKSPACE_PATH+'/images'
MODEL_PATH = WORKSPACE_PATH+'/models'
PRETRAINED_MODEL_PATH = WORKSPACE_PATH+'/pre-trained-models'
CONFIG_PATH = ''
CHECKPOINT_PATH = ''

#Creating labels for the 5-basic gestures
labels = [{'name':'Hello' , 'id':1},
          {'name':'Yes' , 'id':2},
          {'name':'No' , 'id':3},
          {'name':'Thank You' , 'id':4},
          {'name':'I Love You' , 'id':5},
          {'name' : 'Live Long' , 'id' : 6}]

with open(ANNOTATION_PATH+'\label_map.pbtxt' , 'w') as f:
    for label in labels:
        f.write()
        f.write()
        f.write()
        f.write()
        f.write()