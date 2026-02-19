# Walkthrough - LaMMA-P Benchmarking Framework

This walkthrough demonstrates the features and usage of the modular benchmarking framework designed for the LaMMA-P robotics project.

## 🏗 System Design

The system is built to be modular and research-ready, with a clear separation between LLM interaction, data validation, and performance evaluation.

```mermaid
graph TD
    A[run_eval.py] --> B[LLMClient]
    B --> C{Provider?}
    C -- OpenAI --> D[GPT-4o/etc]
    C -- Ollama --> E[Local Models]
    C -- Open WebUI --> L[Centralized Local Hub]
    B --> F[Schema Validator]
    F --> G[RoboticsTaskSchema]
    A --> H[BenchmarkingLogger]
    H --> I[results.csv]
    
    subgraph "Hybrid Planning Pipeline"
        M[scripts/lamma_test_node.py] --> B
        M --> O[MILPOptimizer]
        M --> P[PDDLGenerator]
        P --> Q[FastDownwardClient]
        Q --> R[Executable Action Plan]
    end
    
    J[visualize_results.py] --> I
    J --> K[PNG Charts]
```

## 🛠 Key Features

### 1. Swappable LLM Adapter (Open WebUI Support)
The `LLMClient` provides a unified interface for OpenAI, Ollama, and **Open WebUI**. This allows you to leverage your existing local infrastructure while minimizing costs.

### 2. Strict JSON Schema Enforcement
We use **Pydantic** to define a strict schema for robotics tasks. Any response that doesn't match the schema is automatically rejected and retried once.

### 3. State-Aware Logical Validation
The `PlanValidator` now tracks object states (opened/closed, toggleable on/off). It enforces physical constraints from AI2-THOR, such as:
- **Container Constraint**: Cannot pick up an object from a closed fridge or drawer.
- **State Constraint**: Cannot place an object inside a closed microwave.
- **Toggleable Support**: Tracks the state of machines like coffee makers or stoves.

### 4. Advanced PDDL Generation
The `PDDLGenerator` supports **initial state predicates** and is aligned with AI2-THOR's logical representation (`opened`, `closed`, `switchedOn`). This ensures plans are compatible with standard symbolic planners.

### 5. AI2-THOR Benchmarking Scenarios
We've generalized the evaluation harness to support AI2-THOR floor plans (e.g., `FloorPlan1`) and object categories.
- **Kitchen Breakfast**: A dedicated test case where the agent must interact with a fridge, microwave, and coffee machine.
- **Lab Maintenance**: A multi-step cleaning task.

## 📈 Example Result Visualization

After running a benchmark, the `visualize_results.py` script aggregates all trials and generates comparative analysis:

- **Execution Readiness**: Compares JSON validity and logical consistency across different models.
- **Latency Analysis**: Compares the average token generation speed across different models and quantizations.

## 📝 Usage Commands

### Run AI2-THOR Evaluation
```bash
python evaluation/run_eval.py --model mistral:7b --provider openwebui --trials 10 --testcase kitchen_breakfast
```

### Start ROS2 Test Node (MOCK Mode)
```bash
python scripts/lamma_test_node.py
```

### Run Automated Ablation Study
```bash
python scripts/run_comparisons.py
```

### Generate Plots
```bash
python evaluation/visualize_results.py
```

## 🔬 Research & Defensive Strategies

As a production-grade research artefact, the system anticipates common failure points in LLM-driven robotics:

| Failure Point | Defensive Strategy |
| :--- | :--- |
| **Malformed JSON** | Pydantic validation + 1 automatic retry (Temperature=0). |
| **Local LLM Latency** | Asynchronous-ready calls and standardized latency logging. |
| **Model Hallucination** | System prompt enforcement + Schema validation. |
| **Connectivity Breaks** | `FALLBACK_TO_CLOUD` option allows seamless failover to OpenAI. |
| **Reproducibility** | Fixed random seeds (Temp=0) and explicit quantization logging. |

### 6. Constraint-Driven Optimization (MILP)
The system now includes a `MILPOptimizer` (`core/optimizer.py`) using PuLP to:
- **Minimize Global Utility**: Allocates tasks to robots based on travel costs.
- **Support Multi-Robot Coordination**: Handles task distribution across LIMO robots.

### 7. Symbolic Planning with Fast Downward
The `FastDownwardClient` (`core/planner_client.py`) bridges LLM reasoning with executable plans:
- **PDDL Translation**: Generates PDDL problem files from instructions.
- **Robust Planning**: Invokes Fast Downward to find optimal action sequences.

## 🏁 The Finished Product: End-to-End Walkthrough

The system operates as a **Hybrid Planning Brain** for LIMO robots, coordinating semantic intent with mathematical and logical rigor.

```mermaid
sequenceDiagram
    participant U as User (Natural Language)
    participant L as LLM Client (Semantic)
    participant O as MILP Optimizer (Math)
    participant G as PDDL Generator
    participant P as Fast Downward (Logic)
    participant R as LIMO Robots (ROS 2/Gazebo)

    U->>L: "Pick up kit on Floor 6, move to Lab"
    L->>O: Structured Tasks & Constraints
    O->>G: Optimized Task Allocation
    G->>P: PDDL Domain + Problem
    P->>R: Sequential Action Plan (Move, Pick, Place)
```

### 1. Semantic Reasoning (LLM)
The **LLM Client** interprets complex instructions like *"Prioritize Limo 2 for the heavy lifting"*, identifying goals and constraints that are hard to hardcode.

### 2. Global Utility Optimization (MILP)
The **MILP Optimizer** (`core/optimizer.py`) ensures global efficiency. It assigns tasks to the closest or most capable robot, minimizing battery drain and transit time.

### 3. Symbolic Planning (Fast Downward)
**Fast Downward** computes the exact, collision-free path. It respects physical constraints (like closed doors or avoiding elevators) defined in the PDDL domain.

### 4. ROS 2 Coordination
The **ROS 2 Node** (`scripts/lamma_test_node.py`) serves as the central hub, publishing optimized action plans that robots can execute in **AI2-THOR**, **Gazebo**, or the **Real World**.

## 🚀 Research Readiness
This framework generates all the data needed for publication-level reporting:
- **Success Rate Charts**: Comparative performance of LLMs.
- **Optimization Surface**: Efficiency gains from MILP.
- **Planning Latency**: Benchmarking local vs. cloud execution.
- **Visual Evidence**: State traces from AI2-THOR Floor 6.
