import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_intro_rover = get_package_share_directory('intro_rover_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    urdf_path = os.path.join(pkg_intro_rover, 'urdf', 'intro_rover_description.urdf')

    with open(urdf_path, 'r') as infp:
        # Resolve package:// URIs to absolute file:// paths so Gazebo Harmonic
        # always loads the visual STL meshes reliably.
        robot_desc = infp.read().replace(
            'package://intro_rover_description',
            f'file://{pkg_intro_rover}'
        )

    # On WSL2, use X11 (xcb) backend for reliable Gazebo GUI window management
    wsl_env_actions = []
    if 'WSL_DISTRO_NAME' in os.environ:
        wsl_env_actions = [
            SetEnvironmentVariable(name='QT_QPA_PLATFORM', value='xcb'),
        ]

    # Add the workspace share directory to Gazebo's resource path for mesh resolution
    set_gz_resource_path = AppendEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.path.dirname(pkg_intro_rover)
    )

    # Publish the URDF to /robot_description using simulation clock
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True,
        }],
    )

    # Launch Gazebo Harmonic with an empty world (-r starts simulation running immediately)
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # Spawn the rover entity in Gazebo from the /robot_description topic
    spawn_rover = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'intro_rover_description',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5',
        ],
        output='screen',
    )

    # Bridge ROS 2 Float64 joint command topics to Gazebo Double messages
    # for all 14 joints controlled by JointPositionController plugins
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/shoulder_yaw@std_msgs/msg/Float64@gz.msgs.Double',
            '/shoulder_pitch@std_msgs/msg/Float64@gz.msgs.Double',
            '/elbow_pitch@std_msgs/msg/Float64@gz.msgs.Double',
            '/elbow_roll@std_msgs/msg/Float64@gz.msgs.Double',
            '/wrist_pitch@std_msgs/msg/Float64@gz.msgs.Double',
            '/wrist_roll@std_msgs/msg/Float64@gz.msgs.Double',
            '/fr_swerve_yaw@std_msgs/msg/Float64@gz.msgs.Double',
            '/fr_wheel@std_msgs/msg/Float64@gz.msgs.Double',
            '/br_swerve_yaw@std_msgs/msg/Float64@gz.msgs.Double',
            '/br_wheel@std_msgs/msg/Float64@gz.msgs.Double',
            '/fl_swerve_yaw@std_msgs/msg/Float64@gz.msgs.Double',
            '/fl_wheel@std_msgs/msg/Float64@gz.msgs.Double',
            '/bl_swerve_yaw@std_msgs/msg/Float64@gz.msgs.Double',
            '/bl_wheel@std_msgs/msg/Float64@gz.msgs.Double',
        ],
        output='screen',
    )

    return LaunchDescription(wsl_env_actions + [
        set_gz_resource_path,
        robot_state_publisher,
        gz_sim,
        spawn_rover,
        ros_gz_bridge,
    ])
