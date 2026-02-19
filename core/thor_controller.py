import ai2thor.controller
from typing import List, Dict, Any, Optional
import time
import logging

class ThorController:
    """
    Bridge between PDDL action plans and AI2-THOR simulation.
    """
    def __init__(self, scene: str = "FloorPlan1"):
        self.scene = scene
        self.controller = ai2thor.controller.Controller(
            agentMode="default",
            visibilityDistance=2.0,
            scene=scene,
            gridSize=0.25,
            width=600,
            height=600
        )
        # Mock mapping for demo locations to THOR coordinates
        self.location_map = {
            "floor6_charging_dock": {"x": -1.25, "y": 0.95, "z": -1.5},
            "floor6_hallway": {"x": 0.0, "y": 0.95, "z": 0.0},
            "floor2_lab": {"x": 1.5, "y": 0.95, "z": 1.5},
            "workbench": {"x": 1.5, "y": 0.95, "z": 1.5}
        }
        logging.info(f"AI2-THOR Controller initialized on scene {scene}")

    def execute_plan(self, plan: List[str]):
        """
        Executes a sequence of PDDL actions in the simulator.
        """
        for i, action_str in enumerate(plan):
            logging.info(f"Step {i+1}: Executing {action_str}")
            # Clean up action string
            clean_action = action_str.lower().replace('(', '').replace(')', '').strip()
            parts = clean_action.split(' ')
            action_name = parts[0]
            args = parts[1:]
            
            if action_name == "move_to":
                # args: [robot, from, to]
                target_loc = args[-1]
                self.move_to_location(target_loc)
            elif action_name == "pick_up":
                # args: [robot, object, location]
                self.pick_up_object(args[1])
            elif action_name == "place":
                # args: [robot, object, location]
                self.put_object(args[1], args[2])
            
            # Save frame for documentation
            event = self.controller.last_event
            import PIL.Image
            img = PIL.Image.fromarray(event.frame)
            img.save(f"demo_step_{i+1}.png")
            
            time.sleep(1.0)

    def move_to_location(self, location_id: str):
        pos = self.location_map.get(location_id, {"x": 0, "y": 0, "z": 0})
        self.controller.step(
            action="Teleport",
            position=pos,
            rotation={"x": 0, "y": 0, "z": 0}
        )
        logging.info(f"Moved robot to {location_id} at {pos}")

    def pick_up_object(self, object_id: str):
        # In a real demo, we'd find an object ID. 
        # Here we mock successful pickup or interact with a nearby object.
        logging.info(f"Robot picking up {object_id}")
        self.controller.step(action="RotateRight") # Small visual action

    def put_object(self, object_id: str, receptacle_id: str):
        logging.info(f"Robot placing {object_id} on {receptacle_id}")
        self.controller.step(action="RotateLeft") # Small visual action

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("AI2-THOR Controller module ready.")
