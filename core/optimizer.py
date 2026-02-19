import pulp
import json
import os
from typing import List, Dict, Any

class MILPOptimizer:
    """
    Mixed-Integer Linear Programming optimizer for multi-robot task allocation.
    Uses PuLP to minimize global travel costs while respecting robot capabilities.
    """

    def __init__(self):
        # Load robot profiles
        profiles_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config', 'robot_profiles.json'
        )
        try:
            with open(profiles_path, 'r') as f:
                self.profiles = json.load(f)
        except Exception:
            self.profiles = {}

    def allocate_tasks(self, robots: List[str], tasks: List[str], costs: Dict[str, Dict[str, float]], capabilities: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Allocate tasks to robots to minimize total cost.
        :param robots: List of robot IDs.
        :param tasks: List of task IDs.
        :param costs: Nested dict {robot: {task: cost}}.
        :param capabilities: Dict {robot: [task_type1, task_type2]}.
        :return: Dict {robot: [task1, task2, ...]}.
        """
        # Create the LP problem
        prob = pulp.LpProblem("MultiRobotAllocation", pulp.LpMinimize)

        # Decision variables: x[r][t] = 1 if robot r is assigned to task t
        x = pulp.LpVariable.dicts("x", (robots, tasks), 0, 1, pulp.LpBinary)

        # Objective Function: Minimize total cost
        prob += pulp.lpSum([costs[r][t] * x[r][t] for r in robots for t in tasks])

        # Constraint 1: Each task must be assigned to exactly one robot
        for t in tasks:
            prob += pulp.lpSum([x[r][t] for r in robots]) == 1

        # Constraint 2: Robot must have the capability for the assigned task
        for r in robots:
            # Match robot instance to profile
            profile_name = "limo_standard"
            for p_name in self.profiles:
                if p_name in r:
                    profile_name = p_name
                    break
            profile = self.profiles.get(profile_name, {})
            caps = profile.get("capabilities", [])
            
            for t in tasks:
                # If task requires manipulation but robot lacks it, forbid assignment
                if "pick" in t or "place" in t or "open" in t:
                    if "can_manipulate" not in caps:
                        prob += x[r][t] == 0
                # If task requires sensing but robot lacks it, forbid assignment
                if "detect" in t or "search" in t:
                    if "can_sense" not in caps:
                        prob += x[r][t] == 0

        # Constraint 3: Battery constraints
        # Assume energy cost is proportional to travel cost + fixed task cost
        for r in robots:
            profile_name = "limo_standard"
            for p_name in self.profiles:
                if p_name in r:
                    profile_name = p_name
                    break
            profile = self.profiles.get(profile_name, {})
            # Battery in Wh converted to arbitrary cost units for demo
            capacity = profile.get("battery_capacity_wh", 150) / 10.0 
            
            # Simple energy model: cost[r][t] is the energy consumed
            prob += pulp.lpSum([costs[r][t] * x[r][t] for t in tasks]) <= capacity

        # Solve the problem
        prob.solve(pulp.PULP_CBC_CMD(msg=0))

        # Format output
        allocation = {r: [] for r in robots}
        if pulp.LpStatus[prob.status] == 'Optimal':
            for r in robots:
                for t in tasks:
                    if pulp.value(x[r][t]) == 1:
                        allocation[r].append(t)
        
        return allocation

if __name__ == "__main__":
    # Example usage
    robots = ["limo_1", "limo_2"]
    tasks = ["pick_up_red_block", "move_to_lab"]
    costs = {
        "limo_1": {"pick_up_red_block": 5.0, "move_to_lab": 10.0},
        "limo_2": {"pick_up_red_block": 2.0, "move_to_lab": 15.0}
    }
    
    optimizer = MILPOptimizer()
    result = optimizer.allocate_tasks(robots, tasks, costs, {})
    print(f"Optimal Allocation: {result}")
