#! /usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
import numpy as np
import cv2
from cv_bridge import CvBridge
import tensorflow as tf
import classify_image
from keras.models import load_model

class RosTensorflow():
    def __init__(self):
        self.is_published = False
        self.to_publish = None
        self.model = load_model("/home/ros2018/catkin_ws/src/moving_bot/scripts/blocks_classifier.h5")
        self.classes = ['Block', 'Fire Hydrant']
        self.img_width, self.img_height = 64, 64

        self.graph = tf.get_default_graph()

        # self.img_counter = 95
        self._session = tf.Session()
        self._cvbridge = CvBridge()
        # subscribe to the image publishing topic
        self._sub = rospy.Subscriber("/mybot/camera/image_raw", Image , self.callback, queue_size=1)
        # topic to publish the results
        self._pub = rospy.Publisher('/result', String, queue_size =1)
        self.score_threshold = rospy.get_param("score_threshold", 0.1)
        self.use_top_k = rospy.get_param("-use_top_k", 5)


    def callback(self, image_msg):
        cv_image = self._cvbridge.imgmsg_to_cv2(image_msg, desired_encoding="passthrough")
        cv_image  = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        resized_image = cv2.resize(cv_image, (self.img_width, self.img_height))
        input_image = np.resize(resized_image, (1, self.img_width, self.img_height, 3))
        with self.graph.as_default():
            prediction = self.model.predict(input_image)
            print("Predicted Value: " + self.classes[int(prediction[0][0])])
            if self.to_publish != self.classes[int(prediction[0][0])]:
                self.to_publish = self.classes[int(prediction[0][0])]
                self._pub.publish(self.to_publish)


    def display(self,cv_image):
        cv2.imshow('image',cv_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def prep(self):
        if (self.img_counter >= 500):
            print("Full")
        else:
            print "Not yet on [%s]"%self.img_counter
            file_name = "fire_hydrant"+str(self.img_counter)+".jpg"
            cv2.imwrite(file_name, cv_image)
            # self.img_counter += 1
    def main(self):
        rospy.spin()


if __name__ == '__main__':
    print("Running")
    rospy.init_node("tensorflow")
    tensor = RosTensorflow()
    tensor.main()

        