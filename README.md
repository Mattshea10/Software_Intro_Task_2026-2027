# Space Concordia Robotics — Software Intro Task (2026–2027)

ROS 2 Jazzy package (`intro_rover_description`) for visualizing and controlling the Space Concordia rover in **RViz2** and **Gazebo Harmonic**.

---

## Quick Start

### 0. Install Dependencies (First-Time Setup on a New Machine)

Make sure ROS 2 Jazzy's Gazebo Harmonic packages and state publishers are installed:

```bash
sudo apt update
sudo apt install -y ros-jazzy-ros-gz ros-jazzy-joint-state-publisher ros-jazzy-robot-state-publisher ros-jazzy-rviz2
```

---

### 1. Build the Workspace

From the root of this repository:

```bash
# If moving between machines or rebuilding cleanly, remove old build artifacts first:
rm -rf build install log

# Source ROS 2 Jazzy and build
source /opt/ros/jazzy/setup.bash
colcon build --packages-select intro_rover_description
source install/setup.bash
```

---

### 2. Launch the Rover

Choose **one** of the following modes:

- **Option A — RViz Visualization:**
  ```bash
  source /opt/ros/jazzy/setup.bash
  source install/setup.bash
  ros2 launch intro_rover_description rover_launch.py
  ```

- **Option B — Gazebo Harmonic Simulation:**
  ```bash
  source /opt/ros/jazzy/setup.bash
  source install/setup.bash
  ros2 launch intro_rover_description gazebo_launch.py
  ```

> **WSL2 Note:** If RViz or Gazebo ever stays stuck in the Windows taskbar with `[WARN: No copy mode]`, run `wsl --shutdown` in Windows PowerShell and reopen your terminal to reset WSLg's shared memory display bridge.

---

### 3. Control the Rover

Open a **new terminal** in the workspace directory, source the workspace, and run either control node (both work with RViz and Gazebo):

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

- **Manual Joint Control (Interactive CLI):**
  ```bash
  ros2 run intro_rover_description joint_commands.py
  ```
- **Automated Rover Dance (Headbob):**
  ```bash
  ros2 run intro_rover_description headbob_dance.py
  ```

---

## Project Overview

| File | Description |
| :--- | :--- |
| [`CMakeLists.txt`](src/intro_rover_description/CMakeLists.txt) & [`package.xml`](src/intro_rover_description/package.xml) | Installs `urdf/`, `meshes/`, `launch/`, and Python control scripts; declares ROS 2 & Gazebo dependencies. |
| [`rover_launch.py`](src/intro_rover_description/launch/rover_launch.py) | Launches `robot_state_publisher`, `joint_state_publisher` (listening to `/joint_commands`), and `rviz2`. |
| [`gazebo_launch.py`](src/intro_rover_description/launch/gazebo_launch.py) | Launches Gazebo Harmonic (`empty.sdf`), spawns the rover, and bridges all 14 joint topics via `ros_gz_bridge`. |
| [`joint_commands.py`](src/intro_rover_description/joint_commands.py) | CLI node to move any of the 14 rover joints to a target angle (in radians) with automatic joint-limit clamping. |
| [`headbob_dance.py`](src/intro_rover_description/headbob_dance.py) | Timer node (~30 Hz) that drives `wrist_pitch` and `shoulder_yaw` in a continuous sinusoidal motion. |
| [`intro_rover_description.urdf`](src/intro_rover_description/urdf/intro_rover_description.urdf) | Rover URDF updated with optimized `.STL` visual meshes, primitive collision geometry, inertial tensors, and Gazebo PID joint position controllers. |
