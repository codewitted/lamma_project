import csv
import os
import datetime
from typing import Dict, Any

class BenchmarkingLogger:
    def __init__(self, filename: str = "benchmarking_results.csv"):
        from config import RESULTS_DIR
        if not os.path.exists(RESULTS_DIR):
            os.makedirs(RESULTS_DIR)
        
        self.filepath = os.path.join(RESULTS_DIR, filename)
        self.headers = [
            "timestamp", "model", "provider", "instruction_id", 
            "success", "latency", "retries", "json_valid", 
            "fallback_used", "quantization"
        ]
        
        # Initialize file with headers if it doesn't exist
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()

    def log_trial(self, trial_data: Dict[str, Any]):
        """
        Logs a single trial result to the CSV file.
        """
        row = {
            "timestamp": datetime.datetime.now().isoformat(),
            "model": trial_data.get("model", "unknown"),
            "provider": trial_data.get("provider", "unknown"),
            "instruction_id": trial_data.get("instruction_id", "floor6"),
            "success": trial_data.get("success", False),
            "latency": f"{trial_data.get('latency', 0):.4f}",
            "retries": trial_data.get("retries", 0),
            "json_valid": trial_data.get("success", False), # Success implies valid JSON in our flow
            "fallback_used": trial_data.get("fallback_occurred", False),
            "quantization": trial_data.get("quantization", "none")
        }
        
        with open(self.filepath, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow(row)
