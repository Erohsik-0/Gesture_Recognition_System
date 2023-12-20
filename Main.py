import cv2
import os
import time
import uuid

#Setting the image path as global variable
imgpath = r"C:\KISHORE\Sde_Projects\Using Tensorflow\RealTimeObjectDetection\Tensorflow\workspace\images\Collected_Images"

#Naming the gestures
labels = ["hello" , "thanks" , "yes" , "no" , "iloveyou" , "LiveLong"]
numberofimages = 15

#Collecting the images for taining and testing
for label in labels:
    #Creating seperate folder for the group of images
    os.mkdir(os.path.join(imgpath , label))
    #Collecting the images and labelling them as required
    cap = cv2.VideoCapture(0)
    print("Collecting images for {}".format(label)) 
    time.sleep(5)

    for n in range(numberofimages):
        ret , frame = cap.read()
        if not ret :
            print("Error: Unable to capture frame.")
            continue
        #Join used to concatenate different datas intelligently
        #It also generates a filename for the image and it is stored in the path specified in the variable "imgpath"
        imgname = os.path.join(imgpath , label , label+'.'+'{}.jpg'.format(str(uuid.uuid1())))
        cv2.imwrite(imgname , frame)
        cv2.imshow('frame' , frame)
        time.sleep(5)
        #Setting the exit value as 'q'
        if cv2.waitKey(1) and 0xFF == ord('q'):
            break
    cap.release()