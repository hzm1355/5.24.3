#!/bin/bash
# 修复 ROS 源冲突

echo "修复 ROS 源冲突..."

# 检查 Ubuntu 版本
VERSION=$(lsb_release -sc)
echo "当前 Ubuntu 版本: $VERSION"

# 如果是 22.04 (jammy)，ROS1 Noetic 不支持，需要用 Ubuntu 20.04 源
if [ "$VERSION" = "jammy" ]; then
    echo "检测到 Ubuntu 22.04 (Jammy)"
    echo "注意: ROS1 Noetic 主要支持 Ubuntu 20.04"
    echo "将尝试安装 ROS1，但可能需要额外配置..."
    
    # 修复软件源 - 使用 focal 代替 jammy
    sudo sed -i 's/jammy/focal/g' /etc/apt/sources.list.d/ros-latest.list
    echo "已将软件源从 jammy 改为 focal"
fi

# 删除重复的源
sudo rm -f /etc/apt/sources.list.d/archive_uri-http_packages_ros_org_ros2_ubuntu-jammy.list

# 更新
sudo apt update
