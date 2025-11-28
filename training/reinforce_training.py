# training/reinforce_training.py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import numpy as np
from environment import DaladalaEnv
import json
import os
import time
import pandas as pd

# Create results directory
os.makedirs("results", exist_ok=True)
os.makedirs("models/reinforce", exist_ok=True)

# Check GPU availability
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"✓ Using device: {device}")

class PolicyNetwork(nn.Module):
    """Neural network policy for REINFORCE algorithm."""
    def __init__(self, state_dim, action_dim, hidden_dim):
        super(PolicyNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim)
        )

    def forward(self, state):
        return torch.softmax(self.net(state), dim=-1)

    def get_action_and_log_prob(self, state):
        """Get action and log probability from policy."""
        probs = self.forward(state)
        dist = Categorical(probs)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        return action.item(), log_prob

class REINFORCEAgent:
    """REINFORCE (Policy Gradient) agent."""
    def __init__(self, state_dim, action_dim, hidden_dim, learning_rate, device='cpu'):
        self.policy = PolicyNetwork(state_dim, action_dim, hidden_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=learning_rate)
        self.device = device
        self.policy.to(self.device)

    def train_episode(self, env):
        """Train for one complete episode."""
        obs, _ = env.reset()
        log_probs = []
        rewards = []
        done = False

        while not done:
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
            action, log_prob = self.policy.get_action_and_log_prob(obs_tensor)
            obs, reward, terminated, truncated, _ = env.step(action)

            log_probs.append(log_prob)
            rewards.append(reward)
            done = terminated or truncated

        # Calculate returns (discounted cumulative rewards)
        returns = []
        cumulative_return = 0
        for reward in reversed(rewards):
            cumulative_return = reward + 0.99 * cumulative_return
            returns.insert(0, cumulative_return)

        # Normalize returns
        returns = torch.tensor(returns, dtype=torch.float32).to(self.device)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        # Calculate policy loss
        policy_loss = 0
        for log_prob, return_val in zip(log_probs, returns):
            policy_loss += -log_prob * return_val

        # Update policy
        self.optimizer.zero_grad()
        policy_loss.backward()
        self.optimizer.step()

        return sum(rewards)

    def evaluate(self, env, n_episodes=50):
        """Evaluate agent performance."""
        rewards = []
        for _ in range(n_episodes):
            obs, _ = env.reset()
            total_reward = 0
            done = False

            while not done:
                obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    probs = self.policy(obs_tensor)
                    action = probs.argmax(dim=-1).item()
                obs, reward, terminated, truncated, _ = env.step(action)
                total_reward += reward
                done = terminated or truncated

            rewards.append(total_reward)

        return np.mean(rewards), np.std(rewards)

    def save(self, path):
        """Save model to disk."""
        torch.save(self.policy.state_dict(), path + '_policy.pth')

    def load(self, path):
        """Load model from disk."""
        self.policy.load_state_dict(torch.load(path + '_policy.pth', map_location=self.device))

