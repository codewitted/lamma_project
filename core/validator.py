from typing import List, Dict, Any, Optional
import re

class PlanValidator:
    """
    Validates the logical consistency of the generated robotics task list.
    Checks for common sense constraints in pick-and-place and navigation.
    """

    @staticmethod
    def validate_task_sequence(tasks: List[str], initial_predicates: Optional[List[str]] = None) -> bool:
        """
        Validates if the sequence of tasks is logically sound.
        Returns True if valid, False otherwise.
        """
        if not tasks:
            return True

        # Track state
        holding = None
        current_location = None
        # obj -> state (e.g., 'fridge' -> 'closed', 'stove' -> 'off')
        states = {}
        # obj -> contents (list of objects inside)
        containers = {}

        # Initialize from predicates if provided
        if initial_predicates:
            for p in initial_predicates:
                p = p.lower().strip()
                match = re.search(r"(\w+)\((.*)\)", p)
                if not match: continue
                pred, args = match.group(1), [a.strip() for a in match.group(2).split(",")]
                
                if pred == "closed": states[args[0]] = "closed"
                elif pred == "opened": states[args[0]] = "opened"
                elif pred == "switchedon": states[args[0]] = "on"
                elif pred == "switchedoff": states[args[0]] = "off"
                elif pred == "inside":
                    obj, container = args[0], args[1]
                    if container not in containers: containers[container] = []
                    containers[container].append(obj)

        for task in tasks:
            task = task.lower().strip()
            match = re.search(r"(\w+)\((.*)\)", task)
            if not match: continue
            action, args = match.group(1), [a.strip() for a in match.group(2).split(",")]

            if action == "pick_up":
                obj = args[0]
                if holding: return False # Already holding something
                
                # AI2-THOR check: is it inside a closed container?
                for container, contents in containers.items():
                    if obj in contents:
                        if states.get(container) == "closed":
                            return False # Cannot pick up from closed container
                
                holding = obj
            
            elif action == "place" or action == "drop":
                if not holding: return False
                if len(args) > 0 and args[0] != holding: return False
                
                # If placing inside a container, check if it's open
                if len(args) > 1:
                    container = args[1]
                    if states.get(container) == "closed":
                        return False # Cannot place in closed container
                
                holding = None
            
            elif action == "open":
                obj = args[0]
                states[obj] = "opened"
            
            elif action == "close":
                obj = args[0]
                states[obj] = "closed"
            
            elif action == "switch_on":
                obj = args[0]
                states[obj] = "on"
            
            elif action == "switch_off":
                obj = args[0]
                states[obj] = "off"

            elif action == "move_to" or action == "navigate":
                current_location = args[0]

        return True

    @staticmethod
    def calculate_logical_score(tasks: List[str], initial_predicates: Optional[List[str]] = None) -> float:
        """
        Returns a score between 0 and 1 based on task consistency.
        """
        if not tasks:
            return 1.0
        
        return 1.0 if PlanValidator.validate_task_sequence(tasks, initial_predicates) else 0.0

if __name__ == "__main__":
    # Test cases
    valid_plan = ["move_to(table1)", "pick_up(box)", "move_to(shelf)", "place(box)"]
    invalid_plan = ["pick_up(box1)", "pick_up(box2)"]  # Double pick
    invalid_plan2 = ["place(box)"]  # Place without pick
    
    print(f"Valid plan: {PlanValidator.validate_task_sequence(valid_plan)}")
    print(f"Invalid plan (double pick): {PlanValidator.validate_task_sequence(invalid_plan)}")
    print(f"Invalid plan (orphan place): {PlanValidator.validate_task_sequence(invalid_plan2)}")
