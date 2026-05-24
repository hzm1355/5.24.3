#!/usr/bin/env python3
"""
Ground Truth Recorder for Gazebo
Records robot ground truth pose from Gazebo model states
Used for ATE (Absolute Trajectory Error) calculation
ROS2 Version
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, Twist
import os


class GroundTruthRecorder(Node):
    def __init__(self):
        super().__init__('gt_recorder')

        # 参数
        self.declare_parameter('output_file', '/tmp/gt.txt')
        self.declare_parameter('robot_name', 'inspection_robot')

        self.output_file = self.get_parameter('output_file').value
        self.robot_name = self.get_parameter('robot_name').value

        # 确保目录存在
        output_dir = os.path.dirname(self.output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # 打开文件
        self.file = open(self.output_file, 'w')
        self.file.write("# timestamp(s) x(m) y(m) z(m) qx qy qz qw vx vy vz wx wy wz\n")

        self.get_logger().info(f'Ground Truth Recorder started, output: {self.output_file}')

        # 订阅 Gazebo 模型状态
        # 注意: ROS2 中需要使用 /model_states 或 /joint_states
        self.gt_sub = self.create_subscription(
            Odometry,
            '/model/inspection_robot/pose',
            self.pose_callback,
            10
        )

        # 如果上述话题不存在，尝试订阅 robot odometry
        self.robot_odom_sub = self.create_subscription(
            Odometry,
            '/robot/odom',
            self.odom_callback,
            10
        )

        # 发布 Ground Truth Odometry
        self.gt_pub = self.create_publisher(Odometry, '/ground_truth', 10)

    def pose_callback(self, msg: Odometry):
        """处理 Gazebo 发布的位姿"""
        self.record_and_publish(msg)

    def odom_callback(self, msg: Odometry):
        """处理里程计数据（作为 Ground Truth）"""
        self.record_and_publish(msg)

    def record_and_publish(self, msg: Odometry):
        """记录并发布 Ground Truth"""
        # 时间戳
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        # 位置和方向
        pos = msg.pose.pose.position
        ori = msg.pose.pose.orientation
        twist = msg.twist.twist

        # 写入文件
        line = f"{timestamp:.6f} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f} "
        line += f"{ori.x:.6f} {ori.y:.6f} {ori.z:.6f} {ori.w:.6f} "
        line += f"{twist.linear.x:.6f} {twist.linear.y:.6f} {twist.linear.z:.6f} "
        line += f"{twist.angular.x:.6f} {twist.angular.y:.6f} {twist.angular.z:.6f}\n"
        self.file.write(line)
        self.file.flush()

        # 发布 Odometry 消息
        gt_odom = Odometry()
        gt_odom.header.stamp = msg.header.stamp
        gt_odom.header.frame_id = 'world'
        gt_odom.child_frame_id = 'base_link'
        gt_odom.pose.pose = msg.pose.pose
        gt_odom.twist.twist = msg.twist.twist
        self.gt_pub.publish(gt_odom)

    def destroy_node(self):
        self.file.close()
        self.get_logger().info(f'Ground Truth saved to: {self.output_file}')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = GroundTruthRecorder()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
