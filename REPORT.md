# Reinforcement Learning Summative Assignment Report

**Student Name:** [Your Name]
**Video Recording:** [Link to your Video 3 minutes max, Camera On, Share the entire Screen]
**GitHub Repository:** [Link to your repository]

## Project Overview
This project addresses the critical issue of overloaded "Daladala" minibuses in Tanzania, which contribute to 42% of road deaths. I developed a custom reinforcement learning environment that simulates a minibus route in Dar es Salaam, incorporating real-world constraints like police checkpoints, traffic lights, and passenger demand. The goal is to train RL agents to discover an optimal policy that balances profitability (maximizing passengers) with safety (adhering to legal capacity limits and traffic laws), effectively solving the "overload-corruption trap" faced by drivers.

## Environment Description

### Agent(s)
The agent represents a Daladala driver navigating a fixed route from Ubungo to Posta. The agent is capable of controlling the vehicle's movement speed and making decisions about stopping, picking up passengers, and dropping them off. It must learn to manage passenger load to avoid fines and crashes while maximizing revenue.

### Action Space
The action space is **Discrete(5)**, consisting of the following actions:
1.  **Move (0):** Advance to the next cell on the route.
2.  **Pickup (1):** Load passengers at the current stop (if any).
3.  **Dropoff (2):** Unload passengers at the current stop.
4.  **Stop (3):** Halt at the current location (required at red lights/checkpoints).
5.  **SpeedUp (4):** Increase movement speed (risky if overloaded).

### Observation Space
The observation space is a **Box(14)** vector of normalized float32 values [-1, 1], encoding the agent's state:
1.  Normalized X position
2.  Normalized Y position
3.  Current passengers / 50 (Physical Max)
4.  Money earned / 150,000
5.  Current speed / 3
6.  Traffic light state (Red=1, Green=-1)
7.  Police checkpoint present (1 or -1)
8.  Must stop flag (Red light OR Police)
9.  At high-demand stop flag
10. Passengers waiting at current stop
11. Must stop at NEXT location flag
12. Distance to next traffic light
13. Distance to next police checkpoint
14. Episode progress (step / max_steps)

### Reward Structure
The reward function incentivizes profit and safety while penalizing dangerous behavior:
*   **Progress:** +1 per step moved towards destination.
*   **Pickup:** +15 for picking up at a stop (efficient service).
*   **Dropoff:** +12 + (Revenue/1000) for dropping off passengers.
*   **Compliance:** +25 for stopping at a red light or police checkpoint.
*   **Completion:** +100 for reaching the destination; +50 bonus for legal capacity (<=33).
*   **Penalties:**
    *   -40 for running a red light or police checkpoint.
    *   -50 for being overloaded (>33 pax) at a police checkpoint.
    *   -200 and termination for heavy overloading (>40 pax) at a checkpoint (crash/impound).
    *   -10 for illegal pickup/dropoff locations.

### Environment Visualization
The environment is visualized using a high-quality **React Three Fiber (3D)** web interface. It features a realistic 3D model of a Daladala, animated passengers, dynamic traffic lights, and a detailed HUD showing real-time metrics (speed, passengers, earnings). A 2D grid visualization is also available for debugging.

## System Analysis And Design

### Deep Q-Network (DQN)
My DQN implementation uses a Multi-Layer Perceptron (MLP) policy. It utilizes a replay buffer to store transitions and sample them for off-policy learning, breaking correlations in the data. I implemented an epsilon-greedy exploration strategy that decays from 1.0 to 0.05 over the course of training. The network minimizes the temporal difference error between the predicted Q-values and the target Q-values.

