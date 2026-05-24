#!/bin/bash
#===============================================================================
# 深基坑巡检系统 - 快速启动脚本 (ROS Noetic)
#===============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  深基坑机器人巡检系统 - ROS1 启动器${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查 ROS 环境
if [ -z "$ROS_DISTRO" ]; then
    echo -e "${RED}错误: ROS 环境未激活${NC}"
    echo "请运行: source /opt/ros/noetic/setup.bash"
    exit 1
fi

echo -e "${YELLOW}ROS 版本: $ROS_DISTRO${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_DIR="${HOME}/catkin_ws"

echo -e "${YELLOW}工作空间: $WORKSPACE_DIR${NC}"

# 启动 roscore (如果未运行)
if ! pgrep -x "roscore" > /dev/null; then
    echo -e "${YELLOW}启动 roscore...${NC}"
    roscore &
    sleep 3
else
    echo -e "${GREEN}roscore 已在运行${NC}"
fi

# 发布静态 TF
echo -e "${YELLOW}发布静态 TF (world → map)...${NC}"
rosrun tf static_transform_publisher 0 0 0 0 0 0 world map 100 &

# 启动机器人状态发布器
if [ -f "$WORKSPACE_DIR/src/robot_state_publisher/launch/robot_state_publisher.launch" ]; then
    echo -e "${YELLOW}启动机器人状态发布器...${NC}"
    roslaunch robot_state_publisher robot_state_publisher.launch &
fi

# 启动可视化节点
echo -e "${YELLOW}启动可视化数据节点...${NC}"
if [ -f "$SCRIPT_DIR/deep_pit_visualization.py" ]; then
    python3 "$SCRIPT_DIR/deep_pit_visualization.py" &
    VIS_PID=$!
else
    echo -e "${RED}错误: 找不到 deep_pit_visualization.py${NC}"
    exit 1
fi

# 等待节点启动
sleep 2

# 检查话题
echo -e "${YELLOW}\n可用话题列表:${NC}"
rostopic list | grep -E "(trajectory|surfel|support|pit|laser|odometry|current_pose)" || echo "无匹配话题"

# 启动 RViz
if [ -f "$SCRIPT_DIR/robot_config.rviz" ]; then
    echo -e "${GREEN}\n启动 RViz...${NC}"
    rviz -d "$SCRIPT_DIR/robot_config.rviz" &
elif [ -f "$WORKSPACE_DIR/src/deep_pit_inspection/rviz/deep_pit_config.rviz" ]; then
    echo -e "${GREEN}\n启动 RViz...${NC}"
    rviz -d "$WORKSPACE_DIR/src/deep_pit_inspection/rviz/deep_pit_config.rviz" &
else
    echo -e "${YELLOW}\n未找到 RViz 配置文件，请手动启动 rviz${NC}"
fi

echo -e "${GREEN}\n系统已启动${NC}"
echo -e "按 Ctrl+C 关闭所有节点..."

# 等待用户中断
wait $VIS_PID 2>/dev/null || true

# 清理
echo -e "${YELLOW}\n关闭所有节点...${NC}"
killall static_transform_publisher 2>/dev/null || true
killall robot_state_publisher 2>/dev/null || true
killall rviz 2>/dev/null || true

echo -e "${GREEN}已关闭${NC}"
