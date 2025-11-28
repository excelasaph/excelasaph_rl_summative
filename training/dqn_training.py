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

# Hyperparameter (12 configurations)
hyperparams = [
    {"name": "LR_1e4_buf_10k_eps_025", "learning_rate": 1e-4, "buffer_size": 100000, "exploration_fraction": 0.25, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.05, "gamma": 0.65},
    {"name": "LR_1e4_buf_50k_eps_05", "learning_rate": 1e-4, "buffer_size": 50000, "exploration_fraction": 0.5, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.05, "gamma": 0.70},
    {"name": "LR_3e4_buf_10k_eps_025", "learning_rate": 3e-4, "buffer_size": 10000, "exploration_fraction": 0.25, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.05, "gamma": 0.75},
    {"name": "LR_3e4_buf_50k_eps_05", "learning_rate": 3e-4, "buffer_size": 50000, "exploration_fraction": 0.5, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.05, "gamma": 0.77},
    {"name": "LR_5e4_buf_10k_eps_025", "learning_rate": 5e-4, "buffer_size": 10000, "exploration_fraction": 0.25, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.1, "gamma": 0.80},
    {"name": "LR_5e4_buf_50k_eps_05", "learning_rate": 5e-4, "buffer_size": 50000, "exploration_fraction": 0.5, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.1, "gamma": 0.85},
    {"name": "LR_7e4_buf_10k_eps_025", "learning_rate": 7e-4, "buffer_size": 10000, "exploration_fraction": 0.25, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.02, "gamma": 0.90},
    {"name": "LR_7e4_buf_50k_eps_05", "learning_rate": 7e-4, "buffer_size": 50000, "exploration_fraction": 0.5, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.02, "gamma": 0.95},
    {"name": "LR_1e3_buf_10k_eps_025", "learning_rate": 1e-3, "buffer_size": 10000, "exploration_fraction": 0.25, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.05, "gamma": 0.995},
    {"name": "LR_1e3_buf_50k_eps_05", "learning_rate": 1e-3, "buffer_size": 50000, "exploration_fraction": 0.5, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.05, "gamma": 0.67},
    {"name": "LR_1e3_buf_100k_eps_1", "learning_rate": 1e-3, "buffer_size": 100000, "exploration_fraction": 1.0, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.05, "gamma": 0.77},
    {"name": "LR_5e4_buf_100k_eps_1", "learning_rate": 5e-4, "buffer_size": 100000, "exploration_fraction": 1.0, "exploration_initial_eps": 1.0, "exploration_final_eps": 0.1, "gamma": 0.98},
]

results = {}
best_config = None
best_model = None

for idx, config in enumerate(hyperparams, 1):
    print(f"\n{'='*70}")
    print(f"DQN Configuration {idx}/12: {config['name']}")
    print(f"{'='*70}")
    
    env = DaladalaEnv()
    model = DQN(
        "MlpPolicy", env,
        learning_rate=config['learning_rate'],
        buffer_size=config['buffer_size'],
        exploration_fraction=config['exploration_fraction'],
        exploration_initial_eps=config['exploration_initial_eps'],
        exploration_final_eps=config['exploration_final_eps'],
        gamma=config['gamma'],
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
        print("✓ NEW BEST DQN MODEL FOUND!")

    env.close()

# Save best model
if best_model:
    best_model.save("models/dqn/best_dqn")
    print(f"✓ Best model saved to models/dqn/best_dqn")

# Save results
results_summary = {}
for config_name, config_results in results.items():
    results_summary[config_name] = {
        'mean_reward': float(config_results['mean_reward']),
        'std_reward': float(config_results['std_reward']),
        'hyperparameters': {
            'learning_rate': config_results['config']['learning_rate'],
            'buffer_size': config_results['config']['buffer_size'],
            'exploration_fraction': config_results['config']['exploration_fraction'],
            'exploration_initial_eps': config_results['config']['exploration_initial_eps'],
            'exploration_final_eps': config_results['config']['exploration_final_eps'],
            'gamma': config_results['config']['gamma']
        }
    }

with open("results/dqn_results.json", "w") as f:
    json.dump(results_summary, f, indent=2)

print(f"\n{'='*70}")
print(f"DQN Training Complete!")
print(f"Best Configuration: {best_config}")
print(f"Best Mean Reward: {best_reward:.2f}")
print(f"Results saved to results/dqn_results.json")
print(f"{'='*70}")