if __name__ == "__main__":
    # Hyperparameter (12 configurations)
    reinforce_configs = [
        {"name": "LR_1e3_hid_64", "learning_rate": 1e-3, "hidden_dim": 64},
        {"name": "LR_1e3_hid_128", "learning_rate": 1e-3, "hidden_dim": 128},
        {"name": "LR_3e3_hid_64", "learning_rate": 3e-3, "hidden_dim": 64},
        {"name": "LR_3e3_hid_128", "learning_rate": 3e-3, "hidden_dim": 128},
        {"name": "LR_5e3_hid_64", "learning_rate": 5e-3, "hidden_dim": 64},
        {"name": "LR_5e3_hid_128", "learning_rate": 5e-3, "hidden_dim": 128},
        {"name": "LR_1e2_hid_64", "learning_rate": 1e-2, "hidden_dim": 64},
        {"name": "LR_1e2_hid_128", "learning_rate": 1e-2, "hidden_dim": 128},
        {"name": "LR_1e2_hid_256", "learning_rate": 1e-2, "hidden_dim": 256},
        {"name": "LR_5e3_hid_256", "learning_rate": 5e-3, "hidden_dim": 256},
        {"name": "LR_3e3_hid_256", "learning_rate": 3e-3, "hidden_dim": 256},
        {"name": "LR_1e3_hid_256", "learning_rate": 1e-3, "hidden_dim": 256},
    ]

    results = {}
    best_reward = -float('inf')
    best_config = None
    best_agent = None

    total_configs = len(reinforce_configs)
    state_dim = 14
    action_dim = 5

    # Training parameters
    target_steps = 300000
    steps_per_episode = 350
    episodes_per_config = (target_steps + steps_per_episode - 1) // steps_per_episode  # ~857 episodes

    for idx, config in enumerate(reinforce_configs, 1):
        print(f"\n{'='*70}")
        print(f"Training Configuration {idx}/{total_configs}: {config['name']}")
        print(f"{'='*70}")
        print(f"Learning Rate: {config['learning_rate']}, Hidden Dim: {config['hidden_dim']}")
        print(f"Target: {target_steps:,} timesteps (~{episodes_per_config} episodes)")
        print(f"Device: {device}\n")

        # Create environment
        env = DaladalaEnv()

        # Initialize REINFORCE agent with GPU support
        agent = REINFORCEAgent(
            state_dim=state_dim,
            action_dim=action_dim,
            hidden_dim=config['hidden_dim'],
            learning_rate=config['learning_rate'],
            device=device
        )

        # Training loop
        start_time = time.time()
        episode_rewards = []
        total_steps = 0

        for episode in range(episodes_per_config):
            ep_reward = agent.train_episode(env)
            episode_rewards.append(ep_reward)
            total_steps += steps_per_episode

            if (episode + 1) % 50 == 0 or episode == 0:
                recent_avg = np.mean(episode_rewards[-50:]) if len(episode_rewards) >= 50 else np.mean(episode_rewards)
                elapsed = time.time() - start_time
                eps_per_sec = (episode + 1) / elapsed
                eta_sec = (episodes_per_config - episode - 1) / eps_per_sec if eps_per_sec > 0 else 0

                print(f"  Episode {episode+1:4d}/{episodes_per_config} | "
                      f"Recent Avg: {recent_avg:7.2f} | "
                      f"Last Reward: {ep_reward:7.2f} | "
                      f"Steps: {total_steps:,} | "
                      f"ETA: {int(eta_sec//60):3d}m {int(eta_sec%60):02d}s")

        training_time = time.time() - start_time

        # Evaluate agent on 50 episodes 
        print(f"\n  Evaluating on 50 episodes...")
        eval_start = time.time()
        mean_reward, std_reward = agent.evaluate(env, n_episodes=50)
        eval_time = time.time() - eval_start

        results[config['name']] = {
            'config': config,
            'mean_reward': mean_reward,
            'std_reward': std_reward,
            'training_time': training_time,
            'eval_time': eval_time
        }

        print(f"  ✓ Evaluation Complete!")
        print(f"    Mean Reward: {mean_reward:.2f} (±{std_reward:.2f})")
        print(f"    Training Time: {int(training_time//60)}m {int(training_time%60)}s")

        # Track best model
        if mean_reward > best_reward:
            best_reward = mean_reward
            best_config = config['name']
            best_agent = agent
            print(f"    ★ NEW BEST MODEL! ★")

        env.close()

    # Save best model
    if best_agent:
        best_model_path = 'models/reinforce/best_reinforce'
        best_agent.save(best_model_path)
        print(f"✓ Best model saved to: {best_model_path}_policy.pth")

    # Save results as JSON
    results_json_path = 'results/reinforce_results.json'
    results_summary = {}
    for config_name, config_results in results.items():
        results_summary[config_name] = {
            'mean_reward': float(config_results['mean_reward']),
            'std_reward': float(config_results['std_reward']),
            'hyperparameters': {
                'learning_rate': config_results['config']['learning_rate'],
                'hidden_dim': config_results['config']['hidden_dim']
            }
        }

    with open(results_json_path, 'w') as f:
        json.dump(results_summary, f, indent=2)
    print(f"✓ Results saved to: {results_json_path}")

    print(f"\n{'='*70}")
    print(f"REINFORCE Training Complete!")
    print(f"Best Configuration: {best_config}")
    print(f"Best Mean Reward: {best_reward:.2f}")
    print(f"Results saved to results/reinforce_results.json")
    print(f"{'='*70}")