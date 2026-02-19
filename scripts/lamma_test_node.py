#!/usr/bin/env python3
import sys
import os
import json

# Mock ROS2 rclpy if not installed
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
except ImportError:
    print("⚠️ ROS2 (rclpy) not found. Running in MOCK mode.")
    class Node:
        def __init__(self, name): self.name = name
        def create_subscription(self, type, topic, cb, qos): print(f"Subscribed to {topic}")
        def create_publisher(self, type, topic, qos): 
            class Pub:
                def publish(self, msg): print(f"Published to {topic}: {msg.data}")
            return Pub()
        def get_logger(self):
            class Logger:
                def info(self, msg): print(f"[INFO] {msg}")
            return Logger()
    class String:
        def __init__(self): self.data = ""

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_client import LLMClient
from core.pddl_generator import PDDLGenerator
from core.optimizer import MILPOptimizer
from core.planner_client import FastDownwardClient

class LaMMATestNode(Node):
    def __init__(self):
        super().__init__('lamma_test_node')
        self.client = LLMClient()
        self.pddl_gen = PDDLGenerator()
        self.optimizer = MILPOptimizer()
        self.planner = FastDownwardClient()
        
        # PDDL Domain path (aligned with LaMMA-P architecture)
        self.domain_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'core', 'domain.pddl'
        )

        # ROS2 Interface
        self.subscription = self.create_subscription(
            String,
            'lamma/instruction',
            self.listener_callback,
            10
        )
        self.publisher = self.create_publisher(String, 'lamma/action_plan', 10)
        self.get_logger().info("LaMMA Test Node Initialized (Hybrid Pipeline). Listening on /lamma/instruction")

    def listener_callback(self, msg):
        instruction = msg.data
        self.get_logger().info(f"Received instruction: {instruction}")
        
        # 1. Parse via LLM (Semantic Reasoning)
        result = self.client.parse_instruction(instruction)
        
        if result['success']:
            data = result['data']
            
            # 2. Optimize Task Allocation (MILP)
            # For demonstration, we assume identity costs if not provided
            robots = data.get('robots', ['limo_1'])
            tasks = data.get('tasks', [])
            costs = {r: {t: 1.0 for t in tasks} for r in robots}
            allocation = self.optimizer.allocate_tasks(robots, tasks, costs, {})
            self.get_logger().info(f"Optimized Allocation: {allocation}")

            # 3. Generate PDDL (Structured Planning)
            pddl_problem = self.pddl_gen.generate_problem_skeleton(data)
            
            # Save temporary problem file
            with open("temp_problem.pddl", "w") as f:
                f.write(pddl_problem)
            
            # 4. Invoke Fast Downward
            plan = self.planner.run_planner(self.domain_path, "temp_problem.pddl")
            
            if plan:
                # Publish Plan
                out_msg = String()
                out_msg.data = json.dumps({"plan": plan, "allocation": allocation})
                self.publisher.publish(out_msg)
                self.get_logger().info(f"Action plan generated and published: {plan}")
            else:
                self.get_logger().info("Fast Downward failed to find a plan.")
        else:
            self.get_logger().info("LLM failed to parse instruction.")

def main(args=None):
    if 'rclpy' in sys.modules:
        rclpy.init(args=args)
        node = LaMMATestNode()
        rclpy.spin(node)
        node.destroy_node()
        rclpy.shutdown()
    else:
        # Manual test if rclpy is missing
        node = LaMMATestNode()
        msg = String()
        msg.data = "Pick up the red block from the microwave."
        node.listener_callback(msg)

if __name__ == '__main__':
    main()
