from setuptools import setup
import os
from glob import glob

package_name = 'deep_pit_simulation'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # URDF 文件
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.xacro')),
        # World 文件
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        # Launch 文件
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # RViz 配置
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        # Config 文件
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Maintainer',
    maintainer_email='maintainer@example.com',
    description='Deep Pit Inspection Robot Simulation with ROS2 and Gazebo',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simulation = deep_pit_simulation.simulation_node:main',
            'gt_recorder = deep_pit_simulation.gt_recorder:main',
            'trajectory_publisher = deep_pit_simulation.trajectory_publisher:main',
        ],
    },
)
