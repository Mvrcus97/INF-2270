# PID Assignment
Test your skill at [`PID`][1] creation! Tune your controller graphically through
a state-off-the-art GUI!

## Build
In order to build this code run the following:
```bash
$ cd /path/to/your/workspace
$ catkin build pid_assignment
$ source devel/setup.bash
```

## Running
In the code we have added two [`launch`-files][2] for your benefit. One starts
Gazebo and the other starts the assignment code. They are split so that it is
easier to start and stop your own code without restarting Gazebo (which takes
quite a bit of time).

To start Gazebo:
```
$ roslaunch pid_assignment setup.launch
```

To start the `PID` controller code run:
```bash
$ roslaunch pid_assignment pid.launch
```

Launching `pid.launch` should start [`rqt`][3] where you can change the desired
set-point and tune your `PID` values. If you quit `rqt` your own code will also
be shutdown.

## Tuning `PID`
![`rqt` GUI](rqt.png?raw=true "rqt gui")

In the above image you can change the set-point by editing the `expression`
value under _Message Publisher_. To tune the `PID` either drag the sliders or
edit the value (be sure to press enter when editing or else the value might not
change).

[1]: https://en.wikipedia.org/wiki/PID_controller
[2]: http://wiki.ros.org/roslaunch
[3]: http://wiki.ros.org/rqt
