import os
import subprocess
import tempfile
from typing import List, Optional

class FastDownwardClient:
    """
    Client to interface with the Fast Downward planner.
    """

    def __init__(self, executable_path: str = "/home/gautham/LaMMA-P/downward/builds/release/bin/downward"):
        self.executable_path = executable_path

    def run_planner(self, domain_path: str, problem_path: str, alias: str = "llama-p-alias") -> Optional[List[str]]:
        """
        Run Fast Downward and return the plan as a list of actions.
        """
        if not os.path.exists(self.executable_path):
            print(f"Error: Fast Downward executable not found at {self.executable_path}")
            return None

        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "sas_plan")
            
            cmd = [
                self.executable_path,
                "--alias", "lama-first", # Using lama-first for balance of speed/quality
                domain_path,
                problem_path
            ]
            
            try:
                # Run the planner
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=tmpdir)
                
                if result.returncode != 0:
                    print(f"Planner failed with return code {result.returncode}")
                    print(f"STDOUT: {result.stdout}")
                    print(f"STDERR: {result.stderr}")
                    return None

                # Look for sas_plan (default output)
                # Note: downward usually writes sas_plan in the CWD
                if os.path.exists(plan_file):
                    with open(plan_file, 'r') as f:
                        lines = f.readlines()
                        # Parse actions, skipping cost line at the end
                        plan = [line.strip().strip('()') for line in lines if not line.startswith(';')]
                        return plan
                else:
                    # Check if it produced multiple plans (sas_plan.1, etc)
                    plans = sorted([f for f in os.listdir(tmpdir) if f.startswith("sas_plan")])
                    if plans:
                        with open(os.path.join(tmpdir, plans[-1]), 'r') as f:
                            lines = f.readlines()
                            plan = [line.strip().strip('()') for line in lines if not line.startswith(';')]
                            return plan
                    
                    print("No plan file generated.")
                    return None

            except Exception as e:
                print(f"Error executing Fast Downward: {e}")
                return None

if __name__ == "__main__":
    # Test stub
    client = FastDownwardClient()
    print("Fast Downward Client initialized.")
