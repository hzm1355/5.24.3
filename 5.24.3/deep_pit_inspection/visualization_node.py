#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深基坑机器人巡检系统 - ROS2 可视化数据发布节点
"""

import rclpy
from rclpy.node import Node
import numpy as np
from geometry_msgs.msg import PoseStamped, TransformStamped
from nav_msgs.msg import Path
from sensor_msgs.msg import PointCloud2, PointField
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import ColorRGBA, Header
import tf_transformations
from tf2_ros import TransformBroadcaster
import struct


class DeepPitVisualizationNode(Node):
    def __init__(self):
        super().__init__('deep_pit_visualization')

        self.trajectory_pub = self.create_publisher(Path, '/trajectory', 10)
        self.ground_truth_pub = self.create_publisher(Path, '/ground_truth_path', 10)
        self.surfel_map_pub = self.create_publisher(MarkerArray, '/surfel_map', 10)
        self.pit_boundary_pub = self.create_publisher(Path, '/pit_boundary', 10)
        self.support_piles_pub = self.create_publisher(MarkerArray, '/support_piles', 10)
        self.measured_geometry_pub = self.create_publisher(MarkerArray, '/measured_geometry', 10)
        self.current_pose_pub = self.create_publisher(PoseStamped, '/current_pose', 10)
        self.laser_features_pub = self.create_publisher(PointCloud2, '/laser_features', 10)

        self.tf_broadcaster = TransformBroadcaster(self)

        self.trajectory = Path()
        self.trajectory.header.frame_id = "world"
        self.ground_truth_path = Path()
        self.ground_truth_path.header.frame_id = "world"

        self.pit_diameter = 10.0
        self.pit_depth = 5.0
        self.num_piles = 6
        self.pile_diameter = 0.8

        self.start_time = self.get_clock().now()
        self.timer = self.create_timer(0.1, self.timer_callback)

        self.publish_static_data()

        self.get_logger().info('深基坑巡检可视化节点已启动')
        self.get_logger().info(f'基坑直径: {self.pit_diameter}m, 深度: {self.pit_depth}m, 支护桩: {self.num_piles}根')

    def publish_static_data(self):
        self.get_logger().info('发布静态数据...')
        
        import time
        self.pit_boundary_pub.publish(self.create_pit_boundary())
        time.sleep(0.1)
        self.support_piles_pub.publish(self.create_support_piles())
        time.sleep(0.1)
        self.surfel_map_pub.publish(self.create_surfel_map())
        time.sleep(0.1)
        self.measured_geometry_pub.publish(self.create_measured_geometry())
        
        self.get_logger().info('静态数据已发布')

    def timer_callback(self):
        t = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        x, y, z = self.generate_trajectory_point(t)
        self.publish_tf(x, y, z, t)

        pose = PoseStamped()
        pose.header.frame_id = "world"
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        angle = 0.5 * t
        q = tf_transformations.quaternion_from_euler(0, 0, angle + np.pi/2)
        pose.pose.orientation.x = q[0]
        pose.pose.orientation.y = q[1]
        pose.pose.orientation.z = q[2]
        pose.pose.orientation.w = q[3]
        self.current_pose_pub.publish(pose)

        self.trajectory.header.stamp = self.get_clock().now().to_msg()
        self.trajectory.poses.append(pose)
        if len(self.trajectory.poses) > 1000:
            self.trajectory.poses.pop(0)
        self.trajectory_pub.publish(self.trajectory)

        gt_pose = PoseStamped()
        gt_pose.header = pose.header
        gt_x, gt_y, gt_z = self.generate_trajectory_point(t)
        gt_pose.pose.position.x = gt_x
        gt_pose.pose.position.y = gt_y
        gt_pose.pose.position.z = gt_z
        gt_pose.pose.orientation = pose.pose.orientation
        self.ground_truth_path.header.stamp = self.get_clock().now().to_msg()
        self.ground_truth_path.poses.append(gt_pose)
        if len(self.ground_truth_path.poses) > 1000:
            self.ground_truth_path.poses.pop(0)
        self.ground_truth_pub.publish(self.ground_truth_path)

        self.laser_features_pub.publish(self.create_laser_features(x, y, z))

    def create_pit_boundary(self):
        path = Path()
        path.header.frame_id = "world"
        path.header.stamp = self.get_clock().now().to_msg()
        radius = self.pit_diameter / 2
        for i in range(101):
            angle = 2 * np.pi * i / 100
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = radius * np.cos(angle)
            pose.pose.position.y = radius * np.sin(angle)
            pose.pose.position.z = 0.0
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        return path

    def create_support_piles(self):
        marker_array = MarkerArray()
        radius = self.pit_diameter / 2 - 0.5
        colors = [
            ColorRGBA(1.0, 0.0, 0.0, 1.0),
            ColorRGBA(1.0, 0.5, 0.0, 1.0),
            ColorRGBA(1.0, 1.0, 0.0, 1.0),
            ColorRGBA(0.0, 1.0, 0.0, 1.0),
            ColorRGBA(0.0, 0.0, 1.0, 1.0),
            ColorRGBA(0.5, 0.0, 0.5, 1.0),
        ]
        for i in range(self.num_piles):
            angle = 2 * np.pi * i / self.num_piles
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)

            marker = Marker()
            marker.header.frame_id = "world"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "support_piles"
            marker.id = i
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD
            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = -self.pit_depth / 2
            marker.pose.orientation.w = 1.0
            marker.scale.x = self.pile_diameter
            marker.scale.y = self.pile_diameter
            marker.scale.z = self.pit_depth
            marker.color = colors[i]
            marker_array.markers.append(marker)

            text = Marker()
            text.header = marker.header
            text.ns = "support_piles"
            text.id = i + 100
            text.type = Marker.TEXT_VIEW_FACING
            text.action = Marker.ADD
            text.pose.position.x = x
            text.pose.position.y = y
            text.pose.position.z = 0.5
            text.scale.z = 0.3
            text.color = ColorRGBA(1, 1, 1, 1)
            text.text = f"Pile {i+1}\nD={self.pile_diameter:.1f}m"
            marker_array.markers.append(text)

        return marker_array

    def create_surfel_map(self):
        marker_array = MarkerArray()
        now = self.get_clock().now().to_msg()
        np.random.seed(42)
        for i in range(200):
            angle = 2 * np.pi * i / 200
            height = -np.random.uniform(0, self.pit_depth)
            r = self.pit_diameter / 2
            marker = Marker()
            marker.header.frame_id = "world"
            marker.header.stamp = now
            marker.ns = "surfel_map"
            marker.id = i
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = r * np.cos(angle)
            marker.pose.position.y = r * np.sin(angle)
            marker.pose.position.z = height
            ratio = abs(height) / self.pit_depth
            marker.color = ColorRGBA(ratio, 0.2, 1.0 - ratio, 0.7)
            marker.scale.x = 0.15
            marker.scale.y = 0.15
            marker.scale.z = 0.05
            marker_array.markers.append(marker)

        for i in range(100):
            angle = 2 * np.pi * i / 100
            r = np.random.uniform(0, self.pit_diameter / 2 - 0.5)
            marker = Marker()
            marker.header.frame_id = "world"
            marker.header.stamp = now
            marker.ns = "surfel_map"
            marker.id = 1000 + i
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = r * np.cos(angle)
            marker.pose.position.y = r * np.sin(angle)
            marker.pose.position.z = -self.pit_depth
            marker.color = ColorRGBA(0.6, 0.4, 0.2, 0.8)
            marker.scale.x = 0.15
            marker.scale.y = 0.15
            marker.scale.z = 0.05
            marker_array.markers.append(marker)

        for pile_idx in range(self.num_piles):
            angle = 2 * np.pi * pile_idx / self.num_piles
            pile_r = self.pit_diameter / 2 - 0.5
            px = pile_r * np.cos(angle)
            py = pile_r * np.sin(angle)
            for h_idx in range(20):
                height = -h_idx * self.pit_depth / 20
                marker = Marker()
                marker.header.frame_id = "world"
                marker.header.stamp = now
                marker.ns = "surfel_map"
                marker.id = 2000 + pile_idx * 20 + h_idx
                marker.type = Marker.SPHERE
                marker.action = Marker.ADD
                marker.pose.position.x = px + np.random.normal(0, 0.02)
                marker.pose.position.y = py + np.random.normal(0, 0.02)
                marker.pose.position.z = height
                marker.color = ColorRGBA(1.0, 0.6, 0.0, 0.8)
                marker.scale.x = 0.1
                marker.scale.y = 0.1
                marker.scale.z = 0.1
                marker_array.markers.append(marker)

        return marker_array

    def create_measured_geometry(self):
        from geometry_msgs.msg import Point
        marker_array = MarkerArray()
        now = self.get_clock().now().to_msg()

        line = Marker()
        line.header.frame_id = "world"
        line.header.stamp = now
        line.ns = "measurement_lines"
        line.id = 1
        line.type = Marker.LINE_LIST
        line.action = Marker.ADD
        line.scale.x = 0.02
        line.color = ColorRGBA(0, 1, 0, 1)
        line.points = [
            Point(6, 0, 0), Point(6, 0, -self.pit_depth),
            Point(5.8, 0, 0), Point(6.2, 0, 0),
            Point(5.8, 0, -self.pit_depth), Point(6.2, 0, -self.pit_depth)
        ]
        marker_array.markers.append(line)

        text = Marker()
        text.header = line.header
        text.ns = "geometry_text"
        text.id = 10
        text.type = Marker.TEXT_VIEW_FACING
        text.action = Marker.ADD
        text.pose.position.x = 6.5
        text.pose.position.y = 0
        text.pose.position.z = -self.pit_depth / 2
        text.scale.z = 0.3
        text.color = ColorRGBA(0, 1, 0, 1)
        text.text = f"Depth: {self.pit_depth:.1f}m"
        marker_array.markers.append(text)

        diam = Marker()
        diam.header = line.header
        diam.ns = "measurement_lines"
        diam.id = 2
        diam.type = Marker.LINE_LIST
        diam.action = Marker.ADD
        diam.scale.x = 0.02
        diam.color = ColorRGBA(1, 0, 0, 1)
        r = self.pit_depth / 2
        diam.points = [
            Point(-r, 0, 0.5), Point(r, 0, 0.5),
            Point(-r, -0.2, 0.5), Point(-r, 0.2, 0.5),
            Point(r, -0.2, 0.5), Point(r, 0.2, 0.5)
        ]
        marker_array.markers.append(diam)

        diam_text = Marker()
        diam_text.header = line.header
        diam_text.ns = "geometry_text"
        diam_text.id = 11
        diam_text.type = Marker.TEXT_VIEW_FACING
        diam_text.action = Marker.ADD
        diam_text.pose.position.x = 0
        diam_text.pose.position.y = 0
        diam_text.pose.position.z = 1.0
        diam_text.scale.z = 0.3
        diam_text.color = ColorRGBA(1, 0, 0, 1)
        diam_text.text = f"Diameter: {self.pit_diameter:.1f}m"
        marker_array.markers.append(diam_text)

        return marker_array

    def generate_trajectory_point(self, t):
        radius = 4.0
        descent_rate = self.pit_depth / (2 * np.pi * 2)
        angular_speed = 0.5
        angle = angular_speed * t
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = -descent_rate * angle
        z = max(z, -self.pit_depth)
        return x, y, z

    def publish_tf(self, x, y, z, t):
        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = "world"
        transform.child_frame_id = "base_link"
        transform.transform.translation.x = float(x)
        transform.transform.translation.y = float(y)
        transform.transform.translation.z = float(z)
        angle = 0.5 * t
        q = tf_transformations.quaternion_from_euler(0, 0, angle + np.pi/2)
        transform.transform.rotation.x = q[0]
        transform.transform.rotation.y = q[1]
        transform.transform.rotation.z = q[2]
        transform.transform.rotation.w = q[3]
        self.tf_broadcaster.sendTransform(transform)

    def create_laser_features(self, x, y, z):
        points = []
        colors = []
        for angle in np.linspace(0, 2*np.pi, 20):
            r = self.pit_diameter / 2
            px = r * np.cos(angle)
            py = r * np.sin(angle)
            pz = z + np.random.normal(0, 0.01)
            points.append([px, py, pz])
            colors.append([255, 0, 0])

        for angle in np.linspace(0, 2*np.pi, 40):
            if abs(np.sin(angle * 6)) > 0.5:
                r = self.pit_diameter / 2
                px = r * np.cos(angle)
                py = r * np.sin(angle)
                pz = z + np.random.normal(0, 0.01)
                points.append([px, py, pz])
                colors.append([0, 0, 255])

        return self.create_pointcloud2(points, colors)

    def create_pointcloud2(self, points, colors):
        header = Header()
        header.frame_id = "world"
        header.stamp = self.get_clock().now().to_msg()

        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name='rgb', offset=12, datatype=PointField.UINT32, count=1),
        ]

        point_data = []
        for point, color in zip(points, colors):
            r, g, b = color
            rgb = struct.unpack('I', struct.pack('BBBB', b, g, r, 255))[0]
            point_data.append(struct.pack('fffI', point[0], point[1], point[2], rgb))

        data = b''.join(point_data)

        pc2 = PointCloud2()
        pc2.header = header
        pc2.height = 1
        pc2.width = len(points)
        pc2.fields = fields
        pc2.is_bigendian = False
        pc2.point_step = 16
        pc2.row_step = pc2.point_step * len(points)
        pc2.data = data
        pc2.is_dense = True

        return pc2


def main(args=None):
    rclpy.init(args=args)
    node = DeepPitVisualizationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
