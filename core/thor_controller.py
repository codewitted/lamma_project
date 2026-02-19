import ai2thor.controller
from typing import List, Dict, Any, Optional
import time
import logging

class ThorController:
    """
    Enhanced bridge between PDDL action plans and AI2-THOR simulation.
    Supports multi-agent coordination, continuous movement, and third-party cameras.
    """
    def __init__(self, scene: str = "FloorPlan1", num_agents: int = 1):
        self.scene = scene
        self.num_agents = num_agents
        self.controller = ai2thor.controller.Controller(
            agentMode="default",
            visibilityDistance=2.0,
            scene=scene,
            gridSize=0.25,
            width=800, # Increased for better visuals
            height=600,
            agentCount=num_agents
        )
        
        # Add a Third-Party Camera for a global overview (Kitchen/Lab friendly)
        self.controller.step(
            action="AddThirdPartyCamera",
            position={"x": -1.5, "y": 2.5, "z": 0.0},
            rotation={"x": 30, "y": 90, "z": 0}
        )
        
        # Mapping robot IDs to agent indices
        self.robot_to_agent = {}
        
        # Enhanced mapping for demo locations to THOR coordinates (Kitchen/Lab)
        self.location_map = {
            "floor6_charging_dock": {"x": -1.25, "y": 0.9, "z": -1.5},
            "floor6_hallway": {"x": 0.0, "y": 0.9, "z": 0.0},
            "floor2_lab": {"x": 1.5, "y": 0.9, "z": 1.5},
            "workbench": {"x": 0.5, "y": 0.9, "z": 1.0},
            "floor2_lab_workbench": {"x": 0.5, "y": 0.9, "z": 1.0},
            "sink": {"x": -0.5, "y": 0.9, "z": 1.2}
        }
        logging.info(f"AI2-THOR Controller initialized with {num_agents} agents on {scene}")

    def execute_plan(self, plan: List[str], wait_at_end: bool = True):
        """
        Executes a sequence of PDDL actions in the simulator.
        """
        # Assign robots to agents
        robot_names = set()
        for action_str in plan:
            clean_action = action_str.lower().replace('(', '').replace(')', '').strip()
            if not clean_action: continue
            parts = clean_action.split(' ')
            if len(parts) > 1:
                robot_names.add(parts[1])
        
        sorted_robots = sorted(list(robot_names))
        for i, robot in enumerate(sorted_robots):
            if i < self.num_agents:
                self.robot_to_agent[robot] = i
                # Initial positioning with offset to avoid overlap
                offset_pos = {
                    "x": -1.5 + (i * 0.5), 
                    "y": 0.9, 
                    "z": -1.5
                }
                self.controller.step(
                    action="Teleport", 
                    agentId=i, 
                    position=offset_pos,
                    rotation={"x": 0, "y": i * 90, "z": 0}
                )

        for i, action_str in enumerate(plan):
            logging.info(f"Step {i+1}: Executing {action_str}")
            clean_action = action_str.lower().replace('(', '').replace(')', '').strip()
            if not clean_action: continue
            parts = clean_action.split(' ')
            if len(parts) < 2: continue
            action_name = parts[0]
            robot_id = parts[1]
            args = parts[2:]
            
            agent_id = self.robot_to_agent.get(robot_id, 0)
            
            if action_name == "move_to":
                target_loc = args[-1] if args else "floor6_hallway"
                self.move_to_location(robot_id, target_loc)
            elif action_name == "pick_up":
                obj = args[0] if args else "item"
                self.pick_up_object(robot_id, obj)
            elif action_name in ["place", "drop"]:
                obj = args[0] if args else "item"
                loc = args[1] if len(args) > 1 else "here"
                self.put_object(robot_id, obj, loc)
            
            # Save frames for documentation
            event = self.controller.last_event
            import PIL.Image
            
            # Agent View
            if len(event.events) > agent_id:
                img_agent = PIL.Image.fromarray(event.events[agent_id].frame)
                img_agent.save(f"demo_step_{i+1}_agent_{agent_id}.png")
                
                # Third-Party Overview
                if len(event.events[agent_id].third_party_camera_frames) > 0:
                    img_ov = PIL.Image.fromarray(event.events[agent_id].third_party_camera_frames[0])
                    img_ov.save(f"demo_step_{i+1}_overview.png")
            
            time.sleep(0.5)
            
        if wait_at_end:
            print("\n🏁 Action Sequence Complete.")
            print("📸 Check the project root for demo_step_* images.")
            input("Press Enter to close the AI2-THOR simulator window...")

    def move_to_location(self, robot_id: str, location_id: str, teleport: bool = False):
        agent_id = self.robot_to_agent.get(robot_id, 0)
        target_pos = self.location_map.get(location_id, {"x": 0, "y": 0.95, "z": 0})
        
        if teleport:
            self.controller.step(
                action="Teleport",
                agentId=agent_id,
                position=target_pos,
                rotation={"x": 0.0, "y": 0.0, "z": 0.0}
            )
        else:
            # Simple "smooth" movement: 5 steps of interpolation for visual continuity
            # Use metadata to get position
            current_event = self.controller.last_event.events[agent_id]
            current_pos = current_event.metadata['agent']['position']
            
            for i in range(1, 6):
                step_pos = {
                    "x": current_pos["x"] + (target_pos["x"] - current_pos["x"]) * (i / 5.0),
                    "y": target_pos["y"],
                    "z": current_pos["z"] + (target_pos["z"] - current_pos["z"]) * (i / 5.0)
                }
                self.controller.step(
                    action="Teleport",
                    agentId=agent_id,
                    position=step_pos
                )
                time.sleep(0.05)

        logging.info(f"Robot {robot_id} (Agent {agent_id}) moved to {location_id}")

    def pick_up_object(self, robot_id: str, object_id: str):
        agent_id = self.robot_to_agent.get(robot_id, 0)
        logging.info(f"Robot {robot_id} picking up {object_id}")
        for _ in range(3):
            self.controller.step(action="RotateRight", agentId=agent_id, degrees=30)
            time.sleep(0.1)

    def put_object(self, robot_id: str, object_id: str, receptacle_id: str):
        agent_id = self.robot_to_agent.get(robot_id, 0)
        logging.info(f"Robot {robot_id} placing {object_id} on {receptacle_id}")
        for _ in range(3):
            self.controller.step(action="RotateLeft", agentId=agent_id, degrees=30)
            time.sleep(0.1)

    def cinematic_pan(self, output_name: str = "room_overview_360.mp4"):
        print(f"🎥 Starting 360° Cinematic Pan of {self.scene}")
        frames = []
        import PIL.Image
        import numpy as np
        
        # Rotate camera 360 degrees
        for angle in range(0, 361, 5):
            self.controller.step(
                action="UpdateThirdPartyCamera",
                thirdPartyCameraId=0,
                rotation={"x": 30, "y": angle, "z": 0}
            )
            event = self.controller.last_event
            # Capture overview frame
            img_ov = PIL.Image.fromarray(event.events[0].third_party_camera_frames[0])
            frames.append(np.array(img_ov))
            time.sleep(0.05)
            
        print(f"🎬 Compiling {len(frames)} frames into video...")
        try:
            import cv2
            height, width, layers = frames[0].shape
            video = cv2.VideoWriter(output_name, cv2.VideoWriter_fourcc(*'mp4v'), 20, (width, height))
            for frame in frames:
                video.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            video.release()
            print(f"✅ Video saved: {output_name}. You can open this with VLC!")
        except ImportError:
            # Fallback to saving as a sequence if cv2 is missing
            print("⚠️ OpenCV not found. Saving as image sequence instead.")
            for i, frame in enumerate(frames):
                PIL.Image.fromarray(frame).save(f"pan_frame_{i:03d}.png")
        except Exception as e:
            print(f"❌ Video compilation failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("AI2-THOR Controller module ready.")
