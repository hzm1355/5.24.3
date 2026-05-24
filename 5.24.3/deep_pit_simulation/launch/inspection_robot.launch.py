#!/usr/bin/env python3
"""
Deep Pit Inspection - Complete Robot with Sensors Launch
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import Command
import os


def generate_launch_description():
    pkg_share = FindPackageShare(package='deep_pit_simulation').find('deep_pit_simulation')
    
    # Xacro 文件
    xacro_file = os.path.join(pkg_share, 'urdf', 'inspection_robot_complete.xacro')
    
    # World 文件
    world_file = os.path.join(pkg_share, 'worlds', 'deep_pit_spiral_ramp.world')
    
    # 声明参数
    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock'
    )
    
    # 生成 robot description from xacro
    robot_description = Command([
        'xacro ', xacro_file
    ])
    
    return LaunchDescription([
        # Gazebo 服务器
        ExecuteProcess(
            cmd=['gazebo', '--verbose', world_file, '-s', 'libgazebo_ros_factory.so', '-s', 'libgazebo_ros_init.so'],
            output='screen',
            shell=False
        ),
        
        # Robot State Publisher (使用 xacro)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'robot_description': robot_description
            }]
        ),
        
        # Joint State Publisher
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            parameters=[{'use_sim_time': True}]
        ),
        
        # 里程计到 TF
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='odom_to_base_tf',
            arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_link']
        ),
    ])
