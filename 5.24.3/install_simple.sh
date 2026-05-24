#!/bin/bash
# ROS Noetic 快速安装脚本
echo "========================================"
echo "  ROS Noetic 安装"
echo "========================================"

# 1. 添加软件源
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654

# 2. 更新
sudo apt update

# 3. 安装 ROS
sudo apt install -y ros-noetic-desktop-full

# 4. 配置环境
echo 'source /opt/ros/noetic/setup.bash' >> ~/.bashrc
source ~/.bashrc

# 5. 安装工具
sudo apt install -y python3-rosdep python3-catkin-tools

# 6. 初始化 rosdep
sudo rosdep init

# 7. 安装 Gazebo
sudo apt install -y ros-noetic-gazebo-*

# 8. 安装可视化
sudo apt install -y ros-noetic-rviz ros-noetic-rqt

echo "========================================"
echo "  安装完成!"
echo "========================================"
echo "运行: source ~/.bashrc"
