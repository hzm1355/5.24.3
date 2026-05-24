# 深基坑巡检系统 - 安装指南 (ROS Noetic)

## 系统要求

- **操作系统**: Ubuntu 20.04 LTS
- **内存**: 至少 8GB (推荐 16GB)
- **硬盘**: 至少 50GB 可用空间
- **网络**: 需要互联网连接

---

## 快速安装

### 选项 1: 使用自动安装脚本 (推荐)

```bash
# 1. 将脚本复制到 Ubuntu
scp install_ros_noetic.sh user@ubuntu:/home/user/

# 2. 在 Ubuntu 上运行
chmod +x install_ros_noetic.sh
./install_ros_noetic.sh
```

### 选项 2: 手动安装

按顺序执行以下步骤:

---

## 步骤 1: 安装 ROS Noetic

```bash
# 添加 ROS 软件源
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654

# 更新软件包
sudo apt update

# 安装 ROS Noetic Desktop Full
sudo apt install ros-noetic-desktop-full
```

---

## 步骤 2: 配置 ROS 环境

```bash
# Source ROS 环境
source /opt/ros/noetic/setup.bash

# 添加到 ~/.bashrc (永久生效)
echo 'source /opt/ros/noetic/setup.bash' >> ~/.bashrc

# 安装并初始化 rosdep
sudo apt install python3-rosdep
sudo rosdep init
```

---

## 步骤 3: 安装 Gazebo 相关包

```bash
sudo apt install ros-noetic-gazebo-ros-pkgs
sudo apt install ros-noetic-gazebo-ros-control
sudo apt install ros-noetic-gazebo-plugins
```

---

## 步骤 4: 安装机器人相关包

```bash
sudo apt install ros-noetic-robot-state-publisher
sudo apt install ros-noetic-joint-state-publisher
sudo apt install ros-noetic-xacro
sudo apt install ros-noetic-teleop-twist-keyboard
```

---

## 步骤 5: 安装传感器驱动 (可选)

```bash
# 雷达驱动
sudo apt install ros-noetic-rplidar-ros

# 深度相机驱动
sudo apt install ros-noetic-realsense2-camera
```

---

## 步骤 6: 安装可视化工具

```bash
sudo apt install ros-noetic-rviz
sudo apt install ros-noetic-rqt
sudo apt install ros-noetic-rqt-common-plugins
```

---

## 步骤 7: 创建 Catkin 工作空间

```bash
# 创建工作空间
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
catkin_init_workspace

# 编译
cd ~/catkin_ws
catkin_make

# Source 工作空间
source devel/setup.bash

# 添加到 ~/.bashrc
echo 'source ~/catkin_ws/devel/setup.bash' >> ~/.bashrc
```

---

## 步骤 8: 复制项目文件

```bash
# 复制到工作空间
cp -r /path/to/deep_pit_inspection ~/catkin_ws/src/

# 编译
cd ~/catkin_ws
catkin_make
```

---

## 运行系统

### 启动可视化节点

```bash
# 方法 1: 使用启动脚本
./start_ros1.sh

# 方法 2: 手动启动
source ~/catkin_ws/devel/setup.bash
roscore &
python3 ~/catkin_ws/src/deep_pit_inspection/deep_pit_visualization.py

# 方法 3: RViz 可视化
rviz -d ~/catkin_ws/src/deep_pit_inspection/rviz/deep_pit_config.rviz
```

---

## 验证安装

```bash
# 检查 ROS 版本
rosversion -d

# 检查话题
rostopic list

# 检查节点
rosnode list

# 查看可视化节点输出
rosrun deep_pit_inspection deep_pit_visualization.py
```

---

## 常见问题

### Q: `rosdep: command not found`

```bash
sudo apt install python3-rosdep
```

### Q: `catkin_make: command not found`

```bash
sudo apt install python3-catkin-tools
```

### Q: Gazebo 无法启动

```bash
# 安装 Gazebo
sudo apt install gazebo

# 设置模型路径
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/catkin_ws/src/deep_pit_inspection/models
```

### Q: 权限问题

```bash
# 给脚本添加执行权限
chmod +x install_ros_noetic.sh
chmod +x start_ros1.sh
```
