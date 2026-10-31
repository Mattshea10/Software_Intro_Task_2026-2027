#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64

# Joint limits in radians (None = continuous joint)
JOINT_LIMITS = {
    'shoulder_yaw': None,
    'shoulder_pitch': (-1.57, 1.57),
    'elbow_pitch': (-1.57, 1.57),
    'elbow_roll': None,
    'wrist_pitch': (-1.57, 1.57),
    'wrist_roll': None,
    'fr_swerve_yaw': (-1.57, 1.57),
    'fr_wheel': None,
    'br_swerve_yaw': (-1.57, 1.57),
    'br_wheel': None,
    'fl_swerve_yaw': (-1.57, 1.57),
    'fl_wheel': None,
    'bl_swerve_yaw': (-1.57, 1.57),
    'bl_wheel': None,
}


class JointCommands(Node):
    """Interactive CLI node for sending target joint angles (in radians) to RViz and Gazebo."""

    def __init__(self):
        super().__init__('joint_commands_node')
        # Publishers for Gazebo Harmonic (std_msgs/msg/Float64 per joint topic)
        self.gz_publishers_ = {
            joint: self.create_publisher(Float64, f'/{joint}', 10)
            for joint in JOINT_LIMITS
        }
        # Publisher for RViz joint_state_publisher source_list (sensor_msgs/msg/JointState)
        self.rviz_publisher_ = self.create_publisher(JointState, '/joint_commands', 10)

    def command_loop(self):
        """Continuously prompt the user for a joint name and target radian angle."""
        print(f"Available joints:\n  {', '.join(JOINT_LIMITS.keys())}\n")
        while rclpy.ok():
            # Read and normalize joint name input
            joint_name = input("Joint Name: ").strip().lstrip('/')
            if joint_name not in self.gz_publishers_:
                print(f"Unknown joint '{joint_name}'. Valid joints: {', '.join(JOINT_LIMITS.keys())}\n")
                continue

            # Prompt for target angle and validate numeric input
            limits = JOINT_LIMITS[joint_name]
            limit_str = f" [{limits[0]} to {limits[1]} rad]" if limits else " [continuous, in radians]"
            try:
                angle = float(input(f"Angle{limit_str}: "))
            except ValueError:
                print("Please enter a valid numeric angle.\n")
                continue

            # Clamp revolute joints to their physical URDF limits if exceeded
            if limits is not None and (angle < limits[0] or angle > limits[1]):
                clamped = max(limits[0], min(limits[1], angle))
                print(f"Warning: {angle} rad exceeds limits {limits} for '{joint_name}'. Clamping to {clamped} rad.")
                angle = clamped

            # Publish Float64 for Gazebo Harmonic
            gz_msg = Float64()
            gz_msg.data = angle
            self.gz_publishers_[joint_name].publish(gz_msg)

            # Publish JointState for RViz
            rviz_msg = JointState()
            rviz_msg.header.stamp = self.get_clock().now().to_msg()
            rviz_msg.name = [joint_name]
            rviz_msg.position = [angle]
            self.rviz_publisher_.publish(rviz_msg)

            print(f"--> Published {angle} rad to /{joint_name} (Gazebo) and /joint_commands (RViz)\n")


def main(args=None):
    rclpy.init(args=args)
    node = JointCommands()

    try:
        node.command_loop()
    except (KeyboardInterrupt, EOFError):
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
