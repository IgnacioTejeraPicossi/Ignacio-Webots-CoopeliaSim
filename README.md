# Robot Arm Simulation with CoppeliaSim

This project demonstrates a robotic arm simulation using CoppeliaSim (formerly V-REP) with Python and Lua integration. The simulation includes potential VR visualization capabilities.

## Prerequisites

- CoppeliaSim EDU/PRO (Download from Coppelia Robotics website)
- Python 3.7 or higher
- Required Python packages (install via requirements.txt)

## Setup Instructions

1. Install CoppeliaSim on your system
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add CoppeliaSim to your system PATH
4. Place the scene file (.ttt) in your CoppeliaSim scenes folder

## Project Structure

- `robot_arm.ttt` - CoppeliaSim scene file containing the robot arm model
- `scripts/` - Contains Python and Lua scripts
  - `main.py` - Main Python script for controlling the simulation
  - `arm_control.lua` - Lua script for robot arm control logic
- `requirements.txt` - Python dependencies

## Usage

1. Open CoppeliaSim and load the robot_arm.ttt scene
2. Run the Python script:
   ```bash
   python scripts/main.py
   ```

## VR Integration

The project is structured to allow future VR integration using OpenVR or similar frameworks. 