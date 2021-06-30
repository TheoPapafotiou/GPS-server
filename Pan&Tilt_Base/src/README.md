# PhantomX Turret ROS Packages
This project uses the PhantomX Turret Kit to set a desired position of the camera used for the GPS server. 
Therefore, with the procedure below, a visualized handling of the arm position -and consequently the camera position- is feasible.
The project is based on the repositories:
[vanadiumlabs/arbotix_ros#28]
[fictionlab/pincher_arm]

## Building

All of the dependencies can be installed using the [rosdep] tool.
* cd ~/.../GPS-server/Pan&Tilt\_Base
* sudo apt-get install ros-melodic-moveit*
* catkin_make
* source devel/setup.bash

## Usage

Start the arm driver:
```
roslaunch pincher_arm_bringup arm.launch
```
You might need to change the `port` parameter in the `pincher_arm_bringup/config/arm.yaml` file.

Once you have the driver up and running, you can start MoveIt!:
```
roslaunch pincher_arm_moveit_config pincher_arm_moveit.launch
```
and perform the path planning operations in RViz.

[PhantomX Turret Kit]: https://www.roscomponents.com/en/pan-tilts/130-phantomx-robot-turret-kit.html#/assembled-no/trossen_phantomx_turret_version-ax_12a
[turtlebot_arm]: https://github.com/turtlebot/turtlebot_arm
[arbotix_ros]: https://github.com/corb555/arbotix_ros
[vanadiumlabs/arbotix_ros#28]: https://github.com/vanadiumlabs/arbotix_ros/pull/28
[fictionlab/pincher_arm]: https://github.com/fictionlab/pincher_arm
[catkin]: http://docs.ros.org/en/api/catkin/html/
[rosdep]: http://wiki.ros.org/rosdep
