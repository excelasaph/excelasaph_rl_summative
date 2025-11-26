# Daladala Safe-Profit Agent: Learning to Survive Dar es Salaam's Overload-Corruption Trap

## Project Overview

This project applies reinforcement learning to address Tanzania's critical road safety crisis: **42% of road deaths are daladala passengers** (WHO 2023). The average daladala carries **58 passengers in a 33-seater bus**, causing catastrophic accidents due to overloading.

**The Mission**: Train RL agents to discover the optimal balance between profitability and safety—that drivers should operate at optimal capacity and always comply with traffic laws to maximize long-term rewards.

---

## Problem Statement

### The Real-World Context
- **Country**: Tanzania, Dar es Salaam
- **Problem**: Overloaded public transport (daladalas) causes 40% of fatal road accidents
- **Root Cause**: Drivers earn only ~TSh 22,000/day operating legally → forced to overload
- **Challenge**: How can RL teach agents to maximize profit while minimizing crashes and fines?

### Why RL?
Traditional rule-based systems fail because they don't account for:
- Trade-offs between risk (overloading) and reward (more passengers = more income)
- Dynamic decision-making under uncertainty (will I get caught at this police checkpoint?)
- Exploration vs. exploitation

RL discovers this balance autonomously through trial and error.

---

## Environment Design

### Grid Layout
- **15×15 grid** representing the fixed route: **Ubungo → Morocco → Kariakoo → Posta**
- Route traversal: 15 cells right (x=0→14 at y=14), then 15 cells up (y=14→0 at x=14)

### Agent (Daladala Bus)
- **Legal Capacity**: 33 passengers
- **Physical Maximum**: 50 passengers
- **Starting State**: At Ubungo (0, 14), 0 passengers, 0 money

### Stops & Hazards
| Type | Locations | Purpose |
|------|-----------|---------|
| **High-Demand Stops** | (4,14), (8,14), (14,8), (14,3) | Pick up/drop off passengers |
| **Police Checkpoints** | Randomized (3 per episode) | Enforce legal capacity |
| **Traffic Lights** | Randomized (4 per episode) | Cyclic red/green |

---

## Action Space (5 Discrete Actions)

| Action | Code | Effect |
|--------|------|--------|
| **Move Forward** | 0 | Advance 1 cell (progress = +2 reward) |
| **Pick Up Passengers** | 1 | At high-demand stop: +passengers |
| **Drop Off Passengers** | 2 | At high-demand stop: -passengers, +revenue |
| **Stop** | 3 | Decelerate/Hold position (safe at police/lights) |
| **Speed Up** | 4 | Accelerate (RISKY if overloaded/near hazards) |

---

## Observation Space (14 Features, Normalized to [-1, 1])

| Index | Feature | Range | Purpose |
|-------|---------|-------|---------|
| 0 | pos_x | [0, 14] | X coordinate |
| 1 | pos_y | [0, 14] | Y coordinate |
| 2 | current_passengers | [0, 50] | Occupancy level |
| 3 | money_earned | [0, 150000] | TSh earned |
| 4 | current_speed | [0, 3] | Movement speed |
| 5 | light_is_red | {0, 1} | Red light now? |
| 6 | police_checkpoint_here | {0, 1} | Police here? |
| 7 | **must_stop_now** | {0, 1} | **CRITICAL FLAG** (police OR red light) |
| 8 | at_high_demand_stop | {0, 1} | At pickup/dropoff? |
| 9 | passengers_waiting | [0, 10] | Demand at current stop |
| 10 | must_stop_next | {0, 1} | Hazard in next cell? |
| 11 | distance_to_traffic_light | Lookahead | Traffic light proximity |
| 12 | distance_to_police | Lookahead | Police checkpoint proximity |
| 13 | episode_progress | [0, 1] | Step count / max_steps |

---

## Reward Structure

### Progress & Delivery
- **+2**: Per step forward (encourage efficiency)
- **+12**: Per passenger dropped off
- **+100**: Reaching final destination (Posta)
- **+50**: Perfect legal trip bonus (≤33 passengers at Posta)

### Safety & Compliance
- **+25**: Voluntarily stopping at police/red light (`must_stop_now=1` AND action=3)
- **-40**: Ignoring police/red light (action≠3 when `must_stop_now=1`)
- **+15**: Valid pickup at stop
- **-3**: Unnecessary stop

