#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64


class HeadbobDance(Node):
    def __init__(self):
        super().__init__('headbob_dance')
        # Publishers for Gazebo Harmonic (std_msgs/msg/Float64 per joint topic)
        self.wrist_pitch_pub = self.create_publisher(Float64, '/wrist_pitch', 10)
        self.shoulder_yaw_pub = self.create_publisher(Float64, '/shoulder_yaw', 10)

        # Publisher for RViz joint_state_publisher source_list (sensor_msgs/msg/JointState)
        self.joint_state_pub = self.create_publisher(JointState, '/joint_commands', 10)

        timer_period = 0.033  # ~30 Hz
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.counter = 0.0

    def timer_callback(self):
        self.counter += 0.05

        wrist_angle = math.sin(self.counter)
        shoulder_angle = 0.5 * math.sin(self.counter * 0.5)

        # Publish Float64 commands for Gazebo Harmonic
        wrist_msg = Float64()
        wrist_msg.data = wrist_angle
        self.wrist_pitch_pub.publish(wrist_msg)

        shoulder_msg = Float64()
        shoulder_msg.data = shoulder_angle
        self.shoulder_yaw_pub.publish(shoulder_msg)

        # Publish JointState command for RViz
        js_msg = JointState()
        js_msg.header.stamp = self.get_clock().now().to_msg()
        js_msg.name = ['wrist_pitch', 'shoulder_yaw']
        js_msg.position = [wrist_angle, shoulder_angle]
        self.joint_state_pub.publish(js_msg)


def main(args=None):
    rclpy.init(args=args)
    node = HeadbobDance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

    main()