# comparison_eval.py
"""
Model Comparison & Evaluation
Evaluates all 4 trained RL agents side-by-side with detailed metrics.
"""
import numpy as np
import json
from pathlib import Path
from stable_baselines3 import DQN, PPO, A2C
import torch
from environment import DaladalaEnv
from training.reinforce_training import Policy

def evaluate_model(model, env, n_episodes=100, model_type="sb3"):
    """Evaluate a trained model and collect detailed metrics."""
    rewards = []
    passengers_delivered = []
    legal_trips = []
    crashes = []
    fines = []
    
    for _ in range(n_episodes):
        obs, _ = env.reset()
        episode_reward = 0
        crashed = False
        fined = False
        
        while True:
            if model_type == "sb3":
                action, _ = model.predict(obs, deterministic=True)
            elif model_type == "reinforce":
                obs_tensor = torch.from_numpy(obs).float()
                probs = model(obs_tensor)
                action = torch.argmax(probs).item()
            
            obs, reward, terminated, truncated, _ = env.step(action)
            episode_reward += reward
            
            if terminated:
                if env.passengers <= 40 or env.step_count >= env.max_steps:
                    if env.passengers > 40:
                        crashed = True
                    if env.fined:
                        fined = True
                break
            if truncated:
                break
        
        rewards.append(episode_reward)
        passengers_delivered.append(env.passengers)
        legal_trips.append(1 if env.passengers <= 33 else 0)
        crashes.append(1 if crashed else 0)
        fines.append(1 if fined else 0)
    
    return {
        "mean_reward": np.mean(rewards),
        "std_reward": np.std(rewards),
        "max_reward": np.max(rewards),
        "min_reward": np.min(rewards),
        "avg_passengers": np.mean(passengers_delivered),
        "legal_compliance": np.mean(legal_trips),
        "crash_rate": np.mean(crashes),
        "fine_rate": np.mean(fines),
    }

def main():
    print("\n" + "="*80)
    print("DALADALA AGENT COMPARISON & EVALUATION")
    print("="*80 + "\n")
    
    env = DaladalaEnv()
    results = {}
    
    # ===== DQN =====
    try:
        print("Evaluating DQN...")
        dqn_model = DQN.load("models/dqn/best_dqn")
        dqn_metrics = evaluate_model(dqn_model, env, n_episodes=100, model_type="sb3")
        results["DQN"] = dqn_metrics
        print(f"  ✓ Mean Reward: {dqn_metrics['mean_reward']:.2f} ± {dqn_metrics['std_reward']:.2f}")
    except Exception as e:
        print(f"  ✗ Failed to load DQN: {e}")
    
    # ===== PPO =====
    try:
        print("Evaluating PPO...")
        ppo_model = PPO.load("models/ppo/best_ppo")
        ppo_metrics = evaluate_model(ppo_model, env, n_episodes=100, model_type="sb3")
        results["PPO"] = ppo_metrics
        print(f"  ✓ Mean Reward: {ppo_metrics['mean_reward']:.2f} ± {ppo_metrics['std_reward']:.2f}")
    except Exception as e:
        print(f"  ✗ Failed to load PPO: {e}")
    
    # ===== A2C =====
    try:
        print("Evaluating A2C...")
        a2c_model = A2C.load("models/a2c/best_a2c")
        a2c_metrics = evaluate_model(a2c_model, env, n_episodes=100, model_type="sb3")
        results["A2C"] = a2c_metrics
        print(f"  ✓ Mean Reward: {a2c_metrics['mean_reward']:.2f} ± {a2c_metrics['std_reward']:.2f}")
    except Exception as e:
        print(f"  ✗ Failed to load A2C: {e}")
    
    # ===== REINFORCE =====
    try:
        print("Evaluating REINFORCE...")
        # Architecture matches the saved checkpoint: Input 14 -> Hidden 64 -> Output 5
        reinforce_model = Policy(hidden_size=64)
        reinforce_model.load_state_dict(torch.load("models/reinforce/best_reinforce_policy.pth"))
        reinforce_model.eval()
        reinforce_metrics = evaluate_model(reinforce_model, env, n_episodes=100, model_type="reinforce")
        results["REINFORCE"] = reinforce_metrics
        print(f"  ✓ Mean Reward: {reinforce_metrics['mean_reward']:.2f} ± {reinforce_metrics['std_reward']:.2f}")
    except Exception as e:
        print(f"  ✗ Failed to load REINFORCE: {e}")
    
    # ===== COMPARISON TABLE =====
    print("\n" + "="*80)
    print("COMPARISON TABLE (100 evaluation episodes per model)")
    print("="*80 + "\n")
    
    print(f"{'Algorithm':<15} {'Mean Reward':<15} {'Std Dev':<12} {'Legal %':<12} {'Crash %':<12} {'Fine %':<12}")
    print("-" * 80)
    
    for algo, metrics in results.items():
        print(f"{algo:<15} {metrics['mean_reward']:>8.2f}       {metrics['std_reward']:>8.2f}     "
              f"{metrics['legal_compliance']*100:>6.1f}%     {metrics['crash_rate']*100:>6.1f}%     "
              f"{metrics['fine_rate']*100:>6.1f}%")
    
    print("\n" + "="*80)
    print("DETAILED METRICS")
    print("="*80 + "\n")
    
    for algo, metrics in results.items():
        print(f"\n{algo}:")
        print(f"  Reward Stats:")
        print(f"    Mean: {metrics['mean_reward']:.2f}")
        print(f"    Std:  {metrics['std_reward']:.2f}")
        print(f"    Max:  {metrics['max_reward']:.2f}")
        print(f"    Min:  {metrics['min_reward']:.2f}")
        print(f"  Safety & Legal:")
        print(f"    Avg Passengers Delivered: {metrics['avg_passengers']:.1f}")
        print(f"    Legal Trips (≤33 pax): {metrics['legal_compliance']*100:.1f}%")
        print(f"    Crash Rate: {metrics['crash_rate']*100:.1f}%")
        print(f"    Fine Rate: {metrics['fine_rate']*100:.1f}%")
    
    # ===== BEST PERFORMER =====
    if results:
        best_algo = max(results, key=lambda x: results[x]['mean_reward'])
        print(f"\n{'='*80}")
        print(f"🏆 BEST PERFORMER: {best_algo}")
        print(f"   Mean Reward: {results[best_algo]['mean_reward']:.2f}")
        print(f"{'='*80}\n")
    
    # Save results
    Path("results").mkdir(exist_ok=True)
    with open("results/comparison_results.json", "w") as f:
        # Convert numpy types to Python types for JSON serialization
        json_results = {}
        for algo, metrics in results.items():
            json_results[algo] = {k: float(v) for k, v in metrics.items()}
        json.dump(json_results, f, indent=2)
    
    print("Results saved to results/comparison_results.json")
    env.close()

if __name__ == "__main__":
    main()