### Penalties
- **-20**: Light fine (34–40 passengers at police checkpoint)
- **-50**: Heavy fine + episode ends (>40 passengers at police)
- **-30**: Accident + episode ends (overloaded + speeding)
- **-5 to -8**: Invalid pickup/dropoff actions

---

## Terminal Conditions

**Success**:
- Reach Posta (final cell)

**Failure**:
- Caught with >40 passengers at police checkpoint
- Accident (overloaded + speeding)

**Truncation**:
- 350 steps elapsed without success/failure

---

## RL Algorithms Implemented

### 1. **DQN** (Value-Based)
- **Architecture**: MLP policy (14 → 64 → 64 → 5)
- **Training**: 300,000 timesteps
- **Hyperparameters Tuned**: 12 configurations
  - Learning rates: 1e-4, 3e-4, 5e-4, 7e-4, 1e-3
  - Buffer sizes: 10k, 50k, 100k
  - Exploration fractions: 0.25, 0.5, 1.0

### 2. **PPO** (Policy Gradient)
- **Architecture**: MLP policy (14 → 64 → 64 → 5)
- **Training**: 300,000 timesteps
- **Hyperparameters Tuned**: 12 configurations
  - Learning rates: 1e-4, 3e-4, 5e-4, 7e-4, 1e-3
  - Entropy coefficients: 0.0, 0.005, 0.01
  - n_steps: 512, 1024, 2048

### 3. **A2C** (Actor-Critic)
- **Architecture**: MLP policy (14 → 64 → 64 → 5)
- **Training**: 300,000 timesteps
- **Hyperparameters Tuned**: 12 configurations
  - Learning rates: 1e-4, 3e-4, 5e-4, 7e-4, 1e-3
  - Gamma values: 0.65, 0.70, 0.75, 0.80, 0.90, 0.95, 0.995
  - n_steps: 5, 8, 10
  - Entropy coefficients: 0.0, 0.005, 0.01, 0.05

### 4. **REINFORCE** (Policy Gradient)
- **Architecture**: Neural network policy (14 → hidden → hidden → 5)
- **Training**: 300,000 timesteps
- **Hyperparameters Tuned**: 12 configurations
  - Learning rates: 1e-3, 3e-3, 5e-3, 1e-2
  - Hidden sizes: 64, 128, 256

---

## Project Structure

```
project_root/
├── environment/
│   ├── __init__.py
│   ├── daladala_env.py           # Gymnasium environment
│   └── rendering.py              # Pygame visualization
├── training/
│   ├── dqn_training.py           # DQN training (12 configs)
│   ├── ppo_training.py           # PPO training (12 configs)
│   ├── a2c_training.py           # A2C training (12 configs)
│   └── reinforce_training.py     # REINFORCE training (12 configs)
├── models/
│   ├── dqn/best_dqn.zip          # Best DQN model
│   ├── ppo/best_ppo.zip          # Best PPO model
│   ├── a2c/best_a2c.zip          # Best A2C model
│   └── reinforce/best_reinforce_policy.pth  # Best REINFORCE model
├── results/
│   ├── dqn_results.json
│   ├── ppo_results.json
│   ├── a2c_results.json
│   ├── reinforce_results.json
│   └── plots/                    # Generated analysis plots
├── notebooks/                    # Colab notebooks for training
├── random_demo2.py               # Realistic Pygame demo
├── generate_plots.py             # Generate analysis plots
├── generate_convergence_plots.py # Generate convergence plots
├── generalization_test.py        # Test generalization
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

---

## Installation & Usage

### Requirements
- Python 3.8+
- See `requirements.txt` for exact dependencies

### Setup
```bash
pip install -r requirements.txt
```

### Training All Models (12 configurations each)
```bash
# Train DQN (300k steps, ~30 min)
python training/dqn_training.py

# Train PPO (300k steps, ~25 min)
python training/ppo_training.py

# Train A2C (300k steps, ~20 min)
python training/a2c_training.py

