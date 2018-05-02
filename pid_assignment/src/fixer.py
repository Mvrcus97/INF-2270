#!/usr/bin/env python

"""
Helper code to set to joints in the simulation to static

!!!Do not change this file!!!
"""

import rospy
from gazebo_msgs.srv import SetJointProperties
from gazebo_msgs.srv import SetJointPropertiesRequest


def _create_service_msg(name):
    """
    Helper method to create service arguments
    """
    msg = SetJointPropertiesRequest()
    msg.joint_name = name
    msg.ode_joint_config.hiStop.extend([0.0, 0.0, 0.0])
    msg.ode_joint_config.loStop.extend([0.0, 0.0, 0.0])
    msg.ode_joint_config.vel.extend([0.0, 0.0, 0.0])
    return msg


if __name__ == '__main__':
    rospy.init_node("gazebo_fix", anonymous=True)
    # Wait for Gazebo to advertise service to us
    rospy.wait_for_service('/gazebo/set_joint_properties')
    # Because of race conditions we sleep for X seconds
    rospy.sleep(2.0)
    # Send message to fix two joints
    try:
        serv = rospy.ServiceProxy('/gazebo/set_joint_properties',
                                  SetJointProperties)
        msg = _create_service_msg("joint_1")
        if not serv(msg):
            rospy.logfatal("Gazebo could not fix 'joint_1'!")
        msg = _create_service_msg("joint_3")
        if not serv(msg):
            rospy.logfatal("Gazebo could not fix 'joint_3'!")
    except rospy.ServiceException as e:
        rospy.logfatal("Could not call 'set_joint_properties': {!s}".format(e))
    else:
        rospy.loginfo("Set 'joint_1' and 'joint_3' fixed")
