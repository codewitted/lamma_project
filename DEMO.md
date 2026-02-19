# 🚀 AI2-THOR Hybrid Planning Demonstrations

This guide provides step-by-step instructions to run the single-robot and multi-robot demonstrations for the LaMMA-P hybrid planning framework.

## 📋 Prerequisites

Ensure your environment is set up:
```bash
# Activate virtual environment
source venv/bin/bin/activate

# Ensure PYTHONPATH includes the project root
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

---

## 🤖 Demo 1: Single-Robot Visualizer
**Goal**: Move a red block from the Floor 6 hallway to the Floor 2 lab workbench using a single robot.

### Execution
Run the visualizer script:
```bash
python scripts/demo_visualizer.py
```

### What happens:
1.  **LLM Reasoning**: The system parses the natural language instruction into a structured JSON task.
2.  **PDDL Generation**: A symbolic problem is generated based on the parsed intent.
3.  **Fast Downward**: The planner finds a sequence of actions (`move_to`, `pick_up`, `drop`).
4.  **AI2-THOR Execution**: The simulator window opens, and the robot executes the plan.
5.  **Output**: Screenshots are saved as `demo_step_*.png` in the project root.
6.  **Persistence**: The window will remain open until you press **Enter** in the terminal.

---

## 🤖🤝🤖 Demo 2: Heterogeneous Multi-Robot Coordination
**Goal**: Coordinate a `limo_scout` (sensing) and a `limo_heavy` (manipulation) to find and deliver an object, respecting battery constraints.

### Execution
Run the multi-robot demo script:
```bash
python scripts/multi_robot_demo.py
```

### What happens:
1.  **MILP Allocation**: The global optimizer reads `config/robot_profiles.json` and assigns tasks based on capabilities and energy efficiency.
    *   *Scout* gets `search` tasks.
    *   *Heavy* gets `pick/place` tasks.
2.  **Capability-Aware Planning**: Fast Downward generates a coordinated plan where robots only perform actions they are capable of.
3.  **Coordinated Execution**: AI2-THOR simulates the joint mission.
4.  **Logs**: Real-time allocation logs and planning status are printed to the terminal.

---

## 🛠️ Troubleshooting
*   **Unity Crash**: If Unity crashes, ensure your GPU drivers are up to date (`nvidia-smi`). We have optimized `ThorController` to use standard rendering to minimize this.
*   **Planning Failed**: Check `core/domain.pddl` to ensure all actions and types are correctly defined.
