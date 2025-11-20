# training/ppo_training.py
from stable_baselines3 import PPO
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
    {"lr": 1e-4, "ent_coef": 0.0, "n_steps": 2048, "batch_size": 64},
    {"lr": 1e-4, "ent_coef": 0.01, "n_steps": 2048, "batch_size": 128},
    {"lr": 3e-4, "ent_coef": 0.0, "n_steps": 2048, "batch_size": 64},
    {"lr": 3e-4, "ent_coef": 0.01, "n_steps": 4096, "batch_size": 128},
    {"lr": 5e-4, "ent_coef": 0.005, "n_steps": 2048, "batch_size": 64},
    {"lr": 5e-4, "ent_coef": 0.01, "n_steps": 4096, "batch_size": 64},
    {"lr": 7e-4, "ent_coef": 0.0, "n_steps": 4096, "batch_size": 128},
    {"lr": 7e-4, "ent_coef": 0.01, "n_steps": 2048, "batch_size": 64},
    {"lr": 1e-3, "ent_coef": 0.005, "n_steps": 2048, "batch_size": 128},
    {"lr": 1e-3, "ent_coef": 0.01, "n_steps": 4096, "batch_size": 128},
    {"lr": 3e-4, "ent_coef": 0.005, "n_steps": 4096, "batch_size": 64},
    {"lr": 5e-4, "ent_coef": 0.0, "n_steps": 2048, "batch_size": 128},
]

for idx, params in enumerate(hyperparams):
    print(f"\n{'='*70}")
    print(f"PPO Configuration {idx+1}/12")
    print(f"lr={params['lr']}, ent_coef={params['ent_coef']}, n_steps={params['n_steps']}")
    print(f"{'='*70}")
    
    env = DaladalaEnv()
    model = PPO(
        "MlpPolicy", env,
        learning_rate=params['lr'],
        ent_coef=params['ent_coef'],
        n_steps=params['n_steps'],
        batch_size=params['batch_size'],
        n_epochs=10,
        gae_lambda=0.95,
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
        model.save("models/ppo/best_ppo")
        print("✓ NEW BEST PPO MODEL SAVED!")

    env.close()

# Save results
with open("results/ppo_results.json", "w") as f:
    json.dump(all_results, f, indent=2)

print(f"\n{'='*70}")
print(f"PPO Training Complete!")
print(f"Best Mean Reward: {best_reward:.2f}")
print(f"Results saved to results/ppo_results.json")
print(f"{'='*70}")