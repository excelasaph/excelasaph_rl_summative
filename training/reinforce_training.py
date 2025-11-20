# training/reinforce_training.py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import numpy as np
from environment import DaladalaEnv
import json
import os

# Create results directory
os.makedirs("results", exist_ok=True)

class Policy(nn.Module):
    def __init__(self, hidden_size=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(15, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 8),
            nn.Softmax(dim=-1)
        )
        self.saved_log_probs = []
        self.rewards = []

    def forward(self, x):
        return self.net(x)

def select_action(state, policy):
    state = torch.from_numpy(state).float()
    probs = policy(state)
    m = Categorical(probs)
    action = m.sample()
    policy.saved_log_probs.append(m.log_prob(action))
    return action.item()

def finish_episode(policy, optimizer, gamma=0.99):
    R = 0
    policy_loss = []
    returns = []
    for r in policy.rewards[::-1]:
        R = r + gamma * R
        returns.insert(0, R)
    returns = torch.tensor(returns)
    returns = (returns - returns.mean()) / (returns.std() + 1e-8)
    for log_prob, R in zip(policy.saved_log_probs, returns):
        policy_loss.append(-log_prob * R)
    optimizer.zero_grad()
    policy_loss = torch.cat(policy_loss).sum()
    policy_loss.backward()
    optimizer.step()
    del policy.rewards[:]
    del policy.saved_log_probs[:]

if __name__ == "__main__":
    best_reward = -np.inf
    all_results = []

    # Comprehensive hyperparameter grid (12 configurations)
    hyperparams = [
        {"lr": 1e-4, "hidden": 128, "gamma": 0.99},
        {"lr": 1e-4, "hidden": 256, "gamma": 0.99},
        {"lr": 3e-4, "hidden": 128, "gamma": 0.99},
        {"lr": 3e-4, "hidden": 256, "gamma": 0.995},
        {"lr": 5e-4, "hidden": 128, "gamma": 0.99},
        {"lr": 5e-4, "hidden": 256, "gamma": 0.99},
        {"lr": 7e-4, "hidden": 128, "gamma": 0.995},
        {"lr": 7e-4, "hidden": 256, "gamma": 0.99},
        {"lr": 1e-3, "hidden": 128, "gamma": 0.99},
        {"lr": 1e-3, "hidden": 256, "gamma": 0.995},
        {"lr": 3e-4, "hidden": 128, "gamma": 0.995},
        {"lr": 5e-4, "hidden": 256, "gamma": 0.995},
    ]

    for idx, params in enumerate(hyperparams):
        print(f"\n{'='*70}")
        print(f"REINFORCE Configuration {idx+1}/12")
        print(f"lr={params['lr']}, hidden={params['hidden']}, gamma={params['gamma']}")
        print(f"{'='*70}")
        
        env = DaladalaEnv()
        policy = Policy(hidden_size=params['hidden'])
        optimizer = optim.Adam(policy.parameters(), lr=params['lr'])

        episode_rewards = []
        for i in range(3000):  # ~300k steps
            state, _ = env.reset()
            episode_reward = 0
            while True:
                action = select_action(state, policy)
                state, reward, terminated, truncated, _ = env.step(action)
                policy.rewards.append(reward)
                episode_reward += reward
                if terminated or truncated:
                    finish_episode(policy, optimizer, gamma=params['gamma'])
                    break

            episode_rewards.append(episode_reward)
            if i % 300 == 0:
                print(f"Episode {i} | Reward: {episode_reward:.1f}")

        # Evaluate
        eval_rewards = []
        for _ in range(50):
            state, _ = env.reset()
            total = 0
            while True:
                action = select_action(state, policy)
                state, r, t, tr, _ = env.step(action)
                total += r
                if t or tr:
                    break
            eval_rewards.append(total)
        
        mean_reward = np.mean(eval_rewards)
        std_reward = np.std(eval_rewards)
        print(f"Final Mean Reward: {mean_reward:.2f} ± {std_reward:.2f}")

        result = {
            "config": idx + 1,
            "hyperparams": params,
            "mean_reward": float(mean_reward),
            "std_reward": float(std_reward),
            "total_episodes": 3000,
            "eval_episodes": 50
        }
        all_results.append(result)

        if mean_reward > best_reward:
            best_reward = mean_reward
            torch.save(policy.state_dict(), "models/reinforce/best_reinforce.pth")
            print("✓ NEW BEST REINFORCE MODEL SAVED!")

        env.close()

    # Save results
    with open("results/reinforce_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*70}")
    print(f"REINFORCE Training Complete!")
    print(f"Best Mean Reward: {best_reward:.2f}")
    print(f"Results saved to results/reinforce_results.json")
    print(f"{'='*70}")