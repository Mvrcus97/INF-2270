#!/usr/bin/env python

"""
This node is designed to take in a circle drawing description and perform
the necessary calculations and commands to draw the circle using the
Crustcrawler platform
"""

from __future__ import print_function
from control_msgs.msg import FollowJointTrajectoryAction
from control_msgs.msg import FollowJointTrajectoryGoal
from control_msgs.msg import JointTolerance
from trajectory_msgs.msg import JointTrajectoryPoint
import actionlib
import numpy as np
import rospy


def path_length(path):
    """
    Calculate path length in centimeters

    :param path: List of points
    :returns: Length of path in centimeters
    """
    length = 0.0
    for p1, p0 in zip(path[1:], path):
        length += np.linalg.norm(p1 - p0)
    return length


def inverse_kinematic(position):
    """
    Calculate the inverse kinematic of the Crustcrawler

    :param position: Desired end-point position
    :returns: Three element vector of joint angles
    """
    x, y, z = position
    l1 = 11.0
    l2 = 22.3
    l3 = 17.1
    l4 = 8.0
    l3_mark = np.sqrt(l4 ** 2 + l3 ** 2 + np.sqrt(2) / 2.0 * l4 * l3)
    phi = np.arccos((l3 ** 2 + l3_mark ** 2 - l4 ** 2)
                    / (2.0 * l4 * l3_mark))
    s = z - l1
    r = np.sqrt(x ** 2 + y ** 2)
    d = ((x ** 2 + y ** 2 + s ** 2 - l2 ** 2 - l3_mark ** 2)
         / (2. * l2 * l3_mark))

    theta1 = np.arctan2(y, x)
    theta3 = np.arctan2(-np.sqrt(1. - d ** 2), d)
    theta2 = np.arctan2(s, r) - np.arctan2(l3_mark * np.sin(theta3),
                                           l2 + l3_mark * np.cos(theta3))
    return np.array([theta1, theta2 * -1. + np.pi / 2., theta3 * -1.])


def create_trajectory_point(position, seconds):
    """
    Create a JointTrajectoryPoint

    :param position: Joint positions
    :param seconds: Time from start in seconds
    :returns: JointTrajectoryPoint
    """
    point = JointTrajectoryPoint()
    point.positions.extend(position)
    point.time_from_start = rospy.Duration(seconds)
    return point


def rotate_path(path, angle, axis):
    """
    Rotate all elements of a path by angle-axis rotation

    :param path: List of points
    :param angle: Angle in radians to rotate by
    :param axis: Unit vector to rotate around
    :returns: List of rotated points
    """


    # TODO: Implement as part 'c)'

    #In this task it seems the only axis chosen is the Y axis. 

    rospy.loginfo("axis is: " + str(axis))

    axis_val = -1

    for i in range (3):
        if axis[i] == 1:
            #Store which axis to rotate about. X = 1, Y = 2 and Z = 3
            axis_val = i+1

    rospy.loginfo("axis_val er : " + str(axis_val))

    rot_x = np.matrix([[1,0,0], 
        [0, np.cos(angle), np.sin(angle)],
        [0, -np.sin(angle), np.cos(angle)]])

    
    rot_y = np.matrix([[np.cos(np.degrees(angle)),0,-np.sin(np.degrees(angle))], 
        [0, 1, 0],
        [np.sin(np.degrees(angle)), 0,  np.cos(np.degrees(angle))]])
    

    rot_z = np.matrix([[np.cos(angle), np.sin(angle), 0], 
        [-np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]])


    test = np.matrix([10,10,10])


    path2 = []
    
    
    #If axis chosen is y ( which it always is)
    if axis_val == 2:
        for i in range(len(path)):
            path2.append(np.dot(path[i], rot_y))


    #Path2 is now matrix. wont work for some reason, so make the
    #Matrix and array:
    path2 = np.squeeze(np.asarray(path2))


        



    return path2


def generate_path(origin, radius, num, angle, axis):
    """
    Generate path in 3D space of where to draw circle

    :param origin: 3D point of circle origin
    :param radius: Radius of circle in centimeters
    :param num: Number of points in circle
    :param angle: Angle to rotate circle by
    :param axis: Unit vector to rotate circle around
    :returns: List of points to draw
    """
    path = []

    distance_between = (2.0 * np.pi) / float(num)

    for i in range(num + 1):
        index = i * distance_between
        path.append(radius * np.array([np.cos(index), np.sin(index), 0.0]))

    # Rotate using the rotation function
    path = rotate_path(path, angle, axis)
    # Add origin to path:
    path = [p + origin for p in path]
    return path

    

