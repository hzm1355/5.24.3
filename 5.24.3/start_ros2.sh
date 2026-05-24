#!/bin/bash
# 深基坑巡检系统 - ROS2 启动脚本

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  深基坑机器人巡检系统 - ROS2 启动器${NC}"
echo -e "${GREEN}========================================${NC}"

# 获取脚本所在目录的父目录 (工作空间根目录)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}工作空间: $WORKSPACE_DIR${NC}"

# Source ROS2 环境
if [ -f /opt/ros/humble/setup.bash ]; then
    source /opt/ros/humble/setup.bash
    echo -e "${GREEN}ROS2 Humble 环境已加载${NC}"
elif [ -f /opt/ros/galactic/setup.bash ]; then
    source /opt/ros/galactic/setup.bash
    echo -e "${GREEN}ROS2 Galactic 环境已加载${NC}"
elif [ -f /opt/ros/iron/setup.bash ]; then
    source /opt/ros/iron/setup.bash
    echo -e "${GREEN}ROS2 Iron 环境已加载${NC}"
else
    echo -e "${RED}错误: 未找到 ROS2 环境${NC}"
    exit 1
fi

# Source 工作空间
if [ -f "$WORKSPACE_DIR/install/setup.bash" ]; then
    source "$WORKSPACE_DIR/install/setup.bash"
    echo -e "${GREEN}工作空间环境已加载${NC}"
else
    echo -e "${YELLOW}警告: 工作空间尚未编译${NC}"
fi

# 检查依赖
echo -e "${YELLOW}检查依赖...${NC}"
python3 -c "import rclpy" 2>/dev/null && echo "rclpy: OK" || echo "rclpy: 缺失"
python3 -c "import numpy" 2>/dev/null && echo "numpy: OK" || echo "numpy: 缺失"

# 启动可视化节点
echo -e "${YELLOW}启动可视化节点...${NC}"
ros2 run deep_pit_inspection deep_pit_visualization &

# 等待节点启动
sleep 2

# 检查话题
echo -e "${YELLOW}\n可用话题列表:${NC}"
ros2 topic list | grep -E "(trajectory|surfel|support|pit|laser|odometry|current_pose)" || echo "无匹配话题"

echo -e "${GREEN}\n节点已启动${NC}"
echo -e "按 Ctrl+C 关闭..."
