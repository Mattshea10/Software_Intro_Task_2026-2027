# Space Concordia Robotics — Software Introduction Task (2026–2027)

This repository contains the completed ROS 2 Jazzy workspace and `intro_rover_description` package for the Space Concordia Robotics Division Software Intro Task, including RViz visualization, interactive and automated joint control nodes, and full physics simulation in **Gazebo Harmonic**.

---

## Summary of Development & Solutions by Step

### 1. Creating a Local Repository
- Forked the upstream `Software_Intro_Task_2026-2027` repository to a personal GitHub account and cloned it locally into a ROS 2 Jazzy workspace.

### 2. Fixing the `intro_rover_description` ROS 2 Package
- **Original Issue:** The starter package only had a skeleton [CMakeLists.txt](src/intro_rover_description/CMakeLists.txt) and [package.xml](src/intro_rover_description/package.xml) that did not install the `urdf/`, `meshes/`, or `launch/` directories, nor declare runtime dependencies. Consequently, ROS 2 could not locate the URDF or `.STL` meshes.
- **Solution:**
  - Updated [CMakeLists.txt](src/intro_rover_description/CMakeLists.txt) with `install(DIRECTORY urdf launch meshes DESTINATION share/${PROJECT_NAME})` and `install(PROGRAMS headbob_dance.py joint_commands.py DESTINATION lib/${PROJECT_NAME})`.
  - Updated [package.xml](src/intro_rover_description/package.xml) with `<exec_depend>` tags for `rclpy`, `std_msgs`, `sensor_msgs`, `robot_state_publisher`, `joint_state_publisher`, `rviz2`, `ros_gz_sim`, and `ros_gz_bridge`.

### 3. Visualizing the Robot in RViz
- Created [rover_launch.py](src/intro_rover_description/launch/rover_launch.py) to launch:
  1. `robot_state_publisher` loaded with `urdf/intro_rover_description.urdf`.
  2. `joint_state_publisher` configured with `source_list: ['/joint_commands']` so external nodes can command individual joints without overwriting the rest of the robot's joint states.
  3. `rviz2` to visualize the rover's TF tree and 3D `.STL` meshes.

### 4. Creating a ROS 2 Infrastructure to Control the Rover
- **4.1 Manual Joint Control ([joint_commands.py](src/intro_rover_description/joint_commands.py)):**
  - Interactive CLI node (`joint_commands_node`) that lists all 14 joints (`shoulder_yaw`, `shoulder_pitch`, `elbow_pitch`, `elbow_roll`, `wrist_pitch`, `wrist_roll`, and the 4 swerve yaw / 4 wheel joints), prompts for a joint name and target angle in radians, validates/clamps revolute joints to their `[-1.57, 1.57]` rad limits, and publishes both `sensor_msgs/msg/JointState` (to `/joint_commands` for RViz) and `std_msgs/msg/Float64` (to `/<joint_name>` for Gazebo Harmonic).
- **4.2 Automated Rover Dance ([headbob_dance.py](src/intro_rover_description/headbob_dance.py)):**
  - Timer-driven node (`headbob_dance`) running at ~30 Hz that computes smooth sinusoidal trajectories (`math.sin`) for `wrist_pitch` and `shoulder_yaw`, publishing simultaneously to `/joint_commands` (RViz) and `/wrist_pitch` & `/shoulder_yaw` (Gazebo Harmonic).

### 5. Simulating the Robot in Gazebo Harmonic
- **Mesh Optimization (89% Triangle Reduction):**
  - The original SolidWorks-exported `.STL` files totaled **30 MB (623,120 triangles)** (`base_link.STL` alone had 154,772 triangles). Using quadric mesh decimation (`vtkQuadricDecimation` with volume and feature-edge preservation), the 15 `.STL` meshes in `meshes/` were reduced from **623,120 triangles to 68,565 triangles (~3.3 MB total)** while keeping visual geometry crisp.
- **Physics & URDF Enhancements ([intro_rover_description.urdf](src/intro_rover_description/urdf/intro_rover_description.urdf)):**
  - Replaced high-polygon `.STL` `<collision>` meshes with lightweight, non-overlapping primitive shapes (`<box>` for chassis/arm/swerve links and `<cylinder>` for the 4 wheels) and clean diagonal `<inertial>` tensors so Gazebo's DART physics engine runs smoothly without trimesh self-collision crashes.
  - Added `<gazebo>` `gz-sim-joint-position-controller-system` (`gz::sim::systems::JointPositionController`) plugins for all 14 joints with tuned PID gains and `<cmd_min>`/`<cmd_max>` torque clamping.
- **Gazebo Launch & Topic Bridging ([gazebo_launch.py](src/intro_rover_description/launch/gazebo_launch.py)):**
  - Resolves `package://intro_rover_description` mesh URIs to `file://` paths and configures `GZ_SIM_RESOURCE_PATH`.
  - Launches Gazebo Harmonic (`empty.sdf`) via `ros_gz_sim`, spawns the rover above the ground plane (`z = 0.5`), and bridges all 14 `/<joint_name>` topics between `std_msgs/msg/Float64` and `gz.msgs.Double` via `ros_gz_bridge`.

