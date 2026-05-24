#!/usr/bin/env python3
"""
Deep Pit Inspection Simulation - Gazebo Launch with Xacro
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    pkg_share = FindPackageShare(package='deep_pit_simulation').find('deep_pit_simulation')
    
    # URDF 文件 (xacro 转换后)
    urdf_file = os.path.join(pkg_share, 'urdf', 'inspection_robot.urdf')
    
    # Xacro 文件
    xacro_file = os.path.join(pkg_share, 'urdf', 'inspection_robot.xacro')
    
    # World 文件
    world_file = os.path.join(pkg_share, 'worlds', 'deep_pit_spiral_ramp.world')
    
    # RViz 配置
    rviz_config = os.path.join(pkg_share, 'rviz', 'simulation.rviz')
    
    # 声明参数
    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock'
    )
    
    return LaunchDescription([
        # Gazebo 服务器
        ExecuteProcess(
            cmd=['gazebo', '--verbose', world_file, '-s', 'libgazebo_ros_factory.so', '-s', 'libgazebo_ros_init.so'],
            output='screen',
            shell=False
        ),
        
        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'robot_description': open(urdf_file).read()
            }]
        ),
        
        # Joint State Publisher
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            parameters=[{'use_sim_time': True}]
        ),
        
        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': True}],
            output='screen'
        ),
    ])
