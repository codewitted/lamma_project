import argparse
import os
import sys
import json
import logging
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_client import LLMClient
from core.logger import BenchmarkingLogger
from core.validator import PlanValidator
from config import TESTCASES_DIR

def run_eval(model: str, provider: str, trials: int, quantization: str, testcase: str):
    logger = BenchmarkingLogger(filename=f"results_{model.replace(':', '_')}_{quantization}.csv")
    client = LLMClient(provider=provider, model=model)

    # Load test case
    testcase_dir = os.path.join(TESTCASES_DIR, testcase)
    
    # Try multiple naming conventions for instruction
    instruction_variants = [f"{testcase}_instruction.txt", "instruction.txt"]
    instruction = ""
    for v in instruction_variants:
        p = os.path.join(testcase_dir, v)
        if os.path.exists(p):
            with open(p, 'r') as f:
                instruction = f.read().strip()
            break
    
    if not instruction:
        logging.error(f"Could not find instruction for testcase {testcase}")
        return

    # Load initial state if exists
    initial_state_path = os.path.join(testcase_dir, "initial_state.json")
    if not os.path.exists(initial_state_path):
         initial_state_path = os.path.join(testcase_dir, f"{testcase}_initial_state.json")
    
    initial_state_data = {}
    if os.path.exists(initial_state_path):
        with open(initial_state_path, 'r') as f:
            initial_state_data = json.load(f)

    print(f"🚀 Starting evaluation for {model} ({provider}) - {trials} trials on testcase: {testcase}")

    for i in tqdm(range(trials)):
        # Inject initial state context if available
        prompt = instruction
        if initial_state_data:
            prompt = f"Environment State: {json.dumps(initial_state_data.get('initial_state', []))}\n\nTask: {instruction}"

        result = client.parse_instruction(prompt)
        result["instruction_id"] = testcase
        result["quantization"] = quantization
        
        # Calculate logical consistency score
        tasks = result.get("tasks", [])
        initial_preds = initial_state_data.get("initial_state", [])
        logical_score = PlanValidator.calculate_logical_score(tasks, initial_preds)
        result["logical_score"] = logical_score
        
        logger.log_trial(result)

    print(f"✅ Evaluation complete. Results saved to results directory.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LaMMA-P Evaluation Harness")
    parser.add_argument("--model", type=str, required=True, help="LLM model name")
    parser.add_argument("--provider", type=str, default="ollama", choices=["openai", "ollama"], help="LLM provider")
    parser.add_argument("--trials", type=int, default=10, help="Number of trials")
    parser.add_argument("--quantization", type=str, default="none", help="Quantization level (e.g. Q4_K_M)")
    parser.add_argument("--testcase", type=str, default="floor6", help="Name of the testcase folder")

    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    run_eval(args.model, args.provider, args.trials, args.quantization, args.testcase)