def generate_movement(path):
    """
    Generate Crustcrawler arm movement through a message

    :param path: List of points to draw
    :returns: FollowJointTrajectoryGoal describing the arm movement
    """
    # Generate our goal message
    movement = FollowJointTrajectoryGoal()

    # Names describes which joint is actuated by which element in the coming
    # matrices
    movement.trajectory.joint_names.extend(['joint_1', 'joint_2', 'joint_3'])
    # Goal tolerance describes how much we allow the movement to deviate
    # from true value at the end
    movement.goal_tolerance.extend([
        JointTolerance('joint_1', 0.1, 0., 0.),
        JointTolerance('joint_2', 0.1, 0., 0.),
        JointTolerance('joint_3', 0.1, 0., 0.)])
    # Goal time is how many seconds we allow the movement to take beyond
    # what we define in the trajectory
    movement.goal_time_tolerance = rospy.Duration(0.5)  # seconds

    time = 4.0  # Cumulative time since start in seconds
    movement.trajectory.points.append(
        create_trajectory_point([0., 0., np.pi / 2.], time))

    # Add initial point, also as a large time fraction to avoid jerking
    time += 4.0
    movement.trajectory.points.append(
        create_trajectory_point(inverse_kinematic(path[0]), time))

    # Calculate total circle length
    length = path_length(path)
    # Calculate how much time we have to process each point of the circle
    time_delta = (length / 2.) / len(path)

    for point in path[1:]:
        time += time_delta
        movement.trajectory.points.append(
	        create_trajectory_point(inverse_kinematic(point), time))

    # Once drawing is done we add the default position
    time += 4.0
    movement.trajectory.points.append(
        create_trajectory_point([0., 0., np.pi / 2.], time))
    return movement



    


def draw_circle(origin, radius, num, angle, axis):
    """
    Draw circle using Crustcrawler

    :param origin: 3D point of circle origin
    :param radius: Radius of circle in centimeters
    :param num: Number of points in circle
    :param angle: Angle to rotate circle by
    :param axis: Unit vector to rotate circle around
    """
    # First start by creating action client, this is responsible for passing
    # our parameters and monitoring the Crustcrawler during operations
    client = actionlib.SimpleActionClient(
            '/crustcrawler/controller/follow_joint_trajectory',
            FollowJointTrajectoryAction)
    # Generate circle path
    path = generate_path(origin, radius, num, angle, axis)
    # Generate arm movement path
    goal = generate_movement(path)
    # Wait for arm to respond to action client
    client.wait_for_server()
    # Send goal
    client.send_goal(goal)
    # Wait for arm to perform our movement
    client.wait_for_result()
    # Finally print status of arm, did it work or not?
    result = client.get_result()
    if not result.error_code:
        print("Crustcrawler done!")
    else:
        print("Crustcrawler failed due to: '{!s}'({!s})"
              .format(result.error_string, result.error_code))
    return result.error_code


if __name__ == '__main__':
    import argparse
    import sys
    # Create command line parser and add options:
    parser = argparse.ArgumentParser(
            description="CrustCrawler circle drawer TM(C), patent pending!",
            version="Spring 2018")
    parser.add_argument(
            '--origin', '-o', type=float, nargs=3,
            metavar=('x', 'y', 'z'), required=True,
            help="Origin of the board")
    parser.add_argument(
            '--radius', '-r', type=float, default=5.0,
            metavar='cm', help="The radius of the circle to draw")
    parser.add_argument(
            '--num_points', '-n', type=int,
            default=4, metavar='num',
            help="Number of points to use when drawing the circle")
    parser.add_argument(
            '--orientation', '-orient', type=float, default=0.0,
            metavar='degrees',
            help="Orientation of the board along the X-axis")
    args = parser.parse_args()
    # Ensure points are NumPy arrays
    args.origin = np.array(args.origin)
    orient = np.array([0, 1., 0])
    # Ensure that arguments are within legal limits:
    if 0.0 > args.orientation or args.orientation > 90.0:
        sys.exit("Orientation must be in range [0.0, 90.0], was: {:.1f}"
                 .format(args.orientation))
    if 3 >= args.num_points <= 101:
        sys.exit("Number of points must be in range [3, 101] was: {:d}"
                 .format(args.num_points))
    max_dist = np.linalg.norm(args.origin)
    if max_dist - args.radius < 20.0:
        sys.exit("Circle to close to the robot! Minimum: 40cm, was: {:.2f}"
                 .format(max_dist - args.radius))
    # Create ROS node
    rospy.init_node('circle_drawer', anonymous=True)
    # Call function to draw circle
    try:
        sys.exit(draw_circle(args.origin, args.radius, args.num_points,
                             np.deg2rad(args.orientation), orient))
    except rospy.ROSInterruptException:
        sys.exit("Program aborted during circle drawing")