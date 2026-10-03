#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math


class HeadbobDance(Node):
    def __init__(self):
        super().__init__('headbob_dance')
        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)

        timer_period = 0.033
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.counter = 0.0

    def timer_callback(self):
        self.counter += 0.05

        angle = math.sin(self.counter)

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['wrist_pitch']
        msg.position = [angle]

        # 4. Publish message
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = HeadbobDance()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()