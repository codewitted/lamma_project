import json
from typing import Dict, Any

class PDDLGenerator:
    """
    Utility to convert RoboticsTaskSchema JSON into PDDL problem snippets.
    Suitable for integration with Fast Downward or ROS2 planning nodes.
    """
    
    @staticmethod
    def generate_problem_skeleton(data: Dict[str, Any], problem_name: str = "robotics_task") -> str:
        # Extract robots explicitly
        robots = set(data.get("robots", []))
        if not robots:
            robots.add("robot1") # Default fallback
            
        # Extract all potential entities
        all_entities = set(data.get("objects", []))
        all_entities.update(robots)
        
        # Helper to extract args from pred(a,b)
        def get_args(p):
            p = p.strip()
            if "(" in p and ")" in p:
                return [a.strip() for a in p.split("(")[1].split(")")[0].split(",")]
            return [p]

        # Scan initial state and goals for missing entities (locations, etc)
        initial_state = data.get("initial_state", [])
        for p in initial_state + data.get("goal_predicates", []):
            all_entities.update(get_args(p))

        # Ensure each robot has at least one initial 'at' position
        has_at = {r: False for r in robots}
        for r in robots:
            for p in initial_state:
                if f"at({r}" in p.lower() or f"at ({r}" in p.lower():
                    has_at[r] = True
            
            if not has_at[r]:
                # Fallback start position for demo
                initial_state.append(f"at({r}, floor6_charging_dock)")
                all_entities.add("floor6_charging_dock")

        # Format objects string: robots as one type, rest as target
        others = all_entities - robots
        objects_str = ""
        if robots:
            objects_str += f"    {' '.join(robots)} - robot\n"
        if others:
            objects_str += f"    {' '.join(others)} - target"
        
        # Helper to convert pred(a,b) to (pred a b)
        def format_predicate(p):
            p = p.lower().strip()
            if "(" in p and ")" in p:
                predicate = p.split("(")[0]
                args = [a.strip() for a in p.split("(")[1].split(")")[0].split(",")]
                return f"({predicate} {' '.join(args)})"
            return f"({p})"

        # Convert initial state predicates
        init_preds = ""
        for p in initial_state:
            init_preds += f"    {format_predicate(p)}\n"

        # Convert goal predicates
        goals = ""
        for p in data.get("goal_predicates", []):
            goals += f"      {format_predicate(p)}\n"

        pddl = f"""(define (problem {problem_name})
  (:domain lamma_p_domain)
  (:objects
{objects_str}
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
