import subprocess
import IPython
import tensorflow as tf
from object_detection.utils import config_util
from object_detection.protos import pipeline_pb2
from google.protobuf import text_format
WORKSPACE_PATH = 'C:/KISHORE/Sde_Projects/UsingTensorflow/RealTimeObjectDetection/Tensorflow/workspace'
SCRIPTS_PATH = 'C:/KISHORE/Sde_Projects/UsingTensorflow/RealTimeObjectDetection/Tensorflow/scripts'
APIMODEL_PATH = 'Tensorflow/models'
ANNOTATION_PATH = WORKSPACE_PATH+r'/annotations'
IMAGE_PATH = WORKSPACE_PATH+r'/images'
MODEL_PATH = WORKSPACE_PATH+r'/models'
PRETRAINED_MODEL_PATH = WORKSPACE_PATH+r'/pre-trained-models'
CONFIG_PATH = MODEL_PATH+r' /my_ssd_mobnet/pipeline.config'
CHECKPOINT_PATH = MODEL_PATH+r'/my_ssd_mobnet/'

#Creating a label map
labels = [{'name' : 'Hello' , 'id' : 1} , {'name' : 'Thanks' , 'id' : 2} , {'name' : 'Yes' , 'id' : 3} , {'name' : 'No' , 'id' : 4} , {'name' : 'I Love You','id' : 5} , {'name' : 'LiveLong' , 'id' : 6}]

with open(ANNOTATION_PATH + '\label_map.pbtxt', 'w') as f:
    for label in labels:
        f.write('item { \n')
        f.write('\tname:\'{}\'\n'.format(label['name']))
        f.write('\tid:{}\n'.format(label['id']))
        f.write('}\n')
# -
train_command = [
    "python",
    f"{SCRIPTS_PATH}/generate_tfrecord.py",
    "-x", f"{IMAGE_PATH}/train",
    "-l", f"{ANNOTATION_PATH}/label_map.pbtxt",
    "-o", f"{ANNOTATION_PATH}/train.record"
]

# Command for test data
test_command = [
    "python",
    f"{SCRIPTS_PATH}/generate_tfrecord.py",
    "-x", f"{IMAGE_PATH}/test",
    "-l", f"{ANNOTATION_PATH}/label_map.pbtxt",
    "-o", f"{ANNOTATION_PATH}/test.record"
]

# Execute commands
subprocess.run(train_command, check=True)
subprocess.run(test_command, check=True)


CUSTOM_MODEL_NAME = 'my_ssd_mobnet' 



# # 5. Update Config For Transfer Learning

CONFIG_PATH = MODEL_PATH+'/'+CUSTOM_MODEL_NAME+'/pipeline.config'

config = config_util.get_configs_from_pipeline_file(CONFIG_PATH)

config

pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()
with tf.io.gfile.GFile(CONFIG_PATH, "r") as f:                                                                                                                                                                                                                     
    proto_str = f.read()                                                                                                                                                                                                                                          
    text_format.Merge(proto_str, pipeline_config)  

pipeline_config.model.ssd.num_classes = 2
pipeline_config.train_config.batch_size = 4
pipeline_config.train_config.fine_tune_checkpoint = PRETRAINED_MODEL_PATH+'/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8/checkpoint/ckpt-0'
pipeline_config.train_config.fine_tune_checkpoint_type = "detection"
pipeline_config.train_input_reader.label_map_path= ANNOTATION_PATH + '/label_map.pbtxt'
pipeline_config.train_input_reader.tf_record_input_reader.input_path[:] = [ANNOTATION_PATH + '/train.record']
pipeline_config.eval_input_reader[0].label_map_path = ANNOTATION_PATH + '/label_map.pbtxt'
pipeline_config.eval_input_reader[0].tf_record_input_reader.input_path[:] = [ANNOTATION_PATH + '/test.record']

config_text = text_format.MessageToString(pipeline_config)                                                                                                                                                                                                        
with tf.io.gfile.GFile(CONFIG_PATH, "wb") as f:                                                                                                                                                                                                                     
    f.write(config_text)   

# # 6. Train the model

print("""python {}/research/object_detection/model_main_tf2.py --model_dir={}/{} --pipeline_config_path={}/{}/pipeline.config --num_train_steps=5000""".format(APIMODEL_PATH, MODEL_PATH,CUSTOM_MODEL_NAME,MODEL_PATH,CUSTOM_MODEL_NAME))

# # 7. Load Train Model From Checkpoint

import os
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder

# +
# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(CONFIG_PATH)
detection_model = model_builder.build(model_config=configs['model'], is_training=False)

# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(CHECKPOINT_PATH, 'ckpt-6')).expect_partial()

@tf.function
def detect_fn(image):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections


# -

# # 8. Detect in Real-Time

import cv2 
import numpy as np

category_index = label_map_util.create_category_index_from_labelmap(ANNOTATION_PATH+'/label_map.pbtxt')

#cap.release()

# Setup capture
cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

while True: 
    ret, frame = cap.read()
    image_np = np.array(frame)
    
    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
    detections = detect_fn(input_tensor)
    
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections

    # detection_classes should be ints.
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    label_id_offset = 1
    image_np_with_detections = image_np.copy()

    viz_utils.visualize_boxes_and_labels_on_image_array(
                image_np_with_detections,
                detections['detection_boxes'],
                detections['detection_classes']+label_id_offset,
                detections['detection_scores'],
                category_index,
                use_normalized_coordinates=True,
                max_boxes_to_draw=5,
                min_score_thresh=.5,
                agnostic_mode=False)

    cv2.imshow('object detection',  cv2.resize(image_np_with_detections, (800, 600)))
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cap.release()
        break

detections = detect_fn(input_tensor)

from matplotlib import pyplot as plt


