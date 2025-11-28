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

# Hyperparameter (12 configurations)
hyperparams = [
    {"name": "LR_1e4_n_steps_512", "learning_rate": 1e-4, "n_steps": 512, "batch_size": 64, "gamma": 0.65, "clip_range": 0.2, "ent_coef": 0.0},
    {"name": "LR_1e4_n_steps_1024", "learning_rate": 1e-4, "n_steps": 1024, "batch_size": 64, "gamma": 0.70, "clip_range": 0.2, "ent_coef": 0.0},
    {"name": "LR_3e4_n_steps_512", "learning_rate": 3e-4, "n_steps": 512, "batch_size": 128, "gamma": 0.75, "clip_range": 0.2, "ent_coef": 0.005},
    {"name": "LR_3e4_n_steps_1024", "learning_rate": 3e-4, "n_steps": 1024, "batch_size": 128, "gamma": 0.77, "clip_range": 0.2, "ent_coef": 0.005},
    {"name": "LR_5e4_n_steps_512", "learning_rate": 5e-4, "n_steps": 512, "batch_size": 128, "gamma": 0.80, "clip_range": 0.2, "ent_coef": 0.01},
    {"name": "LR_5e4_n_steps_1024", "learning_rate": 5e-4, "n_steps": 1024, "batch_size": 64, "gamma": 0.85, "clip_range": 0.2, "ent_coef": 0.01},
    {"name": "LR_7e4_n_steps_512", "learning_rate": 7e-4, "n_steps": 512, "batch_size": 64, "gamma": 0.90, "clip_range": 0.25, "ent_coef": 0.0},
    {"name": "LR_7e4_n_steps_1024", "learning_rate": 7e-4, "n_steps": 1024, "batch_size": 128, "gamma": 0.95, "clip_range": 0.25, "ent_coef": 0.005},
    {"name": "LR_1e3_n_steps_512", "learning_rate": 1e-3, "n_steps": 512, "batch_size": 64, "gamma": 0.995, "clip_range": 0.2, "ent_coef": 0.01},
    {"name": "LR_1e3_n_steps_1024", "learning_rate": 1e-3, "n_steps": 1024, "batch_size": 128, "gamma": 0.67, "clip_range": 0.2, "ent_coef": 0.01},
    {"name": "LR_1e3_n_steps_2048", "learning_rate": 1e-3, "n_steps": 2048, "batch_size": 128, "gamma": 0.77, "clip_range": 0.15, "ent_coef": 0.0},
    {"name": "LR_5e4_n_steps_2048", "learning_rate": 5e-4, "n_steps": 2048, "batch_size": 64, "gamma": 0.98, "clip_range": 0.25, "ent_coef": 0.005},
]

results = {}
best_config = None
best_model = None

for idx, config in enumerate(hyperparams, 1):
    print(f"\n{'='*70}")
    print(f"PPO Configuration {idx}/12: {config['name']}")
    print(f"{'='*70}")
    
    env = DaladalaEnv()
    model = PPO(
        "MlpPolicy", env,
        learning_rate=config['learning_rate'],
        n_steps=config['n_steps'],
        batch_size=config['batch_size'],
        gamma=config['gamma'],
        clip_range=config['clip_range'],
        ent_coef=config['ent_coef'],
        verbose=1,
        device='auto'
    )
    model.learn(total_timesteps=300000)

    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=50, deterministic=True)
    print(f"Mean Reward: {mean_reward:.2f} ± {std_reward:.2f}")

    results[config['name']] = {
        'config': config,
        'mean_reward': mean_reward,
        'std_reward': std_reward
    }

    if mean_reward > best_reward:
        best_reward = mean_reward
        best_config = config['name']
        best_model = model
        print("✓ NEW BEST PPO MODEL FOUND!")

    env.close()

# Save best model
if best_model:
    best_model.save("models/ppo/best_ppo")
    print(f"✓ Best model saved to models/ppo/best_ppo")

# Save results
results_summary = {}
for config_name, config_results in results.items():
    results_summary[config_name] = {
        'mean_reward': float(config_results['mean_reward']),
        'std_reward': float(config_results['std_reward']),
        'hyperparameters': {
            'learning_rate': config_results['config']['learning_rate'],
            'n_steps': config_results['config']['n_steps'],
            'batch_size': config_results['config']['batch_size'],
            'gamma': config_results['config']['gamma'],
            'clip_range': config_results['config']['clip_range'],
            'ent_coef': config_results['config']['ent_coef']
        }
    }

with open("results/ppo_results.json", "w") as f:
    json.dump(results_summary, f, indent=2)

print(f"\n{'='*70}")
print(f"PPO Training Complete!")
print(f"Best Configuration: {best_config}")
print(f"Best Mean Reward: {best_reward:.2f}")
print(f"Results saved to results/ppo_results.json")
print(f"{'='*70}")