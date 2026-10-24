#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class JointCommands(Node):
    def __init__(self):
        # Node names should not contain spaces
        super().__init__('joint_commands_node')
        self.publisher_ = self.create_publisher(JointState, '/joint_commands', 10)

    def command_loop(self):
        # This loop takes over the main thread to constantly ask for inputs
        while True:
            joint_name = input("Joint Name: ")
            
            # Catch errors if the user types a letter instead of a number
            try:
                angle = float(input('Angle (in radians): '))
            except ValueError:
                print("Please enter a valid numeric angle.")
                continue

            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = [joint_name]
            msg.position = [angle]

            self.publisher_.publish(msg)
            print(f"--> Published {angle} rad to {joint_name}\n")

def main(args=None):
    rclpy.init(args=args)
    node = JointCommands()
    
    try:
        # Run your custom loop instead of rclpy.spin()
        node.command_loop()
    except KeyboardInterrupt:
        # Allows you to exit cleanly using Ctrl+C
        pass
        
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()