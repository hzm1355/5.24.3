# Deep Pit Inspection Robot System

深基坑机器人巡检系统 - 支持 ROS1 Noetic 和 ROS2 Humble

---

## 系统要求

| 组件 | ROS1 (Noetic) | ROS2 (Humble) |
|------|---------------|---------------|
| 操作系统 | Ubuntu 20.04 LTS | Ubuntu 20.04+ / 22.04 |
| ROS 版本 | ROS Noetic | ROS2 Humble/Galactic/Iron |
| Gazebo | Gazebo 11 | Gazebo 11+ |
| Python | Python 3.8+ | Python 3.8+ |

---

## 快速开始

### ROS2 (推荐)

```bash
# 1. 创建工作空间
mkdir -p ~/deep_pit_ws/src
cp -r deep_pit_inspection ~/deep_pit_ws/src/

# 2. 编译
cd ~/deep_pit_ws
source /opt/ros/humble/setup.bash
colcon build

# 3. 运行
source install/setup.bash
ros2 launch deep_pit_inspection deep_pit.launch.py

# 4. 可视化
rviz2 -d ~/deep_pit_ws/src/deep_pit_inspection/rviz/deep_pit_config.rviz
```

### ROS1 Noetic

```bash
# 1. 创建工作空间
mkdir -p ~/catkin_ws/src
cp -r deep_pit_inspection ~/catkin_ws/src/

# 2. 编译
cd ~/catkin_ws
source /opt/ros/noetic/setup.bash
catkin_make

# 3. 运行
source devel/setup.bash
roscore &
python3 ~/catkin_ws/src/deep_pit_inspection/deep_pit_visualization.py
```

---

## 自动安装脚本

已在项目中包含 `install_ros_noetic.sh`，在 Ubuntu 上运行:

```bash
chmod +x install_ros_noetic.sh
./install_ros_noetic.sh
```

详细说明请查看 [INSTALL_GUIDE.md](INSTALL_GUIDE.md)

---

## 发布的话题

| 话题 | 类型 | 频率 | 描述 |
|------|------|------|------|
| `/trajectory` | nav_msgs/Path | 10Hz | 机器人螺旋下降轨迹 |
| `/ground_truth_path` | nav_msgs/Path | 10Hz | 真值轨迹 |
| `/surfel_map` | MarkerArray | Static | 面元地图 (墙壁/坑底/支护桩) |
| `/support_piles` | MarkerArray | Static | 6根支护桩 (带标注) |
| `/measured_geometry` | MarkerArray | Static | 几何测量标注 (深/直径) |
| `/pit_boundary` | nav_msgs/Path | Static | 基坑圆形边界 |
| `/current_pose` | PoseStamped | 10Hz | 当前位姿 |
| `/laser_features` | PointCloud2 | 10Hz | 激光边缘/平面特征 |
| `/tf` | tfMessage | 10Hz | base_link → world |

---

## 配置参数

| 参数 | 默认值 | 单位 | 描述 |
|------|--------|------|------|
| `pit_diameter` | 10.0 | m | 基坑直径 |
| `pit_depth` | 5.0 | m | 基坑深度 |
| `num_piles` | 6 | - | 支护桩数量 |
| `pile_diameter` | 0.8 | m | 支护桩直径 |

---

## 项目结构

```
deep_pit_inspection/
├── package.xml                    # ROS2 包描述
├── setup.py                      # Python 安装
├── CMakeLists.txt                # CMake 构建
├── README.md                     # 本文件
├── INSTALL_GUIDE.md              # 详细安装指南
├── install_ros_noetic.sh         # ROS1 自动安装脚本
├── start_ros1.sh                 # ROS1 启动脚本
├── start_ros2.sh                 # ROS2 启动脚本
├── resource/
│   └── deep_pit_inspection       # ROS2 资源标记
├── deep_pit_inspection/          # Python 包
│   ├── __init__.py
│   ├── __main__.py
│   └── visualization_node.py     # 主节点
├── launch/
│   └── deep_pit.launch.py        # ROS2 launch 文件
├── rviz/
│   └── deep_pit_config.rviz      # RViz 配置
├── deep_pit_visualization.py     # ROS1 版本
└── deep_pit_visualization_ros2.py # ROS2 版本 (独立)
```

---

## RViz 显示配置

加载配置文件后会自动显示:

- Grid (世界坐标系)
- TF (坐标系树)
- Path `/trajectory` (绿色)
- Path `/ground_truth_path` (红色)
- MarkerArray `/surfel_map` (渐变色面元)
- MarkerArray `/support_piles` (彩色圆柱)
- MarkerArray `/measured_geometry` (测量线)
- Path `/pit_boundary` (蓝色边界)
- Pose `/current_pose` (橙色箭头)
- PointCloud2 `/laser_features` (RGB彩色点云)

---

## Gazebo 仿真 (可选)

```bash
# ROS1 + Gazebo
roslaunch deep_pit_inspection gazebo.launch

# ROS2 + Gazebo
ros2 launch deep_pit_inspection gazebo.launch.py
```

---

## 故障排除

### 找不到包
```bash
# ROS2
source ~/deep_pit_ws/install/setup.bash
colcon build --packages-select deep_pit_inspection

# ROS1
source ~/catkin_ws/devel/setup.bash
cd ~/catkin_ws && catkin_make
```

### 依赖缺失
```bash
# Python 依赖
pip3 install numpy

# ROS1 依赖
rosdep install --from-paths src --ignore-src -r -y
```

---

## License

MIT
