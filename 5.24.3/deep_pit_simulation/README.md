# Deep Pit Inspection Robot Simulation

深基坑机器人巡检仿真系统 - ROS2 Humble + Gazebo

## 项目结构

```
deep_pit_simulation/
├── package.xml                              # 包描述
├── setup.py                                 # 安装脚本
├── README.md                                # 本文件
├── deep_pit_simulation/                     # Python 包
│   ├── __init__.py
│   └── simulation_node.py                   # 仿真节点
├── launch/                                  # 启动文件
│   ├── gazebo.launch.py                     # Gazebo 基础版
│   ├── gazebo_xacro.launch.py              # Xacro版
│   └── inspection_robot.launch.py          # 完整版
├── urdf/                                    # 机器人模型
│   ├── robot.xacro                         # 主模型 (模块化)
│   ├── robot_base.xacro                     # 底盘宏
│   ├── sensors.xacro                        # 传感器宏
│   ├── materials.xacro                      # 材质定义
│   ├── inspection_robot.urdf               # 基础URDF
│   ├── inspection_robot.xacro              # Xacro版
│   └── inspection_robot_complete.xacro     # 完整版
├── worlds/                                  # Gazebo 世界
│   ├── deep_pit.world                      # 基础版
│   └── deep_pit_spiral_ramp.world          # 带螺旋坡道
├── config/                                   # 配置文件
│   └── robot_controllers.yaml               # ROS2 Control配置
└── rviz/                                   # RViz 配置
    └── simulation.rviz
```

## 安装依赖

```bash
# 安装 Gazebo 和 ROS2 插件
sudo apt update
sudo apt install -y ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros-control
sudo apt install -y ros-humble-robot-state-publisher ros-humble-xacro
sudo apt install -y xvfb  # 用于无头模式

# 如果没有安装 Gazebo
sudo apt install -y gazebo
```

## 编译

```bash
cd ~/ros2_ws
colcon build --packages-select deep_pit_simulation
source install/setup.bash
```

## 运行仿真

### 方法1: 基础仿真 (世界)
```bash
xvfb-run -a gazebo ~/ros2_ws/src/deep_pit_simulation/worlds/deep_pit.world
```

### 方法2: 带螺旋坡道仿真
```bash
xvfb-run -a gazebo ~/ros2_ws/src/deep_pit_simulation/worlds/deep_pit_spiral_ramp.world
```

### 方法3: 使用 Launch 文件
```bash
ros2 launch deep_pit_simulation inspection_robot.launch.py
```

## 机器人模型

### 底盘 (robot_base.xacro)
- 尺寸: 0.6m x 0.5m x 0.3m
- 质量: 25kg
- 差速驱动 (左右轮)
- 前后万向轮

### 传感器
| 传感器 | 型号 | 参数 |
|--------|------|------|
| 激光雷达 | RPLIDAR A2 | 1440点, 12m范围, 360° |
| 深度相机 | RealSense D435i | RGB + 深度, 60°FOV |
| IMU | BMI055 | 200Hz, 加速度+角速度 |

## 话题

| 话题 | 类型 | 描述 |
|------|------|------|
| `/robot/cmd_vel` | geometry_msgs/Twist | 速度控制 |
| `/robot/odom` | nav_msgs/Odometry | 里程计 |
| `/robot/scan` | sensor_msgs/LaserScan | 激光扫描 |
| `/robot/imu/data` | sensor_msgs/Imu | IMU数据 |
| `/robot/camera/rgb/image_raw` | sensor_msgs/Image | RGB图像 |
| `/robot/camera/depth/image_raw` | sensor_msgs/Image | 深度图像 |

## 控制机器人

```bash
# 键盘控制
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# 或手动发布命令
ros2 topic pub /robot/cmd_vel geometry_msgs/Twist "{linear: {x: 0.5, y: 0, z: 0}, angular: {x: 0, y: 0, z: 0}}"
```

## 查看话题

```bash
# 列出所有话题
ros2 topic list

# 查看激光数据
ros2 topic echo /robot/scan

# 查看IMU数据
ros2 topic echo /robot/imu/data
```

## RViz 可视化

```bash
rviz2 -d ~/ros2_ws/src/deep_pit_simulation/rviz/simulation.rviz
```

## 仿真世界说明

### deep_pit.world
- 基坑直径: 12m (外径)
- 基坑深度: 5m
- 6根支护桩均匀分布在半径5m的圆上
- 圆柱形墙壁

### deep_pit_spiral_ramp.world
- 基坑直径: 12m
- 基坑深度: 5m
- 螺旋坡道 (半径2.5m, 7段斜坡, 下降约4m)
- 适合机器人导航测试

## 自定义

### 修改机器人参数
编辑 `urdf/robot_base.xacro`:
```xml
<xacro:property name="base_length" value="0.8"/>  <!-- 改长度 -->
<xacro:property name="wheel_radius" value="0.15"/>  <!-- 改轮子大小 -->
```

### 添加传感器
编辑 `urdf/robot.xacro`:
```xml
<xacro:your_sensor prefix="" parent_link="base_link" xyz="0 0 0.5" rpy="0 0 0"/>
```

### 修改仿真世界
编辑 `worlds/deep_pit_spiral_ramp.world`:
```xml
<physics type="ode">
  <real_time_update_rate>1000</real_time_update_rate>
  <max_step_size>0.001</max_step_size>
</physics>
```
