#!/bin/bash
#===============================================================================
# 深基坑巡检系统 - ROS2 Humble 安装脚本
# 适用于 Ubuntu 22.04
#===============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  深基坑巡检系统 - ROS2 Humble 安装${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查 Ubuntu 版本
UBUNTU_CODENAME=$(lsb_release -sc)
echo "检测到 Ubuntu: $UBUNTU_CODENAME"

if [ "$UBUNTU_CODENAME" != "jammy" ]; then
    echo -e "${YELLOW}警告: 推荐使用 Ubuntu 22.04 (Jammy)${NC}"
fi

# 步骤 1: 添加 ROS2 源
echo -e "\n${GREEN}步骤 1: 添加 ROS2 软件源${NC}"
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y universe
sudo apt update
sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo apt-key add -
sudo sh -c 'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" > /etc/apt/sources.list.d/ros2.list'

# 步骤 2: 安装 ROS2 Humble
echo -e "\n${GREEN}步骤 2: 安装 ROS2 Humble Desktop${NC}"
sudo apt update
sudo apt install -y ros-humble-desktop

# 步骤 3: 安装工具
echo -e "\n${GREEN}步骤 3: 安装构建工具${NC}"
sudo apt install -y python3-colcon-common-extensions python3-vcstool python3-argparse

# 步骤 4: 配置环境
echo -e "\n${GREEN}步骤 4: 配置环境${NC}"
echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
source /opt/ros/humble/setup.bash

# 步骤 5: 创建工作空间
echo -e "\n${GREEN}步骤 5: 创建工作空间${NC}"
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
colcon build
source install/setup.bash
echo 'source ~/ros2_ws/install/setup.bash' >> ~/.bashrc

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  安装完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n请运行: source ~/.bashrc"
echo -e "验证安装: ros2 version"
