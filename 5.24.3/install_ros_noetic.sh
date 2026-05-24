#!/bin/bash
#===============================================================================
# 深基坑巡检系统 - ROS Noetic 完整安装脚本
# 运行方式: chmod +x install_ros_noetic.sh && ./install_ros_noetic.sh
#===============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查是否为 Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
    echo -e "${RED}错误: 此脚本仅支持 Ubuntu 系统${NC}"
    exit 1
fi

# 获取 Ubuntu 版本
UBUNTU_CODENAME=$(lsb_release -sc)
echo -e "${BLUE}检测到 Ubuntu: $UBUNTU_CODENAME${NC}"

# 检查 ROS 是否已安装
if [ -f /opt/ros/noetic/setup.bash ]; then
    echo -e "${GREEN}ROS Noetic 已安装${NC}"
    INSTALLED=true
else
    echo -e "${YELLOW}ROS Noetic 未安装，开始安装...${NC}"
    INSTALLED=false
fi

#===============================================================================
# 步骤 1: 添加 ROS 软件源
#===============================================================================
install_ros() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}步骤 1: 添加 ROS 软件源${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
    sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
    
    echo -e "${GREEN}软件源已添加${NC}"
}

#===============================================================================
# 步骤 2: 安装 ROS Noetic
#===============================================================================
install_ros_noetic() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}步骤 2: 安装 ROS Noetic Desktop Full${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    sudo apt update
    sudo apt install -y ros-noetic-desktop-full
    
    echo -e "${GREEN}ROS Noetic 安装完成${NC}"
}

#===============================================================================
# 步骤 3: 配置 ROS 环境
#===============================================================================
configure_ros_env() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}步骤 3: 配置 ROS 环境${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # 添加到 .bashrc
    if ! grep -q "source /opt/ros/noetic/setup.bash" ~/.bashrc; then
        echo 'source /opt/ros/noetic/setup.bash' >> ~/.bashrc
        echo -e "${GREEN}已添加 ROS 环境到 ~/.bashrc${NC}"
    else
        echo -e "${YELLOW}ROS 环境已存在于 ~/.bashrc${NC}"
    fi
    
    # 安装 rosdep
    sudo apt install -y python3-rosdep
    sudo rosdep init
    
    echo -e "${GREEN}ROS 环境配置完成${NC}"
}

#===============================================================================
# 步骤 4: 安装 Gazebo 相关包
#===============================================================================
install_gazebo() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}步骤 4: 安装 Gazebo 相关包${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    sudo apt install -y \
        ros-noetic-gazebo-ros-pkgs \
        ros-noetic-gazebo-ros-control \
        ros-noetic-gazebo-plugins
    
    echo -e "${GREEN}Gazebo 相关包安装完成${NC}"
}

#===============================================================================
# 步骤 5: 安装机器人相关包
#===============================================================================
install_robot_packages() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}步骤 5: 安装机器人相关包${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    sudo apt install -y \
        ros-noetic-robot-state-publisher \
        ros-noetic-joint-state-publisher \
        ros-noetic-xacro \
        ros-noetic-teleop-twist-keyboard
    
    echo -e "${GREEN}机器人相关包安装完成${NC}"
}

#===============================================================================
# 步骤 6: 安装传感器驱动 (可选)
#===============================================================================
install_sensor_drivers() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}步骤 6: 安装传感器驱动 (仿真可选)${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    read -p "是否安装传感器驱动? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo apt install -y \
            ros-noetic-rplidar-ros \
            ros-noetic-realsense2-camera
        echo -e "${GREEN}传感器驱动安装完成${NC}"
    else
        echo -e "${YELLOW}跳过传感器驱动安装${NC}"
    fi
}

#===============================================================================
# 步骤 7: 安装可视化工具
#===============================================================================
install_visualization() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}步骤 7: 安装可视化工具${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    sudo apt install -y \
        ros-noetic-rviz \
        ros-noetic-rqt \
        ros-noetic-rqt-common-plugins
    
    echo -e "${GREEN}可视化工具安装完成${NC}"
}

#===============================================================================
# 步骤 8: 创建 Catkin 工作空间
#===============================================================================
create_workspace() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}步骤 8: 创建 Catkin 工作空间${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    if [ -d ~/catkin_ws ]; then
        echo -e "${YELLOW}工作空间 ~/catkin_ws 已存在${NC}"
    else
        mkdir -p ~/catkin_ws/src
        cd ~/catkin_ws/src
        catkin_init_workspace
        cd ~/catkin_ws
        catkin_make
        
        # 添加到 .bashrc
        if ! grep -q "source ~/catkin_ws/devel/setup.bash" ~/.bashrc; then
            echo 'source ~/catkin_ws/devel/setup.bash' >> ~/.bashrc
        fi
        
        echo -e "${GREEN}Catkin 工作空间创建完成${NC}"
    fi
}

#===============================================================================
# 主流程
#===============================================================================
main() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  深基坑巡检系统 - ROS Noetic 安装向导${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${YELLOW}按 Ctrl+C 可随时退出${NC}\n"
    
    # Source ROS 环境
    if [ -f /opt/ros/noetic/setup.bash ]; then
        source /opt/ros/noetic/setup.bash
    fi
    
    if [ "$INSTALLED" = false ]; then
        install_ros
        install_ros_noetic
    fi
    
    configure_ros_env
    install_gazebo
    install_robot_packages
    install_sensor_drivers
    install_visualization
    create_workspace
    
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  安装完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "\n请运行以下命令使环境生效:"
    echo -e "  ${YELLOW}source ~/.bashrc${NC}"
    echo -e "\n或重新打开终端"
}

# 运行
main "$@"
