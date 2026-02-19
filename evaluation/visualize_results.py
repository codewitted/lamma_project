import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RESULTS_DIR

def generate_comparison_charts():
    # Load all CSV results
    all_files = glob.glob(os.path.join(RESULTS_DIR, "*.csv"))
    if not all_files:
        print("No result files found in results directory.")
        return

    dfs = []
    for f in all_files:
        dfs.append(pd.read_csv(f))
    
    df = pd.concat(dfs, ignore_index=True)
    
    # Calculate metrics grouped by model and provider
    metrics = df.groupby(['model', 'provider']).agg({
        'success': 'mean',
        'logical_score': 'mean',
        'latency': ['mean', 'std'],
        'retries': 'mean'
    }).reset_index()

    metrics.columns = ['model', 'provider', 'validity_rate', 'logical_rate', 'latency_mean', 'latency_std', 'avg_retries']
    metrics['validity_rate'] *= 100
    metrics['logical_rate'] *= 100

    # Professional Plotting Style
    plt.style.use('ggplot')
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6']

    # Plot Success Rate
    plt.figure(figsize=(10, 6))
    x = range(len(metrics))
    width = 0.35
    
    plt.bar([i - width/2 for i in x], metrics['validity_rate'], width, label='JSON Validity', color='#3498db')
    plt.bar([i + width/2 for i in x], metrics['logical_rate'], width, label='Logical Consistency', color='#2ecc71')
    
    plt.title('Execution Readiness Analysis', fontsize=14, fontweight='bold')
    plt.ylabel('Success Rate (%)', fontsize=12)
    plt.xticks(x, metrics['model'], rotation=45)
    plt.legend()
    plt.ylim(0, 105)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'success_rate_comparison.png'), dpi=300)
    print(f"Generated success_rate_comparison.png")

    # Plot Latency with Error Bars
    plt.figure(figsize=(10, 6))
    plt.bar(metrics['model'], metrics['latency_mean'], yerr=metrics['latency_std'], 
            capsize=5, color='#e67e22', alpha=0.8)
    plt.title('Parsing Latency Analysis (Mean ± Std)', fontsize=14, fontweight='bold')
    plt.ylabel('Time (seconds)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'latency_comparison.png'), dpi=300)
    print(f"Generated latency_comparison.png")

    # Print Summary Table for Research Notes
    print("\n--- Research Summary Table ---")
    print(metrics[['model', 'validity_rate', 'latency_mean', 'avg_retries']].to_markdown(index=False))

if __name__ == "__main__":
    generate_comparison_charts()
