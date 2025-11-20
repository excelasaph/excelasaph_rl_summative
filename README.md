# Daladala Safe-Profit Agent: Learning to Survive Dar es Salaam's Overload-Corruption Trap

## Project Overview

This project applies reinforcement learning to address Tanzania's critical road safety crisis: **42% of road deaths are daladala passengers** (WHO 2023). The average daladala carries **58 passengers in a 33-seater bus**, causing catastrophic accidents due to overloading.

**The Mission**: Train RL agents to discover the optimal balance between profitability and safety—that drivers should operate at 34–38 passengers, reject ~75% of bribes, and always comply with traffic laws to maximize long-term rewards.

---

## Problem Statement

### The Real-World Context
- **Country**: Tanzania, Dar es Salaam
- **Problem**: Overloaded public transport (daladalas) causes 40% of fatal road accidents
- **Root Cause**: Drivers earn only ~TSh 22,000/day operating legally → forced to overload + accept bribes
- **Challenge**: How can RL teach agents to maximize profit while minimizing crashes and fines?

### Why RL?
Traditional rule-based systems fail because they don't account for:
- Trade-offs between risk (overloading) and reward (more passengers = more income)
- Dynamic decision-making under uncertainty (will I get caught at this police checkpoint?)
- Exploration vs. exploitation (when to take bribes vs. stay safe?)

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
| **Police Checkpoints** | (6,14), (11,14), (14,10) | Enforce legal capacity |
| **Traffic Lights** | (3,14), (10,14), (14,12), (14,5) | Cyclic red/green (40 steps) |

---

## Action Space (8 Discrete Actions)

| Action | Code | Effect |
|--------|------|--------|
| **Move Forward** | 0 | Advance 1 cell (progress = +0.6 reward) |
| **Stop** | 1 | Hold position (safe at police/lights) |
| **Pick Up Passengers** | 2 | At high-demand stop: +4–8 passengers |
| **Drop Off Passengers** | 3 | At high-demand stop: −6–15 passengers |
| **Hard Accelerate** | 4 | Speed = 3 (RISKY if overloaded) |
| **Hard Brake** | 5 | Speed = 0 (RISKY if overloaded) |
| **Accept Bribe** | 6 | At high-demand stop: +15 cash, +2–5 passengers |
| **Reject Bribe** | 7 | At high-demand stop: +30 honesty bonus |

---

## Observation Space (15 Features, Normalized to [-1, 1])

| Index | Feature | Range | Purpose |
|-------|---------|-------|---------|
| 0 | pos_x | [0, 14] | X coordinate |
| 1 | pos_y | [0, 14] | Y coordinate |
| 2 | current_passengers | [0, 50] | Occupancy level |
| 3 | money_earned | [0, 150000] | TSh earned |
| 4 | current_speed | [0, 3] | Movement speed |
| 5 | distance_to_next_light | Lookahead | Traffic light proximity |
| 6 | distance_to_next_police | Lookahead | Police checkpoint proximity |
| 7 | light_is_red | {0, 1} | Red light now? |
| 8 | police_next_cell | {0, 1} | Police ahead? |
| 9 | **must_stop_next** | {0, 1} | **CRITICAL FLAG** (police OR red light) |
| 10 | at_high_demand_stop | {0, 1} | At pickup/dropoff? |
| 11 | bribe_offered_now | {0, 1} | Bribe available? |
| 12 | passengers_waiting | [0, 10] | Demand at current stop |
| 13 | has_been_fined | {0, 1} | Already fined this episode? |
| 14 | episode_steps | [0, 350] | Step count / max_steps |

---

## Reward Structure

### Progress & Delivery
- **+0.6**: Per step forward (encourage efficiency)
- **+1.2×passengers**: Per passenger dropped off
- **+100**: Reaching final destination (Posta)
- **+200**: Perfect legal trip bonus (≤33 passengers at Posta)

### Safety & Compliance
- **+6**: Voluntarily stopping at police/red light (`must_stop_next=1` AND action=1)
- **-45**: Ignoring police/red light (action≠1 when `must_stop_next=1`)
- **+30**: Rejecting a bribe
- **+15**: Accepting a bribe

### Penalties
- **-40**: Light fine (34–40 passengers at police checkpoint)
- **-200**: Heavy fine + episode ends (>40 passengers at police)
- **-400**: Accident + episode ends (overloaded + hard acceleration/braking OR ran red light with >40 pax)
- **-50**: Truncation penalty (350 steps without reaching Posta)

---

## Terminal Conditions

**Success**:
- Reach Posta (final cell) with ≥30 passengers

