from setuptools import setup

package_name = 'deep_pit_inspection'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/deep_pit.launch.py']),
        ('share/' + package_name + '/rviz', ['rviz/deep_pit_config.rviz']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Maintainer',
    maintainer_email='maintainer@example.com',
    description='Deep Pit Inspection Robot System for ROS2',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'deep_pit_visualization = deep_pit_inspection.visualization_node:main',
        ],
    },
)
