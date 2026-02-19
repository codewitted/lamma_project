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
        
        # Helper to convert pred(a,b) to (pred a b)
        def format_predicate(p):
            if "(" in p and ")" in p:
                predicate = p.split("(")[0]
                args = p.split("(")[1].split(")")[0].replace(",", "")
                return f"({predicate} {args})"
            return f"({p})"

        # Convert initial state predicates
        init_preds = ""
        for p in data.get("initial_state", []):
            init_preds += f"    {format_predicate(p)}\n"

        # Convert goal predicates
        goals = ""
        for p in data.get("goal_predicates", []):
            goals += f"      {format_predicate(p)}\n"

        pddl = f"""(define (problem {problem_name})
  (:domain lamma_p_domain)
  (:objects
    {objects} {robots} - object
  )
  (:init
{init_preds}  )
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
