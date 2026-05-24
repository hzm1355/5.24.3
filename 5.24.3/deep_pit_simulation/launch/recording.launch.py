#!/usr/bin/env python3
"""
Deep Pit Dataset Recording Launch
ROS2 Launch File
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os


def generate_launch_description():
    # 数据集保存目录
    home = os.path.expanduser('~')
    dataset_dir = os.path.join(home, 'datasets')
    
    # 确保目录存在
    os.makedirs(dataset_dir, exist_ok=True)
    
    # 录制文件路径
    bag_file = os.path.join(dataset_dir, 'deep_pit_dataset.bag')
    gt_file = os.path.join(dataset_dir, 'ground_truth.txt')

    return LaunchDescription([
        # 包含主仿真
        # 取消注释下一行以同时启动仿真
        # Include 并发启动 simulation.launch
        
        # ========== Rosbag2 录制 ==========
        Node(
            package='rosbag2_transport',
            executable='record',
            name='rosbag2_record',
            arguments=[
                '-o', bag_file,
                '/robot/scan',
                '/robot/camera/rgb/image_raw',
                '/robot/camera/depth/image_raw',
                '/robot/imu/data',
                '/robot/odom',
                '/tf',
                '/tf_static',
                '/joint_states',
            ],
            output='screen'
        ),
        
        # ========== Ground Truth 录制 ==========
        Node(
            package='deep_pit_simulation',
            executable='gt_recorder',
            name='gt_recorder',
            parameters=[{
                'output_file': gt_file
            }],
            output='screen'
        ),
    ])
