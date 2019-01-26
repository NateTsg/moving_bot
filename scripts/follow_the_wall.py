#!/usr/bin/env python
import rospy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from geometry_msgs.msg import Twist
gState = 0
pub = None

gStateDict = {
    0:'find_the_wall',
    1:'turn_left',
    2:'follow_the_wall',
    3:'fire_hydrant_detected'
}
# Regions infront of the ros
gRegions = {}
def change_state(new_state):
    global gState
    if int(gState) != int(3):

        gState = new_state
        print "Change State to [%s]"% new_state


def LaserScanProcess(msg):
    global gRegions
    gRegions = {
       "right" : min(min(msg.ranges[0:143]),10),
        "front_right" : min(min(msg.ranges[144:287]),10),
        "front" : min(min(msg.ranges[288:431]),10),
        "front_left" : min(min(msg.ranges[432:575]),10),
        "left" : min(min(msg.ranges[576:720]),10),
    }
    
    move(gRegions)
# Avoid obstacles on the way
def move(regions):
    global gRegions
    linear_x = 0
    angular_z = 0

    d = 1.5
    if regions["front"] > d and regions["front_left"]>d and regions["front_right"]>d:
        state_description =  "case 1 - Nothing"
        change_state(0)
    elif regions["front"] < d and regions["front_left"]>d and regions["front_right"]>d:
        state_description =  "case 2 - Front"
        change_state(1)
    elif regions["front"] > d and regions["front_left"]>d and regions["front_right"]<d:
        state_description =  "case 3 - Front_Right"
        change_state(0)
    elif regions["front"] > d and regions["front_left"]<d and regions["front_right"]>d:
        state_description =  "case 4 - Front_Left"
        change_state(2)
    elif regions["front"] < d and regions["front_left"]>d and regions["front_right"]<d:
        state_description =  "case 5 - Front and Right"
        change_state(1)
    elif regions["front"] < d and regions["front_left"]<d and regions["front_right"]>d:
        state_description =  "case 6 - Front and Left"
        change_state(1)
    elif regions["front"] < d and regions["front_left"]<d and regions["front_right"]<d:
        state_description =  "case 7 - All"
        change_state(1)
    elif regions["front"] > d and regions["front_left"]<d and regions["front_right"]<d:
        state_description =  "case 8 - Front_Right and Front_Left"
        change_state(0)
    else:
        state_description = "Unknow  state"
        print("In Else")
        
def find_wall():
    msg = Twist()
    msg.linear.x = 0.4
    msg.angular.z = -0.3
    return msg

def turn_left():
    msg = Twist()
    msg.angular.z = 0.5
    return msg

def follow_the_wall():
    msg = Twist()
    msg.linear.x = 0.5
    return msg

def TfCallback(msg):
    print('object Detected %s'%len(msg.data))
    if int(len(msg.data)) == int(12):
        change_state(3)
    else:
        change_state(2)



def follow_the_hydrant_and_stop():
    global gRegions
    regions = gRegions
    msg = Twist()
    d = 1.5
    if regions["front"] < d or regions["front_left"]< d or regions["front_right"]<d:
        print  "Near Hydrant "
        msg.angular.z = 0
        msg.linear.x = 0
    elif regions["front"] > d or regions["front_left"]< d or regions["front_right"]>d:
        print  "Near Hydrant "
        msg.angular.z = 0.1
        msg.linear.x = 0.4
    else:
        print "Reaching"
        msg.linear.x = 0.3
    return msg
        
def main():
    global pub
    global gDesiredPosition, gState
    rospy.init_node('listener', anonymous=True)

    pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
    laser_sub = rospy.Subscriber("scan", LaserScan , LaserScanProcess)
    # sub = rospy.Subscriber("odom", Odometry, ScanCallback)
    tf_sub = rospy.Subscriber("/result", String, TfCallback)

 
    rate = rospy.Rate(10) # 10hz
    print "Enter"
    while not rospy.is_shutdown():
       
        if gState == 0:
            msg = find_wall()
        elif gState == 1:
            msg = turn_left()
        elif gState == 2:
            msg = follow_the_wall()
            pass
        elif gState == 3:
            msg = follow_the_hydrant_and_stop()
        else:
            rospy.logerr("Unknown State")
            pass
        pub.publish(msg)
        rate.sleep()


if __name__ == '__main__':
    print '5' == '5'
    main()
