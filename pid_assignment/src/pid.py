#!/usr/bin/env python

"""
Implementation of a PID controller.

Assignment 3, INF3480
"""
import rospy
import math


class PID(object):
    def __init__(self):
        # Proportional constant
        self.p = 0.0
        # Integral constant
        self.i = 0.0
        # Integral accumulation variable
        self.integral = 0.0
        # Derivative constant
        self.d = 0.0
        # Non-linear constant
        self.c = 0.0
        # Position error
        self.error = 0.0

	#Ekstra: dt total
	self.dtTotal = 0.0

    def __call__(self, desired_theta, current_theta, velocity_theta, dt):
        """
        Perform PID control step

        :param desired_theta: Desired set-point in radians
        :param current_theta: Current joint angle in radians
        :param velocity_theta: Current joint angle velocity in radians/second
        :param dt: Time since last call in seconds
        :returns: Effort for joint
        """
        # TODO: Change which line is commented according to which part
        # you are testing in your code.
        #return self.step_b(desired_theta, current_theta, dt)
       	#return self.step_c(desired_theta, current_theta, velocity_theta, dt)
        #return self.step_d(desired_theta, current_theta, velocity_theta, dt)
        return self.step_e(desired_theta, current_theta, velocity_theta, dt)

    def step_b(self, desired_theta, current_theta, dt):
        """
        Calculate proportional control

        :param desired_theta: Desired set-point in radians
        :param current_theta: Current joint angle in radians
        :param dt: Time since last call in seconds
        :returns: Effort of joint
        """
        # TODO: Implement!
        # TIP: Use 'rospy.loginfo' to print output in ROS

	e = desired_theta - current_theta
	K = self.p

	u = K * e
	

        return u

    def step_c(self, desired_theta, current_theta, velocity_theta, dt):
        """
        Calculate Proportional-Derivative control

        :param desired_theta: Desired set-point in radians
        :param current_theta: Current joint angle in radians
        :param velocity_theta: Current joint angle velocity in radians/second
        :param dt: Time since last call in seconds
        :returns: Effort for joint
        """
        # TODO: Implement!
        # TIP: Use 'rospy.loginfo' to print output in ROS

	e = desired_theta - current_theta #From b)
	Kpe = self.p * e
	
	edot = -velocity_theta
	Kdedot = self.d * edot

	
	u = Kpe + Kdedot
		
        return u

    def step_d(self, desired_theta, current_theta, velocity_theta, dt):
        """
        Calculate PID control

        :param desired_theta: Desired set-point in radians
        :param current_theta: Current joint angle in radians
        :param velocity_theta: Current joint angle velocity in radians/second
        :param dt: Time since last call in seconds
        :returns: Effort for joint
        """
        # TODO: Implement!
        # TIP: Use 'rospy.loginfo' to print output in ROS
        
	e = desired_theta - current_theta #From b)
	Kpe = self.p * e
	
	edot = -velocity_theta #from c)
	Kdedot = self.d * edot

	Ki = self.i
    

	self.integral += e * dt  #Integral is the same as the area under the graph.
 		
	
	u = Kpe + self.integral + Kdedot

	return u
	

    def step_e(self, desired_theta, current_theta, velocity_theta, dt):
        """
        Calculate non-linear PID control

        :param desired_theta: Desired set-point in radians
        :param current_theta: Current joint angle in radians
        :param velocity_theta: Current joint angle velocity in radians/second
        :param dt: Time since last call in seconds
        :returns: Effort for joint
        """
        # TODO: Implement!
        # TIP: Use 'rospy.loginfo' to print output in ROS


        d = self.step_d(desired_theta, current_theta, velocity_theta, dt) 
        u = d + self.c * math.sin(current_theta)

        return u
