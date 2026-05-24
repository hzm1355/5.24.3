#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深基坑机器人巡检系统 - ROS1 可视化数据发布节点
修复版: 确保所有话题正确发布
"""

import rospy
import numpy as np
from geometry_msgs.msg import Point, Pose, PoseStamped, Quaternion, Vector3, TransformStamped
from nav_msgs.msg import Odometry, Path
from sensor_msgs.msg import PointCloud2, PointField, LaserScan, Image
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import ColorRGBA, Header
import tf
import tf2_ros
from tf2_ros import TransformBroadcaster
import struct

class DeepPitVisualizationNode:
    def __init__(self):
        rospy.init_node('deep_pit_visualization', anonymous=True)

        # 发布器 - 使用较大的队列防止数据丢失
        self.trajectory_pub = rospy.Publisher('/trajectory', Path, queue_size=10, latch=False)
        self.ground_truth_pub = rospy.Publisher('/ground_truth_path', Path, queue_size=10, latch=False)
        self.surfel_map_pub = rospy.Publisher('/surfel_map', MarkerArray, queue_size=10, latch=True)
        self.pit_boundary_pub = rospy.Publisher('/pit_boundary', Path, queue_size=10, latch=True)
        self.support_piles_pub = rospy.Publisher('/support_piles', MarkerArray, queue_size=10, latch=True)
        self.measured_geometry_pub = rospy.Publisher('/measured_geometry', MarkerArray, queue_size=10, latch=True)
        self.current_pose_pub = rospy.Publisher('/current_pose', PoseStamped, queue_size=10)
        self.laser_features_pub = rospy.Publisher('/laser_features', PointCloud2, queue_size=10)

        # TF广播器
        self.tf_broadcaster = TransformBroadcaster()

        # 轨迹历史
        self.trajectory = Path()
        self.trajectory.header.frame_id = "world"
        self.ground_truth_path = Path()
        self.ground_truth_path.header.frame_id = "world"

        # 基坑参数
        self.pit_diameter = 10.0
        self.pit_depth = 5.0
        self.num_piles = 6
        self.pile_diameter = 0.8

        self.start_time = rospy.Time.now()
        self.static_published = False

        rospy.loginfo("=" * 50)
        rospy.loginfo("深基坑巡检可视化节点已启动")
        rospy.loginfo("基坑直径: %.1fm, 深度: %.1fm, 支护桩: %d根", 
                     self.pit_diameter, self.pit_depth, self.num_piles)
        rospy.loginfo("=" * 50)

    def create_pit_boundary(self):
        """基坑边界"""
        path = Path()
        path.header.frame_id = "world"
        path.header.stamp = rospy.Time.now()

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
        """支护桩"""
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

            # 圆柱体
            marker = Marker()
            marker.header.frame_id = "world"
            marker.header.stamp = rospy.Time.now()
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

            # 文字标注
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
            text.text = "Pile %d\nD=%.1fm" % (i+1, self.pile_diameter)
            marker_array.markers.append(text)

        return marker_array

    def create_surfel_map(self):
        """面元地图"""
        marker_array = MarkerArray()
        now = rospy.Time.now()

        # 围护墙面元 (蓝→红渐变)
        np.random.seed(42)  # 固定随机种子保证可重复
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

        # 坑底面元 (棕色)
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

        # 支护桩面元 (橙色)
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
        """几何测量标注"""
        marker_array = MarkerArray()
        now = rospy.Time.now()

        # 深度测量线
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

        # 深度文字
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
        text.text = "Depth: %.1fm" % self.pit_depth
        marker_array.markers.append(text)

        # 直径测量线
        diam = Marker()
        diam.header = line.header
        diam.ns = "measurement_lines"
        diam.id = 2
        diam.type = Marker.LINE_LIST
        diam.action = Marker.ADD
        diam.scale.x = 0.02
        diam.color = ColorRGBA(1, 0, 0, 1)
        r = self.pit_diameter / 2
        diam.points = [
            Point(-r, 0, 0.5), Point(r, 0, 0.5),
            Point(-r, -0.2, 0.5), Point(-r, 0.2, 0.5),
            Point(r, -0.2, 0.5), Point(r, 0.2, 0.5)
        ]
        marker_array.markers.append(diam)

        # 直径文字
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
        diam_text.text = "Diameter: %.1fm" % self.pit_diameter
        marker_array.markers.append(diam_text)

        return marker_array

    def generate_trajectory_point(self, t):
        """螺旋轨迹"""
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
        """发布TF"""
        # base_link → world
        transform = TransformStamped()
        transform.header.stamp = rospy.Time.now()
        transform.header.frame_id = "world"
        transform.child_frame_id = "base_link"
        transform.transform.translation.x = x
        transform.transform.translation.y = y
        transform.transform.translation.z = z
        angle = 0.5 * t
        q = tf.transformations.quaternion_from_euler(0, 0, angle + np.pi/2)
        transform.transform.rotation.x = q[0]
        transform.transform.rotation.y = q[1]
        transform.transform.rotation.z = q[2]
        transform.transform.rotation.w = q[3]
        self.tf_broadcaster.sendTransform(transform)

        # 传感器坐标系
        sensors = [
            ("lidar", 0, 0, 0.35, 0, 0, 0),
            ("camera", 0.3, 0, 0.25, 0, 0.26, 0),
            ("imu", 0, 0, 0.15, 0, 0, 0),
        ]
        for name, dx, dy, dz, roll, pitch, yaw in sensors:
            sensor_tf = TransformStamped()
            sensor_tf.header.stamp = rospy.Time.now()
            sensor_tf.header.frame_id = "base_link"
            sensor_tf.child_frame_id = name
            sensor_tf.transform.translation.x = dx
            sensor_tf.transform.translation.y = dy
            sensor_tf.transform.translation.z = dz
            q = tf.transformations.quaternion_from_euler(roll, pitch, yaw)
            sensor_tf.transform.rotation.x = q[0]
            sensor_tf.transform.rotation.y = q[1]
            sensor_tf.transform.rotation.z = q[2]
            sensor_tf.transform.rotation.w = q[3]
            self.tf_broadcaster.sendTransform(sensor_tf)

    def create_laser_features(self, x, y, z):
        """激光特征点云"""
        points = []
        colors = []

        # 边缘特征 (红色)
        for angle in np.linspace(0, 2*np.pi, 20):
            r = self.pit_diameter / 2
            px = r * np.cos(angle)
            py = r * np.sin(angle)
            pz = z + np.random.normal(0, 0.01)
            points.append([px, py, pz])
            colors.append([255, 0, 0])

        # 平面特征 (蓝色)
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
        """创建PointCloud2"""
        header = Header()
        header.frame_id = "world"
        header.stamp = rospy.Time.now()

        fields = [
            PointField('x', 0, PointField.FLOAT32, 1),
            PointField('y', 4, PointField.FLOAT32, 1),
            PointField('z', 8, PointField.FLOAT32, 1),
            PointField('rgb', 12, PointField.UINT32, 1),
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

    def run(self):
        """主循环"""
        rate = rospy.Rate(10)  # 10Hz

        # 首次发布静态数据
        rospy.sleep(0.5)
        self.pit_boundary_pub.publish(self.create_pit_boundary())
        rospy.sleep(0.1)
        self.support_piles_pub.publish(self.create_support_piles())
        rospy.sleep(0.1)
        self.surfel_map_pub.publish(self.create_surfel_map())
        rospy.sleep(0.1)
        self.measured_geometry_pub.publish(self.create_measured_geometry())
        rospy.loginfo("静态数据已发布")

        while not rospy.is_shutdown():
            t = (rospy.Time.now() - self.start_time).to_sec()

            # 生成轨迹点
            x, y, z = self.generate_trajectory_point(t)

            # 发布TF
            self.publish_tf(x, y, z, t)

            # 当前位姿
            pose = PoseStamped()
            pose.header.frame_id = "world"
            pose.header.stamp = rospy.Time.now()
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.position.z = z
            angle = 0.5 * t
            q = tf.transformations.quaternion_from_euler(0, 0, angle + np.pi/2)
            pose.pose.orientation.x = q[0]
            pose.pose.orientation.y = q[1]
            pose.pose.orientation.z = q[2]
            pose.pose.orientation.w = q[3]
            self.current_pose_pub.publish(pose)

            # 轨迹
            self.trajectory.header.stamp = rospy.Time.now()
            self.trajectory.poses.append(pose)
            if len(self.trajectory.poses) > 1000:
                self.trajectory.poses.pop(0)
            self.trajectory_pub.publish(self.trajectory)

            # 真值轨迹
            gt_pose = PoseStamped()
            gt_pose.header = pose.header
            gt_x, gt_y, gt_z = self.generate_trajectory_point(t)
            gt_pose.pose.position.x = gt_x
            gt_pose.pose.position.y = gt_y
            gt_pose.pose.position.z = gt_z
            gt_pose.pose.orientation = pose.pose.orientation
            self.ground_truth_path.header.stamp = rospy.Time.now()
            self.ground_truth_path.poses.append(gt_pose)
            if len(self.ground_truth_path.poses) > 1000:
                self.ground_truth_path.poses.pop(0)
            self.ground_truth_pub.publish(self.ground_truth_path)

            # 激光特征
            self.laser_features_pub.publish(self.create_laser_features(x, y, z))

            rate.sleep()

if __name__ == '__main__':
    try:
        node = DeepPitVisualizationNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
