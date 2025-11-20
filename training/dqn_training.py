# training/dqn_training.py
from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy
from environment import DaladalaEnv
import numpy as np
import json
import os

# Create results directory
os.makedirs("results", exist_ok=True)

best_reward = -np.inf
all_results = []

# Comprehensive hyperparameter grid (12 configurations)
hyperparams = [
    {"lr": 1e-4, "buffer_size": 50000, "exp_frac": 0.1, "exp_init": 1.0, "exp_final": 0.05},
    {"lr": 1e-4, "buffer_size": 100000, "exp_frac": 0.15, "exp_init": 1.0, "exp_final": 0.05},
    {"lr": 3e-4, "buffer_size": 50000, "exp_frac": 0.1, "exp_init": 1.0, "exp_final": 0.05},
    {"lr": 3e-4, "buffer_size": 100000, "exp_frac": 0.2, "exp_init": 0.95, "exp_final": 0.01},
    {"lr": 5e-4, "buffer_size": 75000, "exp_frac": 0.15, "exp_init": 1.0, "exp_final": 0.05},
    {"lr": 7e-4, "buffer_size": 50000, "exp_frac": 0.2, "exp_init": 1.0, "exp_final": 0.02},
    {"lr": 7e-4, "buffer_size": 100000, "exp_frac": 0.1, "exp_init": 0.95, "exp_final": 0.05},
    {"lr": 1e-3, "buffer_size": 75000, "exp_frac": 0.15, "exp_init": 1.0, "exp_final": 0.03},
    {"lr": 1e-3, "buffer_size": 100000, "exp_frac": 0.2, "exp_init": 1.0, "exp_final": 0.05},
    {"lr": 5e-4, "buffer_size": 100000, "exp_frac": 0.1, "exp_init": 0.9, "exp_final": 0.02},
    {"lr": 3e-4, "buffer_size": 75000, "exp_frac": 0.15, "exp_init": 1.0, "exp_final": 0.04},
    {"lr": 7e-4, "buffer_size": 75000, "exp_frac": 0.2, "exp_init": 0.95, "exp_final": 0.03},
]

for idx, params in enumerate(hyperparams):
    print(f"\n{'='*70}")
    print(f"DQN Configuration {idx+1}/12")
    print(f"lr={params['lr']}, buffer={params['buffer_size']}, exp_frac={params['exp_frac']}")
    print(f"{'='*70}")
    
    env = DaladalaEnv()
    model = DQN(
        "MlpPolicy", env,
        learning_rate=params['lr'],
        buffer_size=params['buffer_size'],
        exploration_fraction=params['exp_frac'],
        exploration_initial_eps=params['exp_init'],
        exploration_final_eps=params['exp_final'],
        train_freq=4,
        gradient_steps=1,
        target_update_interval=1000,
        verbose=0,
        seed=42
    )
    model.learn(total_timesteps=300000)

    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=50)
    print(f"Mean Reward: {mean_reward:.2f} ± {std_reward:.2f}")

    result = {
        "config": idx + 1,
        "hyperparams": params,
        "mean_reward": float(mean_reward),
        "std_reward": float(std_reward),
        "total_timesteps": 300000,
        "eval_episodes": 50
    }
    all_results.append(result)

    if mean_reward > best_reward:
        best_reward = mean_reward
        model.save("models/dqn/best_dqn")
        print("✓ NEW BEST DQN MODEL SAVED!")

    env.close()

# Save results
with open("results/dqn_results.json", "w") as f:
    json.dump(all_results, f, indent=2)

print(f"\n{'='*70}")
print(f"DQN Training Complete!")
print(f"Best Mean Reward: {best_reward:.2f}")
print(f"Results saved to results/dqn_results.json")
print(f"{'='*70}")