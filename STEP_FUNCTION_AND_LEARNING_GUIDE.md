# STEP_FUNCTION_AND_LEARNING_GUIDE.md

# Step Function, Reward System & Model Learning

## 1. THE STEP FUNCTION (What Happens Each Step)

### Structure
```python
def step(self, action):
    # Input: action (0-7) from agent
    # Output: observation, reward, terminated, truncated, info
    
    # A. Execute action
    # B. Calculate reward
    # C. Check termination
    # D. Render (optional)
    # E. Return new state
```

### Timeline of a Single Step

```
┌─────────────────────────────────────────────────┐
│ STEP 0: Agent is at (0,14) with 0 passengers   │
└─────────────────────────────────────────────────┘
         ↓
    Agent observes state:
    obs = [−1, −1, −1, −1, ...]  (15 features)
         ↓
┌─────────────────────────────────────────────────┐
│ Agent chooses ACTION 2 (Pick up passengers)     │
└─────────────────────────────────────────────────┘
         ↓
    Environment EXECUTES action:
    - Add 4-8 random passengers
    - Agent now has ~6 passengers
    - Agent still at (0,14)
         ↓
┌─────────────────────────────────────────────────┐
│ REWARD CALCULATION                              │
│ ─────────────────────────────────────────────── │
│ Base reward:           +0.6  (progress)         │
│ Pickup reward:         +1.2×6 = +7.2           │
│ Total reward:          +7.8                     │
└─────────────────────────────────────────────────┘
         ↓
    Check termination:
    - Is episode finished? (reached Posta or crashed)
    - Has 350 steps elapsed?
    - triggered = False, truncated = False
         ↓
┌─────────────────────────────────────────────────┐
│ STEP 1: New observation returned to agent       │
│ obs = [−1, −1, −0.76, −1, ...]  (state changed)│
│ reward = +7.8                                   │
│ terminated = False                              │
│ truncated = False                               │
└─────────────────────────────────────────────────┘
```

---

## 2. THE REWARD SYSTEM (How Agent Gets Feedback)

### Reward Table (Complete)

#### Progress & Delivery
| Event | Reward | Why |
|-------|--------|-----|
| Each step forward | +0.6 | Encourage efficiency (reach destination faster) |
| Each passenger dropped | +1.2 × passengers | Proportional to passengers delivered |
| Reach Posta (destination) | +100 | Success bonus |
| Perfect legal trip (≤33 pax at Posta) | +200 | Bonus for obeying law |

#### Safety & Compliance  
| Event | Reward | Why |
|-------|--------|-----|
| Stop voluntarily at police/red light | +6 | Reward safe behavior |
| Ignore police/red light (action≠1) | -45 | Penalize recklessness |
| Reject bribe | +30 | Reward honesty |
| Accept bribe | +15 | Allow some flexibility |

#### Penalties (Safety & Law)
| Event | Reward | Why |
|-------|--------|-----|
| Light overload (34-40 pax at police) | -40 | Discourage overloading |
| Heavy overload (>40 pax at police) | -200 + TERMINATED | Severe penalty |
| Accident (overloaded + reckless) | -400 + TERMINATED | Worst case |
| Truncation (350 steps, no success) | -50 | Discourage inefficiency |

### Real Example: 3-Step Episode

```
STEP 0 (Initial):
─────────────────
Position: (0,14), Passengers: 0
Observation: [−1, −1, −1, −1, ...]
Action: 0 (Move forward)
Reward: +0.6 (progress)
Position: (1,14), Passengers: 0
Cumulative: +0.6

STEP 1:
─────────────────
Position: (1,14), Passengers: 0
At high-demand stop? YES (4,14) is coming
Action: 2 (Pick up passengers)
Passengers: +6 added
Reward: +0.6 (progress) + 1.2×6 (pickup) = +7.8
Cumulative: +0.6 + 7.8 = +8.4

STEP 2:
─────────────────
Position: (1,14), Passengers: 6
Approaching police checkpoint at (6,14)
Action: 0 (Move forward)
Position: (2,14), Passengers: 6
Reward: +0.6 (progress)
Cumulative: +8.4 + 0.6 = +9.0
```

---

## 3. HOW THE MODEL LEARNS

### The Learning Loop

