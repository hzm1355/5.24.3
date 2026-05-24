#!/usr/bin/env python3
"""
Deep Pit Inspection - Complete Launch with Robot Spawning
ROS2 Launch File
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.events.lifecycle import ChangeState
from launch_ros.event_handlers import OnStateTransition
from lifecycle_msgs.msg import Configure
import os


def generate_launch_description():
    pkg_share = os.path.join(os.path.expanduser('~'), 'ros2_ws', 'src', 'deep_pit_simulation')
    
    # 参数
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    # URDF/Xacro 文件
    robot_xacro = os.path.join(pkg_share, 'urdf', 'robot.xacro')
    
    # World 文件
    world_file = os.path.join(pkg_share, 'worlds', 'deep_pit_spiral_ramp.world')
    
    # 控制器配置文件
    controller_config = os.path.join(pkg_share, 'config', 'robot_controllers.yaml')
    
    # RViz 配置
    rviz_config = os.path.join(pkg_share, 'rviz', 'simulation.rviz')

    return LaunchDescription([
        # 声明参数
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock'
        ),
        
        # ========== Gazebo ==========
        Node(
            package='gazebo_ros',
            executable='gazebo',
            arguments=[world_file, '--verbose', '-s', 'libgazebo_ros_factory.so', '-s', 'libgazebo_ros_init.so'],
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]
        ),
        
        # ========== Robot State Publisher ==========
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': open(os.path.join(pkg_share, 'urdf', 'inspection_robot.urdf')).read()
            }]
        ),
        
        # ========== Spawn Robot in Gazebo ==========
        Node(
            package='gazebo_ros',
            executable='spawn_model',
            name='spawn_inspection_robot',
            arguments=[
                '-param', 'robot_description',
                '-urdf',
                '-model', 'inspection_robot',
                '-x', '4.5', '-y', '0', '-z', '0.5', '-Y', '0'
            ],
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]
        ),
        
        # ========== Joint State Publisher ==========
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            parameters=[{'use_sim_time': use_sim_time}]
        ),
        
        # ========== Robot Controllers ==========
        # 注意: ROS2 需要使用 ros2_control 插件
        # 此处使用 Gazebo 内置的 diff_drive 插件
        
        # ========== RViz ==========
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'
        ),
        
        # ========== Teleop (可选) ==========
        # 取消注释以下行以启用键盘控制
        # Node(
        #     package='teleop_twist_keyboard',
        #     executable='teleop_twist_keyboard',
        #     name='teleop_twist_keyboard',
        #     output='screen',
        #     remappings=[
        #         ('/cmd_vel', '/robot/cmd_vel')
        #     ]
        # ),
    ])
