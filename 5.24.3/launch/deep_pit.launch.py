#!/usr/bin/env python3
"""
ROS 2 Launch file for Deep Pit Inspection System
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='deep_pit_inspection',
            executable='deep_pit_visualization',
            name='deep_pit_visualization',
            output='screen',
            parameters=[{
                'pit_diameter': 10.0,
                'pit_depth': 5.0,
                'num_piles': 6,
                'pile_diameter': 0.8,
            }]
        ),
    ])