---

## How to Build and Run

### Build the Workspace
```bash
cd /home/Software_Intro_Task_2026-2027
colcon build --packages-select intro_rover_description
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

### Option A: Visualize in RViz (Step 3 & 4)
```bash
ros2 launch intro_rover_description rover_launch.py
```

### Option B: Simulate in Gazebo Harmonic (Step 5)
```bash
ros2 launch intro_rover_description gazebo_launch.py
```

### Run Control Nodes (Works with Both RViz and Gazebo)
In a separate terminal (after sourcing `install/setup.bash`):
- **Manual CLI Joint Control:**
  ```bash
  ros2 run intro_rover_description joint_commands.py
  ```
- **Automated Headbob Dance:**
  ```bash
  ros2 run intro_rover_description headbob_dance.py
  ```

### 4. Creating a ROS 2 Infrastructure to Control the Rover
- **4.1 Manual Joint Control ([joint_commands.py](src/intro_rover_description/joint_commands.py)):**
  - Interactive CLI node (`joint_commands_node`) that lists all 14 joints (`shoulder_yaw`, `shoulder_pitch`, `elbow_pitch`, `elbow_roll`, `wrist_pitch`, `wrist_roll`, and the 4 swerve yaw / 4 wheel joints), prompts for a joint name and target angle in radians, validates/clamps revolute joints to their `[-1.57, 1.57]` rad limits, and publishes both `sensor_msgs/msg/JointState` (to `/joint_commands` for RViz) and `std_msgs/msg/Float64` (to `/<joint_name>` for Gazebo Harmonic).
- **4.2 Automated Rover Dance ([headbob_dance.py](src/intro_rover_description/headbob_dance.py)):**
  - Timer-driven node (`headbob_dance`) running at ~30 Hz that computes smooth sinusoidal trajectories (`math.sin`) for `wrist_pitch` and `shoulder_yaw`, publishing simultaneously to `/joint_commands` (RViz) and `/wrist_pitch` & `/shoulder_yaw` (Gazebo Harmonic).

### 5. Simulating the Robot in Gazebo Harmonic
- **Mesh Optimization (89% Triangle Reduction):**
  - The original SolidWorks-exported `.STL` files totaled **30 MB (623,120 triangles)** (`base_link.STL` alone had 154,772 triangles). Using quadric mesh decimation (`vtkQuadricDecimation` with volume and feature-edge preservation), the 15 `.STL` meshes in `meshes/` were reduced from **623,120 triangles to 68,565 triangles (~3.3 MB total)** while keeping visual geometry crisp.
- **Physics & URDF Enhancements ([intro_rover_description.urdf](src/intro_rover_description/urdf/intro_rover_description.urdf)):**
  - Replaced high-polygon `.STL` `<collision>` meshes with lightweight, non-overlapping primitive shapes (`<box>` for chassis/arm/swerve links and `<cylinder>` for the 4 wheels) and clean diagonal `<inertial>` tensors so Gazebo's DART physics engine runs smoothly without trimesh self-collision crashes.
  - Added `<gazebo>` `gz-sim-joint-position-controller-system` (`gz::sim::systems::JointPositionController`) plugins for all 14 joints with tuned PID gains and `<cmd_min>`/`<cmd_max>` torque clamping.
- **Gazebo Launch & Topic Bridging ([gazebo_launch.py](src/intro_rover_description/launch/gazebo_launch.py)):**
  - Resolves `package://intro_rover_description` mesh URIs to `file://` paths and configures `GZ_SIM_RESOURCE_PATH`.
  - Launches Gazebo Harmonic (`empty.sdf`) via `ros_gz_sim`, spawns the rover above the ground plane (`z = 0.5`), and bridges all 14 `/<joint_name>` topics between `std_msgs/msg/Float64` and `gz.msgs.Double` via `ros_gz_bridge`.

---

## How to Build and Run

### Build the Workspace
```bash
cd /home/Software_Intro_Task_2026-2027
colcon build --packages-select intro_rover_description
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

### Option A: Visualize in RViz (Step 3 & 4)
```bash
ros2 launch intro_rover_description rover_launch.py
```

### Option B: Simulate in Gazebo Harmonic (Step 5)
```bash
ros2 launch intro_rover_description gazebo_launch.py
```

### Run Control Nodes (Works with Both RViz and Gazebo)
In a separate terminal (after sourcing `install/setup.bash`):
- **Manual CLI Joint Control:**
  ```bash
  ros2 run intro_rover_description joint_commands.py
  ```
- **Automated Headbob Dance:**
  ```bash
  ros2 run intro_rover_description headbob_dance.py
  ```

