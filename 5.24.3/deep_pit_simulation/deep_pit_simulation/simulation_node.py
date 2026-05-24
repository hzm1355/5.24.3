#!/usr/bin/env python3
"""
Deep Pit Inspection Simulation Node
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan, Imu
from nav_msgs.msg import Odometry
import numpy as np


class SimulationNode(Node):
    def __init__(self):
        super().__init__('simulation_node')
        
        # 订阅激光雷达
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/robot/scan',
            self.lidar_callback,
            10
        )
        
        # 订阅里程计
        self.odom_sub = self.create_subscription(
            Odometry,
            '/robot/odom',
            self.odom_callback,
            10
        )
        
        # 订阅IMU
        self.imu_sub = self.create_subscription(
            Imu,
            '/robot/imu/data',
            self.imu_callback,
            10
        )
        
        # 发布速度命令
        self.cmd_pub = self.create_publisher(Twist, '/robot/cmd_vel', 10)
        
        # 定时器
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        self.get_logger().info('Deep Pit Simulation Node Started')
        
    def lidar_callback(self, msg):
        # 处理激光数据
        ranges = np.array(msg.ranges)
        valid_ranges = ranges[np.isfinite(ranges)]
        if len(valid_ranges) > 0:
            min_dist = np.min(valid_ranges)
            max_dist = np.max(valid_ranges)
            # self.get_logger().info(f'Lidar: min={min_dist:.2f}m, max={max_dist:.2f}m')
            
    def odom_callback(self, msg):
        # 处理里程计数据
        pos = msg.pose.pose.position
        # self.get_logger().info(f'Position: x={pos.x:.2f}, y={pos.y:.2f}')
        
    def imu_callback(self, msg):
        # 处理IMU数据
        ori = msg.orientation
        # self.get_logger().info(f'IMU: w={ori.w:.2f}')
        
    def timer_callback(self):
        # 简单的测试命令 - 前进
        cmd = Twist()
        cmd.linear.x = 0.5
        cmd.angular.z = 0.0
        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = SimulationNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
