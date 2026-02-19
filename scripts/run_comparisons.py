import subprocess
import os
import sys

# Define models to compare
MODELS = [
    {"name": "mistral:7b", "provider": "ollama", "quantization": "Q4_K_M"},
    {"name": "phi:latest", "provider": "ollama", "quantization": "none"},
    {"name": "gpt-4o", "provider": "openai", "quantization": "none"}
]

TRIALS = 5  # Default trials for quick ablation

def run_ablation():
    print("🚀 Starting Comparative Ablation Study...")
    
    for model in MODELS:
        print(f"\n--- Evaluating Model: {model['name']} ---")
        cmd = [
            "python3", "evaluation/run_eval.py",
            "--model", model["name"],
            "--provider", model["provider"],
            "--trials", str(TRIALS),
            "--quantization", model["quantization"],
            "--testcase", "lab_maintenance"
        ]
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to evaluate {model['name']}: {e}")

    print("\n📊 Generating Research Visualizations...")
    subprocess.run(["python3", "evaluation/visualize_results.py"])
    print("\n✅ Ablation Study Complete.")

if __name__ == "__main__":
    run_ablation()