**Failure**:
- Caught with >40 passengers at police checkpoint
- Accident (overloaded + hard acceleration/braking)

**Truncation**:
- 350 steps elapsed without success/failure

---

## RL Algorithms Implemented

### 1. **DQN** (Value-Based)
- **Architecture**: MLP policy (15 → 128 → 64 → 8)
- **Training**: 300,000 timesteps
- **Hyperparameters Tuned**: 12 configurations
  - Learning rates: 1e-4, 3e-4, 5e-4, 7e-4, 1e-3
  - Buffer sizes: 50k, 75k, 100k
  - Exploration fractions: 0.1, 0.15, 0.2

### 2. **PPO** (Policy Gradient)
- **Architecture**: MLP policy (15 → 128 → 64 → 8)
- **Training**: 300,000 timesteps
- **Hyperparameters Tuned**: 12 configurations
  - Learning rates: 1e-4, 3e-4, 5e-4, 7e-4, 1e-3
  - Entropy coefficients: 0.0, 0.005, 0.01
  - n_steps: 2048, 4096

### 3. **A2C** (Actor-Critic)
- **Architecture**: MLP policy (15 → 128 → 64 → 8)
- **Training**: 300,000 timesteps
- **Hyperparameters Tuned**: 12 configurations
  - Learning rates: 1e-4, 3e-4, 5e-4, 7e-4, 1e-3
  - Gamma values: 0.99, 0.995
  - n_steps: 5, 8, 10
  - Entropy coefficients: 0.0, 0.005, 0.01, 0.05

### 4. **REINFORCE** (Policy Gradient)
- **Architecture**: Neural network policy (15 → hidden → hidden → 8)
- **Training**: 3,000 episodes (~300,000 steps)
- **Hyperparameters Tuned**: 12 configurations
  - Learning rates: 1e-4, 3e-4, 5e-4, 7e-4, 1e-3
  - Hidden sizes: 128, 256
  - Gamma values: 0.99, 0.995

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
│   └── reinforce/best_reinforce.pth  # Best REINFORCE model
├── results/
│   ├── dqn_results.json
│   ├── ppo_results.json
│   ├── a2c_results.json
│   ├── reinforce_results.json
│   └── comparison_results.json
├── main.py                       # Run best model (interactive)
├── random_demo.py                # Generate demo GIF
├── comparison_eval.py             # Compare all 4 models
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
python random_demo.py
# Generates: random_demo.gif
```

### Compare All 4 Trained Models
```bash
python comparison_eval.py
# Outputs: comparison table + detailed metrics
# Saves: results/comparison_results.json
```

### Run Best Model (Interactive Play)
```bash
python main.py
# Shows GUI + terminal output of best-performing agent
```

---

## Key Findings

### Expected Agent Behavior
After training, agents should discover:
1. **Safe operation**: Run at 34–38 passengers (just overloaded enough for profit, but survivable)
2. **Bribe rejection**: Accept ~25% of bribes (high-risk, avoid most)
3. **Traffic compliance**: Always stop at police/red lights (mandatory to avoid -45 penalty)
4. **Optimal route**: Maximize passenger pickups at high-demand stops, minimize truncation

### Why This Works
- **Legal operation** (≤33 pax): Mean reward ≈ +100 + (passengers × 1.2) = +100 to +150
- **Safe overloading** (34–40 pax): +15–50 from bribes, but -40 fines, net ≈ +50–100
- **Reckless overloading** (>40 pax): -200 heavy fine OR -400 crash = CATASTROPHE
- **Traffic violation**: -45 penalty per violation, accumulates quickly

**Equilibrium**: 34–38 passengers, reject bribes, obey traffic → highest long-term expected reward.

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

## Evaluation Metrics

All models evaluated on **100 test episodes** with deterministic (greedy) action selection:

| Metric | Description |
|--------|-------------|
| **Mean Reward** | Average cumulative reward per episode |
| **Std Dev** | Reward variance (stability indicator) |
| **Legal Compliance %** | Episodes ending with ≤33 passengers |
| **Crash Rate %** | Episodes terminated early due to overloading accidents |
| **Fine Rate %** | Episodes where agent was fined |
| **Avg Passengers** | Average passenger count at episode end |

---

## Results Summary

See `results/comparison_results.json` for detailed metrics.

**Expected Ranking** (not guaranteed):
1. PPO (most stable, best exploration-exploitation)
2. A2C (good sample efficiency)
3. DQN (sample efficient but slower convergence)
4. REINFORCE (high variance, slower learning)

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
python random_demo.py

# 4. Compare all trained models
python comparison_eval.py

# 5. Run best model with visualization
python main.py
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
- Bribe offers (corruption dilemma)
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
