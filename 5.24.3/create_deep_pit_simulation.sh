#!/bin/bash
# 深基坑仿真系统 - ROS2 创建脚本
# 在 ~/ros2_ws/src/ 目录下运行

cd ~/ros2_ws/src

# 创建包
ros2 pkg create --build-type ament_python deep_pit_simulation \
  --dependencies rclpy std_msgs geometry_msgs nav_msgs sensor_msgs visualization_msgs tf2 tf2_ros

# 创建目录结构
cd deep_pit_simulation
mkdir -p urdf worlds models launch config scripts rviz

echo "创建完成!"
ls -la
