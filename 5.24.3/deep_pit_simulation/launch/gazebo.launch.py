#!/usr/bin/env python3
"""
Deep Pit Inspection Simulation - Gazebo Launch
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('deep_pit_simulation')
    
    # URDF 文件路径
    urdf_file = os.path.join(pkg_share, 'urdf', 'inspection_robot.urdf')
    
    # World 文件路径
    world_file = os.path.join(pkg_share, 'worlds', 'deep_pit.world')
    
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
        
        # Joint State Publisher (Gazebo)
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
