#!/usr/bin/env python

"""
This is the ROS node that is responsible for calculating effort based
on the desired set-point.

You are not supposed to change anything in this file. See 'src/pid.py'
"""

import rospy
from control_msgs.msg import JointControllerState
from dynamic_reconfigure.server import Server
from pid import PID
from pid_assignment.cfg import PidConfig
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64


class Node(object):
    def __init__(self):
        # Create PID controller
        self._pid = PID()
        # Keep track of position
        self._position = 0.0
        # Keep track of velocity
        self._velocity = 0.0
        # Keep track of desired setpoint
        self._setpoint = 0.0
        # Create ROS publisher to send message to Crustcrawler
        self._out_eff = rospy.Publisher(
                "/crustcrawler/joint2_controller/command", Float64,
                queue_size=5)
        # Create ROS publisher to output internal state
        self._out_state = rospy.Publisher(
                "~state", JointControllerState, queue_size=5)

    def config_callback(self, config, level):
        """
        Callback to update PID parameters
        """
        self._pid.p = config['p']
        self._pid.i = config['i']
        self._pid.d = config['d']
        self._pid.c = config['c']
        return config

    def joint_states_callback(self, states):
        """
        Callback to handle joint state from Crustcrawler

        See http://docs.ros.org/api/sensor_msgs/html/msg/JointState.html
        to understand the message we receive.
        """
        try:
            index = states.name.index("joint_2")
            self._position = states.position[index]
            self._velocity = states.velocity[index]
        except ValueError:
            rospy.logwarn("Could not find 'joint_2' in 'joint_states'")

    def setpoint_callback(self, setpoint):
        """
        Callback to handle setpoint published messages
        """
        self._setpoint = setpoint.data

    def update(self, time_evt):
        """
        Calculate a new update from PID controller
        """
        # Check if this is the first time we are being called
        if time_evt.last_real:
            # Calculate time delta between calls
            dt = time_evt.current_real - time_evt.last_real
            self._publish_effort(dt)
            self._publish_state(dt)

    def _publish_effort(self, dt):
        """
        Helper method to calculate PID and publish
        """
        # Call student PID code to calculate new effort
        effort = self._pid(self._setpoint, self._position, self._velocity,
                           dt.to_sec())
        # Publish to Crustcrawer
        self._out_eff.publish(effort)

    def _publish_state(self, dt):
        """
        Helper method to publish internal state
        """
        # Create internal state message
        msg = JointControllerState()
        msg.header.stamp = rospy.Time.now()
        msg.set_point = self._setpoint
        msg.process_value = self._position
        msg.process_value_dot = self._velocity
        msg.error = self._pid.error
        msg.time_step = dt.to_sec()
        msg.p = self._pid.p
        msg.i = self._pid.i
        msg.d = self._pid.d
        # Publish to listeners
        self._out_state.publish(msg)


if __name__ == '__main__':
    # Create an anonymous ROS node
    rospy.init_node('pid_controller', anonymous=True)
    # Create the actual code that will interact with ROS
    node = Node()
    # Setup callback from Crustcrawler
    rospy.Subscriber("/crustcrawler/joint_states", JointState,
                     node.joint_states_callback)
    # Setup subscription to 'setpoint', this allows users to send messages
    # to '/pid_controller/setpoint' to change our setpoint
    rospy.Subscriber("~setpoint", Float64, node.setpoint_callback)
    # Set up dynamic reconfigure so that we support online PID tuning
    srv = Server(PidConfig, node.config_callback)
    # Create timer so that our code is called at fixed rates
    rospy.Timer(rospy.Duration(1. / 30.), node.update)
    # Sleep until user or ROS quits
    rospy.spin()
