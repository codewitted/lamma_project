#!/usr/bin/env python3
import sys
import os
import json
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_client import LLMClient
from core.pddl_generator import PDDLGenerator
from core.optimizer import MILPOptimizer
from core.planner_client import FastDownwardClient
from core.thor_controller import ThorController

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    instruction = "Pick up the red block from Floor 6 hallway, move it to the lab on Floor 2, and place it on the workbench."
    print(f"🌟 Starting Visual Demonstration: {instruction}")
    
    # 1. LLM Parsing
    print("\n--- [Step 1: LLM Semantic Reasoning] ---")
    client = LLMClient()
    result = client.parse_instruction(instruction)
    if not result['success']:
        print("❌ LLM Parsing failed.")
        return
    data = result['data']
    print(f"Parsed JSON: {json.dumps(data, indent=2)}")

    # 2. MILP Optimization
    print("\n--- [Step 2: MILP Global Optimization] ---")
    optimizer = MILPOptimizer()
    robots = data.get('robots', ['turtlebot3_1'])
    tasks = data.get('tasks', [])
    costs = {r: {t: 1.0 for t in tasks} for r in robots}
    allocation = optimizer.allocate_tasks(robots, tasks, costs, {})
    print(f"Allocations: {allocation}")

    # 3. PDDL Generation & Planning
    print("\n--- [Step 3: Symbolic Planning (Fast Downward)] ---")
    pddl_gen = PDDLGenerator()
    planner = FastDownwardClient()
    domain_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core', 'domain.pddl')
    
    pddl_problem = pddl_gen.generate_problem_skeleton(data)
    with open("demo_problem.pddl", "w") as f:
        f.write(pddl_problem)
    
    plan = planner.run_planner(domain_path, "demo_problem.pddl")
    if not plan:
        print("❌ Planning failed.")
        return
    print(f"Sequential Plan: {plan}")

    # 4. AI2-THOR Execution
    print("\n--- [Step 4: AI2-THOR Visual Execution] ---")
    # For the purpose of the demo, we might use a standard scene like FloorPlan1
    # since FloorPlan6 might not literally be "Floor 6" in the way requested.
    # We will try FloorPlan1 (Kitchen) as a default if FloorPlan6 isn't found.
    try:
        thor = ThorController(scene="FloorPlan1") # Common reliable scene
        print("Simulator started. Running actions...")
        thor.execute_plan(plan)
        print("🏁 Visual Demonstration Complete!")
    except Exception as e:
        print(f"❌ Simulator error: {e}")
        print("Note: AI2-THOR usually requires an X display (Xvfb) on headless servers.")

if __name__ == "__main__":
    main()
