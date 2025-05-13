import sys
import time
import numpy as np
from pathlib import Path
try:
    import sim
except:
    print('Error importing sim module. Make sure CoppeliaSim is installed correctly')
    sys.exit(1)

class RobotArmController:
    def __init__(self):
        self.client_id = None
        self.joint_handles = []
        self.target_handle = None
        self.connected = False
        
    def connect(self):
        """Connect to CoppeliaSim"""
        sim.simxFinish(-1)  # Close all opened connections
        self.client_id = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)
        
        if self.client_id != -1:
            print('Connected to CoppeliaSim remote API server')
            self.connected = True
            return True
        else:
            print('Failed to connect to CoppeliaSim remote API server')
            return False
            
    def initialize_handles(self):
        """Get handles for robot joints and target"""
        if not self.connected:
            print("Not connected to CoppeliaSim")
            return False
            
        try:
            # Get handles for the robot arm joints
            for i in range(1, 7):
                ret, handle = sim.simxGetObjectHandle(
                    self.client_id,
                    f'Joint{i}',
                    sim.simx_opmode_blocking
                )
                if ret != 0:
                    print(f"Error getting handle for Joint{i}")
                    return False
                self.joint_handles.append(handle)
                
            # Get handle for target object
            ret, self.target_handle = sim.simxGetObjectHandle(
                self.client_id,
                'Target',
                sim.simx_opmode_blocking
            )
            if ret != 0:
                print("Error getting handle for Target")
                return False
                
            return True
        except Exception as e:
            print(f"Error initializing handles: {str(e)}")
            return False
            
    def set_joint_angles(self, angles):
        """Set joint angles for the robot arm"""
        if not self.connected:
            return False
            
        try:
            for handle, angle in zip(self.joint_handles, angles):
                sim.simxSetJointTargetPosition(
                    self.client_id,
                    handle,
                    angle,
                    sim.simx_opmode_oneshot
                )
            return True
        except Exception as e:
            print(f"Error setting joint angles: {str(e)}")
            return False
            
    def get_joint_angles(self):
        """Get current joint angles"""
        if not self.connected:
            return None
            
        angles = []
        for handle in self.joint_handles:
            _, angle = sim.simxGetJointPosition(
                self.client_id,
                handle,
                sim.simx_opmode_blocking
            )
            angles.append(angle)
        return angles
            
    def move_to_pose(self, target_angles, speed=1.0):
        """Move the robot arm to a specific pose with controlled speed"""
        if not self.connected:
            return False
            
        current_angles = self.get_joint_angles()
        if not current_angles:
            return False
            
        # Interpolate between current and target angles
        steps = int(50 / speed)  # Adjust steps based on speed
        for i in range(steps):
            interpolated_angles = []
            for curr, target in zip(current_angles, target_angles):
                angle = curr + (target - curr) * (i / steps)
                interpolated_angles.append(angle)
                
            if not self.set_joint_angles(interpolated_angles):
                return False
                
            time.sleep(0.05 / speed)
        return True
        
    def move_to_target(self):
        """Move the end effector to the target position"""
        if not self.connected:
            return False
            
        try:
            # Get target position
            ret, target_pos = sim.simxGetObjectPosition(
                self.client_id,
                self.target_handle,
                -1,  # Relative to world frame
                sim.simx_opmode_blocking
            )
            if ret != 0:
                print("Error getting target position")
                return False
                
            # Get target orientation
            ret, target_ori = sim.simxGetObjectOrientation(
                self.client_id,
                self.target_handle,
                -1,  # Relative to world frame
                sim.simx_opmode_blocking
            )
            if ret != 0:
                print("Error getting target orientation")
                return False
                
            # The actual IK calculation would be done in CoppeliaSim
            # Here we just signal the Lua script to perform IK
            return True
        except Exception as e:
            print(f"Error moving to target: {str(e)}")
            return False

def main():
    # Initialize controller
    controller = RobotArmController()
    
    # Connect to CoppeliaSim
    if not controller.connect():
        sys.exit(1)
        
    # Initialize robot handles
    if not controller.initialize_handles():
        sim.simxFinish(controller.client_id)
        sys.exit(1)
    
    print("\nRobot Arm Control Menu:")
    print("1. Execute predefined movement sequence")
    print("2. Move to specific joint angles")
    print("3. Move to target position")
    print("4. Get current joint angles")
    print("5. Test")
    print("6. Exit")
    
    try:
        while True:
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == '1':
                # Predefined movement sequence
                poses = [
                    [0, np.pi/4, 0, -np.pi/4, 0, 0],  # Home position
                    [np.pi/2, np.pi/3, -np.pi/6, -np.pi/3, np.pi/4, 0],  # Extended position
                    [-np.pi/2, np.pi/6, np.pi/4, -np.pi/2, -np.pi/4, np.pi/6],  # Alternative position
                ]
                
                for pose in poses:
                    if not controller.move_to_pose(pose):
                        print("Failed to execute movement sequence")
                        break
                    time.sleep(1)
                    
            elif choice == '2':
                # Move to specific joint angles
                try:
                    angles = [float(x) for x in input("Enter 6 joint angles in radians (space-separated): ").split()]
                    if len(angles) != 6:
                        print("Please enter exactly 6 angles")
                        continue
                    controller.move_to_pose(angles)
                except ValueError:
                    print("Invalid input. Please enter valid numbers.")
                    
            elif choice == '3':
                # Move to target position
                controller.move_to_target()
                
            elif choice == '4':
                # Get current joint angles
                angles = controller.get_joint_angles()
                if angles:
                    print("Current joint angles (radians):", angles)
                    
            elif choice == '5':
                print("Exiting...")
                break
                
            else:
                print("Invalid choice. Please enter a number between 1 and 5.")
                
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    finally:
        sim.simxFinish(controller.client_id)
        
if __name__ == '__main__':
    main() 