#!/usr/bin/env python3
"""
Automatic Trajectory Publisher for Deep Pit Inspection
Publishes spiral descent or standard patrol trajectory velocity commands
ROS2 Version
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Path
import numpy as np
import math


class TrajectoryPublisher(Node):
    def __init__(self):
        super().__init__('trajectory_publisher')

        # 参数
        self.declare_parameter('trajectory_type', 'spiral')
        self.declare_parameter('spiral_radius', 4.0)
        self.declare_parameter('descent_rate', 0.4)  # m/rad
        self.declare_parameter('angular_speed', 0.5)  # rad/s
        self.declare_parameter('linear_speed', 0.3)  # m/s
        self.declare_parameter('duration', 120.0)  # s
        self.declare_parameter('pit_depth', 5.0)  # 基坑深度

        self.trajectory_type = self.get_parameter('trajectory_type').value
        self.spiral_radius = self.get_parameter('spiral_radius').value
        self.descent_rate = self.get_parameter('descent_rate').value
        self.angular_speed = self.get_parameter('angular_speed').value
        self.linear_speed = self.get_parameter('linear_speed').value
        self.duration = self.get_parameter('duration').value
        self.pit_depth = self.get_parameter('pit_depth').value

        # 发布器
        self.cmd_pub = self.create_publisher(Twist, '/robot/cmd_vel', 10)
        self.path_pub = self.create_publisher(Path, '/planned_trajectory', 10)

        # 状态
        self.current_angle = 0.0
        self.start_time = self.get_clock().now()
        self.path = Path()
        self.path.header.frame_id = 'world'

        self.get_logger().info(f'Trajectory Publisher started: {self.trajectory_type}')
        self.get_logger().info(f'Spiral radius: {self.spiral_radius}m, descent rate: {self.descent_rate}m/rad')

        # 定时器 50Hz
        self.timer = self.create_timer(0.02, self.timer_callback)

    def timer_callback(self):
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9

        if elapsed > self.duration:
            # 停止机器人
            self.cmd_pub.publish(Twist())
            self.get_logger().info('Trajectory completed, stopping')
            return

        if self.trajectory_type == 'spiral':
            cmd = self.generate_spiral_cmd(elapsed)
        elif self.trajectory_type == 'standard':
            cmd = self.generate_standard_cmd(elapsed)
        else:
            cmd = Twist()

        self.cmd_pub.publish(cmd)

        # 发布路径可视化
        self.publish_trajectory_visualization(elapsed)

    def generate_spiral_cmd(self, t):
        """Generate spiral trajectory velocity command"""
        # Current angle
        self.current_angle = self.angular_speed * t

        # Spiral parametric equations: x = r*cos(θ), y = r*sin(θ), z = -k*θ
        # Tangent vector: dx/dθ = -r*sin(θ), dy/dθ = r*cos(θ), dz/dθ = -k

        dx_dtheta = -self.spiral_radius * math.sin(self.current_angle)
        dy_dtheta = self.spiral_radius * math.cos(self.current_angle)
        dz_dtheta = -self.descent_rate

        # Normalize tangent vector
        tangent = np.array([dx_dtheta, dy_dtheta, dz_dtheta])
        tangent = tangent / np.linalg.norm(tangent)

        # Calculate velocity command
        cmd = Twist()
        cmd.linear.x = self.linear_speed * tangent[0]
        cmd.linear.y = self.linear_speed * tangent[1]
        cmd.linear.z = self.linear_speed * tangent[2]
        cmd.angular.z = self.angular_speed

        # Limit depth
        current_depth = self.descent_rate * self.current_angle / self.angular_speed
        if current_depth > self.pit_depth:
            cmd.linear.z = 0

        return cmd

    def generate_standard_cmd(self, t):
        """Generate standard patrol trajectory velocity command"""
        cmd = Twist()

        if t < 30:
            # Phase 1: Enter pit (linear + descent)
            cmd.linear.x = 0.2
            cmd.linear.z = -0.1
            cmd.angular.z = 0.1
        elif t < 90:
            # Phase 2: Circular patrol
            cmd.linear.x = 0.3
            cmd.linear.z = -0.05
            cmd.angular.z = 0.2
        else:
            # Phase 3: Return to surface
            cmd.linear.x = 0.2
            cmd.linear.z = 0.1
            cmd.angular.z = -0.1

        return cmd

    def publish_trajectory_visualization(self, t):
        """Publish trajectory for RViz visualization"""
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = 'world'

        if self.trajectory_type == 'spiral':
            # Calculate position
            x = self.spiral_radius * math.cos(self.current_angle)
            y = self.spiral_radius * math.sin(self.current_angle)
            z = -self.descent_rate * self.current_angle / self.angular_speed
            z = max(z, -self.pit_depth)
        else:
            # For standard trajectory, estimate position
            x = 0.1 * t * math.cos(0.1 * t) if t < 30 else 4.0 * math.cos(0.2 * (t - 30))
            y = 0.1 * t * math.sin(0.1 * t) if t < 30 else 4.0 * math.sin(0.2 * (t - 30))
            z = -0.1 * t if t < 30 else (-3.0 + 0.1 * (t - 90)) if t > 90 else -3.0

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z

        self.path.header.stamp = pose.header.stamp
        self.path.poses.append(pose)
        self.path_pub.publish(self.path)


def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop robot before shutdown
        cmd = Twist()
        node.cmd_pub.publish(cmd)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
