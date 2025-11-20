# main.py
"""
Run any trained RL agent in the Daladala environment.
Displays real-time visualization with verbose console output.

This script lets you choose which algorithm (DQN, PPO, A2C, REINFORCE) to run.
Shows the agent's decision-making process and performance metrics.
"""

from stable_baselines3 import DQN, PPO, A2C
from environment import DaladalaEnv
from environment.rendering import render_frame
import torch
from training.reinforce_training import Policy
import os

def choose_model():
    """Display menu and get user choice of algorithm."""
    print("\n" + "="*80)
    print("DALADALA AGENT - SELECT MODEL")
    print("="*80)
    
    algorithms = {
        "1": ("DQN", "models/dqn/best_dqn.zip", DQN),
        "2": ("PPO", "models/ppo/best_ppo.zip", PPO),
        "3": ("A2C", "models/a2c/best_a2c.zip", A2C),
        "4": ("REINFORCE", "models/reinforce/best_reinforce.pth", None),
    }
    
    print("\nAvailable Models:")
    available_choices = []
    for key, (name, path, _) in algorithms.items():
        exists = "✓" if os.path.exists(path) else "✗"
        print(f"  {key}. {name:<12} {exists} ({path})")
        if os.path.exists(path):
            available_choices.append(key)
    
    if not available_choices:
        print("\n✗ No trained models found!")
        print("  Please run training scripts first:")
        print("    python training/dqn_training.py")
        print("    python training/ppo_training.py")
        print("    python training/a2c_training.py")
        print("    python training/reinforce_training.py")
        return None
    
    while True:
        choice = input(f"\nSelect model ({','.join(available_choices)}): ").strip()
        if choice in algorithms:
            if os.path.exists(algorithms[choice][1]):
                return algorithms[choice]
            else:
                print(f"✗ Model file not found. Please train it first.")
        else:
            print(f"✗ Invalid choice. Select from: {','.join(available_choices)}")

def load_model(algo_name, model_path, model_class):
    """Load the selected model."""
    print(f"\nLoading best {algo_name} model...")
    
    if not os.path.exists(model_path):
        print(f"✗ Model not found at {model_path}")
        print(f"  Please run: python training/{algo_name.lower()}_training.py")
        return None
    
    try:
        if algo_name == "REINFORCE":
            # Load REINFORCE custom model
            model = Policy(hidden_size=256)
            model.load_state_dict(torch.load(model_path))
            model.eval()
        else:
            # Load SB3 models
            model = model_class.load(model_path)
        
        print(f"✓ {algo_name} model loaded successfully")
        return model
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return None

def predict_action(model, obs, algo_name):
    """Get action from model based on algorithm type."""
    if algo_name == "REINFORCE":
        obs_tensor = torch.from_numpy(obs).float()
        with torch.no_grad():
            probs = model(obs_tensor)
            action = torch.argmax(probs).item()
    else:
        action, _ = model.predict(obs, deterministic=True)
    
    return action

def main():
    print("\n" + "="*80)
    print("DALADALA AGENT - BEST MODEL DEMONSTRATION")
    print("="*80)
    
    # Choose model
    result = choose_model()
    if result is None:
        return
    
    algo_name, model_path, model_class = result
    
    # Load model
    model = load_model(algo_name, model_path, model_class)
    if model is None:
        return
    
    env = DaladalaEnv(render_mode="human")
    
    print("\n" + "-"*80)
    print("ENVIRONMENT SPECIFICATIONS")
    print("-"*80)
    print(f"Route length: {len(env.route)} cells")
    print(f"High-demand stops: {env.high_demand_stops}")
    print(f"Police checkpoints: {env.police_checkpoints}")
    print(f"Traffic lights: {env.traffic_lights}")
    print(f"Legal capacity: 33 passengers")
    print(f"Physical max: {env.physical_max} passengers")
    print(f"Max episode length: {env.max_steps} steps")
    print(f"\nOBJECTIVE: Reach destination while maximizing profit and safety")
    print(f"REWARD STRUCTURE: Progress + Passenger delivery - Safety penalties")
    
    print("\n" + "-"*80)
    print("EPISODE SIMULATION")
    print("-"*80 + "\n")
    print(">>> Pygame window opening... Check your taskbar or screen!")
    print(">>> Rendering at 2 FPS (500ms per frame) for easy observation")
    print(">>> Close the window when done\n")
    
    obs, info = env.reset()
    total_reward = 0
    episode_data = []
    last_action = None
    last_reward = 0.0
    
    step = 0
    while True:
        # Get action from model
        action = predict_action(model, obs, algo_name)
        
        # Step environment
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        # Render frame
        render_frame(env, action, reward, rgb=False)
        
        # Verbose logging
        action_names = ["Move Forward", "Stop", "Pick Up", "Drop Off", "Speed Up"]
        action_name = action_names[action] if action < len(action_names) else "Unknown"
        
        step_info = {
            'step': env.step_count,
            'action': action_name,
            'passengers': env.passengers,
            'money': env.money,
            'position': env.pos_idx,
            'speed': env.speed,
            'reward': reward,
            'cumulative': total_reward,
        }
        episode_data.append(step_info)
        
        # Print step info
        if env.step_count % 10 == 0 or env.step_count <= 5:
            print(f"Step {env.step_count:3d} | {action_name:15s} | "
                  f"Passengers: {env.passengers:2d}/50 | Money: TSh {int(env.money):7,d} | "
                  f"Reward: {reward:+7.2f} | Total: {total_reward:+8.2f}")
        
        last_action = action
        last_reward = reward
        
        if terminated or truncated:
            break
        
        step += 1
    
    # Episode summary
    print("\n" + "="*80)
    print("EPISODE SUMMARY")
    print("="*80)
    print(f"Algorithm: {algo_name}")
    print(f"Total Steps: {env.step_count}")
    print(f"Total Reward: {total_reward:+.2f}")
    print(f"Final Passengers: {env.passengers} / 33 (Legal)")
    print(f"Total Money Earned: TSh {int(env.money):,}")
    print(f"Fined: {'Yes' if env.fined else 'No'}")
    print(f"Route Progress: {env.pos_idx} / {len(env.route)-1} cells")
    
    # Safety metrics
    legal_trips = 1 if env.passengers <= 33 else 0
    print(f"\nSafety Metrics:")
    print(f"  Legal capacity maintained: {'✓ Yes' if legal_trips else '✗ No'}")
    print(f"  Reached destination: {'✓ Yes' if env.pos_idx >= len(env.route)-1 else '✗ No'}")
    print(f"  Penalties incurred: {'✗ Yes' if env.fined else '✓ No'}")
    
    # Performance rating
    print(f"\nPerformance Rating:")
    if total_reward > 200:
        print(f"  ★★★★★ Excellent - Agent achieved high reward with safe operations")
    elif total_reward > 100:
        print(f"  ★★★★☆ Very Good - Strong performance with mostly safe decisions")
    elif total_reward > 0:
        print(f"  ★★★☆☆ Good - Reasonable performance, some safety issues")
    else:
        print(f"  ★★☆☆☆ Fair - Below target, needs improvement")
    
    print("\n" + "="*80)
    print(f"Simulation completed. Window will close automatically.")
    print("="*80 + "\n")
    
    env.close()

if __name__ == "__main__":
    main()