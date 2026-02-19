import json
from typing import Dict, Any

class PDDLGenerator:
    """
    Utility to convert RoboticsTaskSchema JSON into PDDL problem snippets.
    Suitable for integration with Fast Downward or ROS2 planning nodes.
    """
    
    @staticmethod
    def generate_problem_skeleton(data: Dict[str, Any], problem_name: str = "robotics_task") -> str:
        objects = " ".join(data.get("objects", []))
        robots = " ".join(data.get("robots", []))
        
        # Convert goal predicates to PDDL list format: (at block workbench)
        goals = ""
        for goal in data.get("goal_predicates", []):
            # Simple conversion: at(a, b) -> (at a b)
            if "(" in goal and ")" in goal:
                predicate = goal.split("(")[0]
                args = goal.split("(")[1].split(")")[0].replace(",", "")
                goals += f"      ({predicate} {args})\n"
            else:
                goals += f"      ({goal})\n"

        pddl = f"""(define (problem {problem_name})
  (:domain lamma_p_domain)
  (:objects
    {objects} {robots} - object
  )
  (:init
    ; Initial state to be filled from sensor data
  )
  (:goal
    (and
{goals}    )
  )
)
"""
        return pddl

if __name__ == "__main__":
    # Test with example
    example_data = {
        "tasks": ["pick_up(red_block)", "move_to(floor2_lab)"],
        "objects": ["red_block", "workbench"],
        "robots": ["turtlebot3_1"],
        "goal_predicates": ["at(red_block, workbench)", "on(red_block, workbench)"]
    }
    print(PDDLGenerator.generate_problem_skeleton(example_data))
