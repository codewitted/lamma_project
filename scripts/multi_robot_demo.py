import logging
import json
from core.llm_client import LLMClient
from core.pddl_generator import PDDLGenerator
from core.optimizer import MILPOptimizer
from core.planner_client import FastDownwardClient
from core.thor_controller import ThorController

def run_multi_robot_demo():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Starting Heterogeneous Multi-Robot Demonstration")
    
    # 1. Setup
    llm = LLMClient()
    pddl_gen = PDDLGenerator()
    optimizer = MILPOptimizer()
    planner = FastDownwardClient()
    thor = ThorController(scene="FloorPlan1", num_agents=2) # 2 robots for demo
    
    instruction = "limo_scout1 search for the red_block. limo_heavy1 pick it up from floor6_hallway and place it on floor2_lab workbench."
    
    print("\n--- [Step 1: LLM Semantic Reasoning] ---")
    result = llm.parse_instruction(instruction)
    if not result['success']:
        print("❌ LLM Failed")
        return
    data = result['data']
    print(f"Parsed Entities: {data.get('objects')} | Robots: {data.get('robots')}")

    print("\n--- [Step 2: MILP Global Optimization (Energy Aware)] ---")
    robots = ["limo_scout1", "limo_heavy1"]
    tasks = ["search_red_block", "pick_up_red_block", "move_to_lab", "place_on_workbench"]
    
    # Mocking costs based on travel/effort
    costs = {
        "limo_scout1": {"search_red_block": 1.0, "pick_up_red_block": 10.0, "move_to_lab": 2.0, "place_on_workbench": 10.0},
        "limo_heavy1": {"search_red_block": 5.0, "pick_up_red_block": 2.0, "move_to_lab": 5.0, "place_on_workbench": 2.0}
    }
    
    allocation = optimizer.allocate_tasks(robots, tasks, costs, {})
    print(f"Allocations: {allocation}")
    # Verification: Scout should have search, Heavy should have pick/place

    print("\n--- [Step 3: Symbolic Planning for Multi-Robot] ---")
    pddl_problem = pddl_gen.generate_problem_skeleton(data)
    with open("multi_demo_problem.pddl", "w") as f:
        f.write(pddl_problem)
        
    plan = planner.run_planner("core/domain.pddl", "multi_demo_problem.pddl")
    if plan:
        print(f"Sequential Plan Found: {plan}")
        
        print("\n--- [Step 4: AI2-THOR Multi-Robot Execution] ---")
        # In this demo, we execute sequentially for visual clarity
        thor.execute_plan(plan, wait_at_end=False)
        
        # New: 360 Cinematic Overview
        thor.cinematic_pan()
        
        print("🏁 Multi-Robot Demonstration Complete!")
    else:
        print("❌ Planning failed. Check domain/initial state.")

if __name__ == "__main__":
    run_multi_robot_demo()