```
┌─────────────────────────────────────────────────────┐
│ EPISODE 1                                           │
├─────────────────────────────────────────────────────┤
│ Agent takes random actions                          │
│ Accumulates experience: (obs, action, reward)       │
│ Episode ends with total reward = 50                 │
└─────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│ LEARNING (Update Policy/Value Function)             │
├─────────────────────────────────────────────────────┤
│ Algorithm analyzes: "What actions led to reward?"   │
│ Updates weights: Increase prob of good actions      │
│ Decrease prob of bad actions                        │
└─────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│ EPISODE 2                                           │
├─────────────────────────────────────────────────────┤
│ Agent uses updated policy (slightly smarter)        │
│ Accumulates experience                              │
│ Episode ends with total reward = 75 (improved!)     │
└─────────────────────────────────────────────────────┘
         ↓
         (Repeat 300,000 times...)
         ↓
┌─────────────────────────────────────────────────────┐
│ EPISODE 150,000                                     │
├─────────────────────────────────────────────────────┤
│ Agent has learned good strategy!                    │
│ Accumulates experience                              │
│ Episode ends with total reward = 250 (expert!)      │
└─────────────────────────────────────────────────────┘
```

### What Each Algorithm Learns

#### **DQN (Value-Based)**
Learns: "What is the VALUE of each state-action pair?"

```
Q(state, action) = Expected future reward if I take this action

Example learning:
State: (pos=5, passengers=10, police_ahead=True)

Q(state, action=0) = Low value  (moving forward is risky)
Q(state, action=1) = High value (stopping is safe)
Q(state, action=6) = Medium value (accepting bribe is risky)

Agent chooses action with highest Q value
```

#### **PPO (Policy Gradient)**
Learns: "What is the PROBABILITY of each action being good?"

```
Policy π(action|state) = Probability of taking this action

Example learning:
State: (pos=5, passengers=10, police_ahead=True)

π(action=0) = 0.2  (20% chance move forward)
π(action=1) = 0.7  (70% chance stop)
π(action=6) = 0.1  (10% chance accept bribe)

Agent samples from distribution (usually picks action=1, sometimes explores)
```

#### **A2C (Actor-Critic)**
Learns: BOTH value (Critic) + probability (Actor)

```
Critic: "Is this state good?" (Value function)
Actor: "What should I do here?" (Policy)

Example:
State: (pos=5, passengers=10, police_ahead=True)

Critic says: V(state) = 50 (moderate value state)
Actor says: π(action=1) = 0.8 (stop is best)

Agent: "This state is okay, and stopping is the right move"
```

#### **REINFORCE (Pure Policy Gradient)**
Learns: "Maximize total episode reward by adjusting policy"

```
At end of episode: Reward = 150
Backward pass: "Which actions contributed to this reward?"

Actions that led to high reward:
- Stop at police → weight UP
- Pick up passengers → weight UP
- Move forward at yellow light → weight DOWN

Policy updated to repeat good actions
```

---

## 4. TRAINING CONVERGENCE

### What "Learning" Looks Like

```
Episode Rewards Over Time:

Reward
  │
  │                                      ╱╱╱╱╱
300│                              ╱╱╱╱╱╱
  │                        ╱╱╱╱╱╱
250│                  ╱╱╱╱╱
  │            ╱╱╱╱╱
200│      ╱╱╱╱╱
  │  ╱╱╱╱╱
150│╱╱╱╱╱ (Convergence)
  │
100│
  │
 50│ (Random exploration)
  │
  0└─────────────────────────────────────
    0      50,000   100,000   150,000   300,000
              Training Steps

Agent gradually improves!
```

### Why Does This Happen?

**Early training (random actions)**:
- Agent tries everything
- Accumulates data on what works
- Rewards are mixed

**Middle training (learning)**:
- Patterns emerge
- Agent starts taking better actions
- Rewards increase

**Late training (convergence)**:
- Agent has learned optimal policy
- Repeats successful strategies
- Rewards plateau at high level

---

## 5. CONCRETE EXAMPLE: Agent Learning

### Episode 1 (Random)
```
Step 0: At (0,14), pax=0
  Action: 1 (Stop)  ← Random choice
  Reward: +0.6
  Observation: [−1, −1, −1, ...]

Step 1: At (0,14), pax=0
  Action: 4 (Hard accelerate)  ← Random choice
  Reward: +0.6
  Observation: [−1, −1, −1, ...]

Step 2: At (1,14), pax=0
  Action: 7 (Reject bribe)  ← Random, but no bribe offered
  Reward: +0 (no effect)
  Observation: [−1, −1, −1, ...]

... (continuing randomly)

Total Episode Reward: 45 (mediocre)
```

