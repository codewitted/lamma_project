from typing import List, Dict, Any
import re

class PlanValidator:
    """
    Validates the logical consistency of the generated robotics task list.
    Checks for common sense constraints in pick-and-place and navigation.
    """

    @staticmethod
    def validate_task_sequence(tasks: List[str]) -> bool:
        """
        Validates if the sequence of tasks is logically sound.
        Returns True if valid, False otherwise.
        """
        if not tasks:
            return True

        # Track robot state
        holding = None
        current_location = None

        for task in tasks:
            task = task.lower().strip()
            
            # Extract action and arguments
            match = re.search(r"(\w+)\((.*)\)", task)
            if not match:
                continue
                
            action = match.group(1)
            args = [a.strip() for a in match.group(2).split(",")]

            if action == "pick_up":
                # Can't pick up if already holding something
                if holding:
                    return False
                holding = args[0]
            
            elif action == "place" or action == "drop":
                # Can't place if not holding anything
                if not holding:
                    return False
                # If placing a specific object, must be holding it
                if len(args) > 0 and args[0] != holding:
                    return False
                holding = None
            
            elif action == "move_to" or action == "navigate":
                target = args[0]
                # If we were already at a location, moving to the same location is redundant but not necessarily invalid
                # However, moving while holding something is fine
                current_location = target

        return True

    @staticmethod
    def calculate_logical_score(tasks: List[str]) -> float:
        """
        Returns a score between 0 and 1 based on task consistency.
        """
        if not tasks:
            return 1.0
        
        return 1.0 if PlanValidator.validate_task_sequence(tasks) else 0.0

if __name__ == "__main__":
    # Test cases
    valid_plan = ["move_to(table1)", "pick_up(box)", "move_to(shelf)", "place(box)"]
    invalid_plan = ["pick_up(box1)", "pick_up(box2)"]  # Double pick
    invalid_plan2 = ["place(box)"]  # Place without pick
    
    print(f"Valid plan: {PlanValidator.validate_task_sequence(valid_plan)}")
    print(f"Invalid plan (double pick): {PlanValidator.validate_task_sequence(invalid_plan)}")
    print(f"Invalid plan (orphan place): {PlanValidator.validate_task_sequence(invalid_plan2)}")
