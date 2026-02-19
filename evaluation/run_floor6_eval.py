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
from config import TESTCASES_DIR

def run_eval(model: str, provider: str, trials: int, quantization: str):
    logger = BenchmarkingLogger(filename=f"results_{model.replace(':', '_')}_{quantization}.csv")
    client = LLMClient(provider=provider, model=model)

    # Load test case
    instruction_path = os.path.join(TESTCASES_DIR, "floor6", "floor6_instruction.txt")
    with open(instruction_path, 'r') as f:
        instruction = f.read().strip()

    print(f"🚀 Starting evaluation for {model} ({provider}) - {trials} trials")

    for i in tqdm(range(trials)):
        result = client.parse_instruction(instruction)
        result["instruction_id"] = "floor6"
        result["quantization"] = quantization
        
        logger.log_trial(result)

    print(f"✅ Evaluation complete. Results saved to results directory.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LaMMA-P Floor 6 Evaluation Harness")
    parser.add_argument("--model", type=str, required=True, help="LLM model name")
    parser.add_argument("--provider", type=str, default="ollama", choices=["openai", "ollama"], help="LLM provider")
    parser.add_argument("--trials", type=int, default=10, help="Number of trials")
    parser.add_argument("--quantization", type=str, default="none", help="Quantization level (e.g. Q4_K_M)")

    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    run_eval(args.model, args.provider, args.trials, args.quantization)
