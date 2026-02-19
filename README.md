# LaMMA-P Benchmarking Framework

A production-grade research artifact for evaluating LLM performance in robotics planning tasks, specifically for the LaMMA-P pipeline.

## 🏗 Directory Structure

```
lamma_p_bench/
├── config.py           # Environment and global configuration
├── core/
│   ├── llm_client.py   # Swappable LLM adapter (OpenAI/Ollama)
│   ├── schema.py       # JSON schema enforcement and validation
│   └── logger.py       # Benchmarking CSV logger
├── evaluation/
│   ├── run_floor6_eval.py    # Main evaluation harness
│   └── visualize_results.py  # Result visualization script
├── testcases/
│   └── floor6/         # "Floor 6" evaluation data
├── results/            # Benchmark outputs and charts
├── requirements.txt    # Project dependencies
└── example.env         # Environment variable template
```

## 🚀 Getting Started

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Configuration

Copy `example.env` to `.env` and configure your providers:

```bash
cp example.env .env
# Edit .env with your LLM_MODEL, OPENAI_API_KEY, etc.
```

### 3. Running Benchmarks

To run the "Floor 6" evaluation for a specific model:

```bash
# Evaluate a local model via Ollama
python evaluation/run_floor6_eval.py --model mistral:7b --provider ollama --trials 10

# Evaluate a cloud model via OpenAI
python evaluation/run_floor6_eval.py --model gpt-4o --provider openai --trials 5
```

### 4. Visualizing Results

After running benchmarks, generate comparison charts:

```bash
python evaluation/visualize_results.py
```

Results will be saved in the `results/` directory as CSVs and PNG charts.

## 🔬 Research Features

- **JSON Schema Enforcement**: Uses Pydantic to ensure LLM outputs always match the required robotics task structure.
- **Deterministic Evaluation**: Fixed test cases and temperature = 0.
- **Hybrid Fallback**: Optional automatic fallback to cloud LLMs if local models fail validation.
- **Reproducibility**: Comprehensive CSV logging including latency, retry counts, and validity rates.