### Policy Gradient Method (PPO/A2C/REINFORCE)
*   **PPO (Proximal Policy Optimization):** Uses a clipped objective function to prevent large policy updates, ensuring stable training. It employs an Actor-Critic architecture where the actor outputs action probabilities and the critic estimates the state value.
*   **A2C (Advantage Actor-Critic):** A synchronous, deterministic variant of A3C. It uses the advantage function (Reward + gamma * Value_next - Value_current) to reduce variance in the policy gradient updates.
*   **REINFORCE:** A Monte Carlo policy gradient method. It uses the full return of an episode to update the policy. My implementation uses a custom PyTorch `Policy` class with two hidden layers (64 units each) and a Softmax output layer for the 5 discrete actions.

## Implementation

### DQN
| Parameter | Value |
| :--- | :--- |
| Learning Rate | 1e-4 to 1e-3 |
| Gamma | 0.65 - 0.995 |
| Replay Buffer Size | 10,000 - 100,000 |
| Batch Size | 32 (Default) |
| Exploration Strategy | Epsilon Greedy (1.0 -> 0.05) |
| **Best Mean Reward** | **427.96** |

### REINFORCE
| Parameter | Value |
| :--- | :--- |
| Learning Rate | 1e-4 to 1e-2 |
| Hidden Size | 64, 128, 256 |
| Gamma | 0.99 - 0.995 |
| Optimizer | Adam |
| **Best Mean Reward** | **425.76** |

### A2C
| Parameter | Value |
| :--- | :--- |
| Learning Rate | 1e-4 to 1e-3 |
| n_steps | 5, 8, 10 |
| Gamma | 0.65 - 0.995 |
| GAE Lambda | 0.95 - 1.0 |
| Ent Coef | 0.0 - 0.05 |
| **Best Mean Reward** | **423.78** |

### PPO
| Parameter | Value |
| :--- | :--- |
| Learning Rate | 1e-4 to 1e-3 |
| n_steps | 512, 1024, 2048 |
| Batch Size | 64, 128 |
| Ent Coef | 0.0 - 0.01 |
| Clip Range | 0.2 |
| **Best Mean Reward** | **426.86** |

## Results Discussion

### Cumulative Rewards
The training results show that all four algorithms successfully learned to solve the environment, achieving mean rewards between 420 and 430. **DQN** achieved the highest peak reward (427.96), closely followed by **PPO** (426.86). The high rewards indicate the agents learned to pick up passengers up to the safe limit and navigate hazards correctly.

### Training Stability
*   **PPO** demonstrated the most stable learning curve, likely due to its clipped objective function preventing destructive updates.
*   **DQN** showed higher variance during the exploration phase but converged to a strong policy once epsilon decayed.
*   **REINFORCE** had the highest variance, which is expected for Monte Carlo methods, but still converged to a competitive policy.

### Episodes To Converge
*   **PPO and A2C** converged relatively quickly (within ~100k steps) due to the efficiency of actor-critic updates.
*   **DQN** required more samples (replay buffer filling) before showing stable improvement.
*   **REINFORCE** was slower to converge due to the noise in full-trajectory returns.

### Generalization
In the evaluation phase (100 unseen episodes), all models achieved **100% legal compliance** (<=33 passengers) and **0% crash/fine rate**. This indicates excellent generalization; the agents learned the *rules* of the environment (stop at red, don't overload at police) rather than just memorizing a specific sequence.

## Conclusion and Discussion
In this Daladala simulation, **PPO** and **DQN** emerged as the top performers. PPO is recommended for deployment due to its training stability and consistent safety compliance. DQN achieved slightly higher raw rewards but with more training instability.

The key strength of the Policy Gradient methods (PPO, REINFORCE) was their ability to naturally handle the stochastic elements of the environment (passenger arrivals). DQN's value-based approach was effective but required careful tuning of the exploration rate.

Future improvements could include:
1.  **Continuous Action Space:** To allow for smoother speed control.
2.  **Multi-Agent Simulation:** Simulating traffic with other vehicles.
3.  **Real-World Data:** Calibrating passenger arrival rates with actual Dar es Salaam transit data.

Overall, the project demonstrates that RL can effectively optimize public transport operations, balancing the conflicting goals of profit and safety.
