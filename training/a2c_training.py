# training/a2c_training.py
from stable_baselines3 import A2C
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
    {"lr": 1e-4, "n_steps": 5, "gamma": 0.99, "gae_lambda": 1.0, "ent_coef": 0.0},
    {"lr": 1e-4, "n_steps": 8, "gamma": 0.99, "gae_lambda": 0.95, "ent_coef": 0.01},
    {"lr": 3e-4, "n_steps": 5, "gamma": 0.99, "gae_lambda": 1.0, "ent_coef": 0.0},
    {"lr": 3e-4, "n_steps": 8, "gamma": 0.995, "gae_lambda": 0.95, "ent_coef": 0.01},
    {"lr": 5e-4, "n_steps": 5, "gamma": 0.99, "gae_lambda": 0.95, "ent_coef": 0.005},
    {"lr": 5e-4, "n_steps": 10, "gamma": 0.995, "gae_lambda": 1.0, "ent_coef": 0.01},
    {"lr": 7e-4, "n_steps": 8, "gamma": 0.99, "gae_lambda": 0.95, "ent_coef": 0.0},
    {"lr": 7e-4, "n_steps": 5, "gamma": 0.995, "gae_lambda": 1.0, "ent_coef": 0.05},
    {"lr": 1e-3, "n_steps": 5, "gamma": 0.99, "gae_lambda": 1.0, "ent_coef": 0.01},
    {"lr": 1e-3, "n_steps": 10, "gamma": 0.995, "gae_lambda": 0.95, "ent_coef": 0.0},
    {"lr": 3e-4, "n_steps": 10, "gamma": 0.99, "gae_lambda": 0.95, "ent_coef": 0.005},
    {"lr": 5e-4, "n_steps": 8, "gamma": 0.99, "gae_lambda": 1.0, "ent_coef": 0.01},
]

for idx, params in enumerate(hyperparams):
    print(f"\n{'='*70}")
    print(f"A2C Configuration {idx+1}/12")
    print(f"lr={params['lr']}, n_steps={params['n_steps']}, gamma={params['gamma']}")
    print(f"{'='*70}")
    
    env = DaladalaEnv()
    model = A2C(
        "MlpPolicy", env,
        learning_rate=params['lr'],
        n_steps=params['n_steps'],
        gamma=params['gamma'],
        gae_lambda=params['gae_lambda'],
        ent_coef=params['ent_coef'],
        vf_coef=0.5,
        max_grad_norm=0.5,
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
        model.save("models/a2c/best_a2c")
        print("✓ NEW BEST A2C MODEL SAVED!")

    env.close()

# Save results
with open("results/a2c_results.json", "w") as f:
    json.dump(all_results, f, indent=2)

print(f"\n{'='*70}")
print(f"A2C Training Complete!")
print(f"Best Mean Reward: {best_reward:.2f}")
print(f"Results saved to results/a2c_results.json")
print(f"{'='*70}")