# Train REINFORCE (3000 episodes, ~40 min)
python training/reinforce_training.py
```

Results saved to `results/*.json`.

### Visualize Random Agent (No Training)
```bash
python random_demo2.py
# Generates: random_demo-pygame.gif
```

### Generate Analysis Plots
```bash
python generate_plots.py
python generate_convergence_plots.py
python generalization_test.py
# Saves plots to results/plots/
```

### Run Best Model (Interactive Play)
```bash
python record_agent_demo.py
# Records GIF of trained agent
```

---

## Key Findings

### Expected Agent Behavior
After training, agents should discover:
1. **Safe operation**: Maximize passengers up to legal limit (33) or slightly above (34-40) if safe, but strictly avoid >40 (severe penalty).
2. **Traffic compliance**: Always stop at police/red lights (mandatory to avoid -40 penalty).
3. **Efficiency**: Minimize stops where unnecessary to maximize progress rewards.

### Why This Works
- **Legal operation**: High rewards from passenger delivery (+12/pax) and completion bonuses (+100 + 50).
- **Reckless overloading** (>40 pax): -50 heavy fine OR -30 crash = CATASTROPHE.
- **Traffic violation**: -40 penalty per violation, accumulates quickly.

**Equilibrium**: Maximize passengers within safe limits, obey all traffic laws → highest long-term expected reward (~430).

---

## Visualization

### Environment Components
- **Sandy road**: Route cells in brown
- **Gold circles**: High-demand stops (pickup/dropoff)
- **Blue rectangles**: Police checkpoints
- **Red/Green circles**: Traffic lights
- **Green rectangle with number**: Daladala bus (shows passenger count)
- **HUD**: Real-time step, passengers, money, action, reward

### Pygame Rendering
- Frame rate: 12 FPS (adjustable)
- Supports both `human` mode (live display) and `rgb_array` (capture frames for GIF)

---

## Analysis & Visualization

We generate three key types of analysis plots to evaluate agent performance:

1.  **Cumulative Rewards**: Compares the mean reward and variance of the best models for each algorithm over 100 evaluation episodes.
2.  **Convergence Analysis**: Tracks the training progress (smoothed reward curves) to determine how quickly each algorithm learns.
3.  **Generalization Test**: Evaluates the agents on unseen "edge case" scenarios (e.g., Heavy Traffic, Police State) to test robustness.

---

## Results Summary

See `results/plots/` for generated visualizations.

**Findings**:
1. **DQN**: Highest peak performance (~431 reward), excellent safety compliance.
2. **PPO**: Fastest convergence (~450 episodes) and best generalization to new scenarios.
3. **A2C**: Good initial learning but higher variance.
4. **REINFORCE**: Slowest convergence and high instability.

---

## How to Run the Entire Pipeline

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train all 4 algorithms (48 total configurations)
python training/dqn_training.py
python training/ppo_training.py
python training/a2c_training.py
python training/reinforce_training.py

# 3. Generate random demo GIF
python random_demo2.py

# 4. Generate analysis plots
python generate_plots.py
python generate_convergence_plots.py
python generalization_test.py

# 5. Record trained agent demo
python record_agent_demo.py
```

**Total training time**: ~2–3 hours on CPU, results saved for later analysis.

---

## Rubric Alignment

| Criterion | Our Approach |
|-----------|--------------|
| **Environment Validity** | ✓ 15×15 grid, realistic route, comprehensive action/observation spaces |
| **Policy Training** | ✓ 4 algorithms, 12 configs each, deterministic evaluation |
| **Visualization** | ✓ Pygame 2D with interactive GUI, real-time HUD |
| **SB3 Implementation** | ✓ DQN, PPO, A2C from stable-baselines3 + custom REINFORCE |
| **Hyperparameter Tuning** | ✓ 48 total configurations (12 per algorithm) |
| **Metrics & Analysis** | ✓ Comparison table, convergence analysis, safety metrics |

---

## Non-Generic Use Case

This project **directly addresses Tanzania's #1 road safety killer**:
- **Real problem**: 4–6 hours/day traffic, 40% of fatal accidents from overloaded buses
- **Real context**: Corruption (bribes) enables overloading despite legal limits
- **Real economy**: Drivers earn poverty wages, forced to overload
- **RL solution**: Discover sustainable profit-safety equilibrium

Unlike generic grid-world environments, our reward structure embeds real-world constraints:
- Police checkpoints (law enforcement)
- Traffic lights (infrastructure)
- Overloading penalties (safety)

---

## Contact & Credits

**Project**: Daladala Safe-Profit Agent  
**Author**: Student name  
**Institution**: [University]  
**Date**: November 2025  
**Reference**: LATRA (2023) - Tanzania road safety statistics

---

## License

This project is submitted as part of a summative assignment. All code is provided for educational purposes.
