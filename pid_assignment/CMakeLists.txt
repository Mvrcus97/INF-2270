cmake_minimum_required(VERSION 2.8.3)
project(pid_assignment)

# Locate dependencies
find_package(catkin REQUIRED COMPONENTS
	rospy
	control_msgs
	crustcrawler_pen_gazebo
	dynamic_reconfigure
	sensor_msgs
	std_msgs
	)

# Automatic support for online PID tuning
generate_dynamic_reconfigure_options(
	cfg/Pid.cfg
	)

# Call to create ROS package
catkin_package(CATKIN_DEPENDS rospy dynamic_reconfigure)

