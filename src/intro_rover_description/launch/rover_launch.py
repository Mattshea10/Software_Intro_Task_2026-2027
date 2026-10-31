from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Locate the installed package share directory and URDF file path
    share = get_package_share_directory('intro_rover_description')
    urdf_path = os.path.join(share, 'urdf', 'intro_rover_description.urdf')

    # On WSL2, use X11 (xcb) backend for reliable window management
    wsl_env_actions = []
    if 'WSL_DISTRO_NAME' in os.environ:
        wsl_env_actions = [
            SetEnvironmentVariable(name='QT_QPA_PLATFORM', value='xcb'),
        ]

    return LaunchDescription(wsl_env_actions + [
        # Publish the rover's TF tree and robot_description from the URDF
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_path).read()}]
        ),
        # Maintain joint states and subscribe to /joint_commands so external
        # control nodes can update individual joints without resetting others
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            parameters=[{'source_list': ['/joint_commands']}]
        ),
        # Launch RViz2 for 3D visualization
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2'
        )
    ])