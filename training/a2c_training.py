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

# Hyperparameter (12 configurations)
hyperparams = [
    {"name": "LR_1e4_n5_g099", "learning_rate": 1e-3, "n_steps": 5, "gamma": 0.65, "gae_lambda": 0.95, "ent_coef": 0.0},
    {"name": "LR_1e4_n5_g0995", "learning_rate": 1e-4, "n_steps": 5, "gamma": 0.70, "gae_lambda": 0.95, "ent_coef": 0.0},
    {"name": "LR_3e4_n8_g099", "learning_rate": 3e-4, "n_steps": 8, "gamma": 0.75, "gae_lambda": 0.95, "ent_coef": 0.005},
    {"name": "LR_3e4_n8_g0995", "learning_rate": 3e-4, "n_steps": 8, "gamma": 0.77, "gae_lambda": 0.95, "ent_coef": 0.005},
    {"name": "LR_5e4_n10_g099", "learning_rate": 5e-4, "n_steps": 10, "gamma": 0.80, "gae_lambda": 1.0, "ent_coef": 0.01},
    {"name": "LR_5e4_n10_g0995", "learning_rate": 5e-4, "n_steps": 10, "gamma": 0.85, "gae_lambda": 1.0, "ent_coef": 0.01},
    {"name": "LR_7e4_n5_g099", "learning_rate": 7e-4, "n_steps": 5, "gamma": 0.90, "gae_lambda": 0.95, "ent_coef": 0.05},
    {"name": "LR_7e4_n5_g0995", "learning_rate": 7e-4, "n_steps": 5, "gamma": 0.95, "gae_lambda": 0.95, "ent_coef": 0.05},
    {"name": "LR_1e3_n8_g099", "learning_rate": 1e-3, "n_steps": 8, "gamma": 0.995, "gae_lambda": 1.0, "ent_coef": 0.01},
    {"name": "LR_1e3_n8_g0995", "learning_rate": 1e-3, "n_steps": 8, "gamma": 0.67, "gae_lambda": 1.0, "ent_coef": 0.01},
    {"name": "LR_1e3_n10_g099", "learning_rate": 1e-3, "n_steps": 10, "gamma": 0.77, "gae_lambda": 0.95, "ent_coef": 0.0},
    {"name": "LR_1e3_n10_g0995", "learning_rate": 1e-3, "n_steps": 10, "gamma": 0.98, "gae_lambda": 0.95, "ent_coef": 0.0},
]

results = {}
best_config = None
best_model = None

for idx, config in enumerate(hyperparams, 1):
    print(f"\n{'='*70}")
    print(f"A2C Configuration {idx}/12: {config['name']}")
    print(f"{'='*70}")
    
    env = DaladalaEnv()
    model = A2C(
        "MlpPolicy", env,
        learning_rate=config['learning_rate'],
        n_steps=config['n_steps'],
        gamma=config['gamma'],
        gae_lambda=config['gae_lambda'],
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
        print("✓ NEW BEST A2C MODEL FOUND!")

    env.close()

# Save best model
if best_model:
    best_model.save("models/a2c/best_a2c")
    print(f"✓ Best model saved to models/a2c/best_a2c")

# Save results
results_summary = {}
for config_name, config_results in results.items():
    results_summary[config_name] = {
        'mean_reward': float(config_results['mean_reward']),
        'std_reward': float(config_results['std_reward']),
        'hyperparameters': {
            'learning_rate': config_results['config']['learning_rate'],
            'n_steps': config_results['config']['n_steps'],
            'gamma': config_results['config']['gamma'],
            'gae_lambda': config_results['config']['gae_lambda'],
            'ent_coef': config_results['config']['ent_coef']
        }
    }

with open("results/a2c_results.json", "w") as f:
    json.dump(results_summary, f, indent=2)

print(f"\n{'='*70}")
print(f"A2C Training Complete!")
print(f"Best Configuration: {best_config}")
print(f"Best Mean Reward: {best_reward:.2f}")
print(f"Results saved to results/a2c_results.json")
print(f"{'='*70}")