### Episode 100 (Slight Learning)
```
Step 0: At (0,14), pax=0
  Action: 0 (Move forward)  ← Agent learned this is good
  Reward: +0.6
  Observation: [−0.86, −1, −1, ...]

Step 1: At (1,14), pax=0
  Action: 0 (Move forward)  ← Continue
  Reward: +0.6
  Observation: [−0.72, −1, −1, ...]

Step 2: At (2,14), pax=0
  Action: 0 (Move forward)
  Reward: +0.6
  Observation: [−0.58, −1, −1, ...]

Step 3: At (3,14), pax=0
  Action: 0 (Move forward) → Wait, traffic light ahead!
  Reward: −45 (violated red light!)
  OBSERVATION: Agent learns "moving on red light = BAD"
  Observation: [−0.44, −1, −1, ...]

Step 4: At (3,14), pax=0
  Action: 1 (Stop)
  Reward: +6 (correct! Stopped at red light)
  Observation: [−0.44, −1, −1, ...]

Step 5: At (4,14), pax=0  ← HIGH-DEMAND STOP
  Action: 2 (Pick up)
  Passengers: +6
  Reward: +0.6 + 1.2×6 = +7.8
  Observation: [−0.44, −1, −0.76, ...]

... (continues with better strategy)

Total Episode Reward: 120 (improving!)
```

### Episode 1000 (Converged)
```
Step 0: At (0,14), pax=0
  Action: 0 (Move forward)
  Reward: +0.6
  (continues moving...)

Step 4: At (4,14) ← HIGH-DEMAND STOP
  Action: 2 (Pick up passengers)
  Passengers: +6
  Reward: +7.8

Step 6: At (6,14) ← POLICE CHECKPOINT
  Must_stop_next: True (sees police ahead)
  Action: 1 (Stop voluntarily)
  Reward: +6 (safe behavior!)

Step 7: At (6,14) ← AT POLICE
  Passengers: 6 (legal, ≤33)
  Action: 0 (Continue)
  Reward: +0.6 (no fine)

... (continues optimally)

Step 28: At (14,0) ← DESTINATION (Posta)
  Passengers: 22 (successfully delivered)
  Action: 0 (Move forward/reached)
  Reward: +100 (destination) + 0 (not ≤33, so no +200)
  TERMINATED: True

Total Episode Reward: 280 (excellent!)
```

---

## 6. KEY INSIGHTS

### What the Model Actually Learns

Through repeated episodes, the agent discovers:

1. **Route knowledge**
   - "High-demand stops at (4,14), (8,14), (14,8), (14,3)"
   - "Police checkpoints at (6,14), (11,14), (14,10)"
   - "Traffic lights at (3,14), (10,14), (14,12), (14,5)"

2. **Risk-reward trade-off**
   - "Picking up passengers = +reward, but overload risk"
   - "Speeding = risky when overloaded"
   - "Bribes = risky, usually reject"

3. **Optimal strategy**
   - "Operate at 34-38 passengers (profitable + survivable)"
   - "Always stop at police (reward outweighs risk)"
   - "Reject ~75% of bribes"
   - "Move forward on green, stop on red"

4. **Efficiency**
   - "Deliver passengers at appropriate stops"
   - "Don't waste time idling"
   - "Reach destination within 350 steps"

### Success Criteria

Agent has learned well when:
- ✓ Mean reward > 200
- ✓ Legal compliance > 50% (≤33 passengers at end)
- ✓ Crash rate < 10%
- ✓ Reaches destination reliably

---

## 7. COMPARISON: 4 ALGORITHMS

| Algorithm | What It Learns | Speed | Stability |
|-----------|-----------------|-------|-----------|
| **DQN** | State-action values | Slow-Medium | Medium |
| **PPO** | Action probabilities | Fast | High |
| **A2C** | Values + probabilities | Medium | High |
| **REINFORCE** | Episode rewards | Slow | Low |

---

## Summary

```
FLOW:
Agent Observes → Chooses Action → Gets Reward → Learns → Better Next Time

REWARD:
Profit-driven (passengers, delivery)
- Safety-constrained (traffic laws, capacity)
- Corruption-tested (bribes)

LEARNING:
Happens automatically through 300,000 timesteps
Each algorithm explores differently
Convergence = agent has discovered optimal strategy

RESULT:
Agent learns to balance safety + profit ✓
```

You now have a complete picture of step → reward → learning! 🎯
