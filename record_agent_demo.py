"""
Record agent performance as an animated GIF.
Runs a trained model and saves the episode as a slow-motion GIF for analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle
from stable_baselines3 import DQN, PPO, A2C
from environment import DaladalaEnv
from training.reinforce_training import Policy
import torch

def choose_model():
    """Display menu and get user choice of algorithm."""
    print("\n" + "="*80)
    print("SELECT MODEL TO RECORD")
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
        return None
    
    while True:
        choice = input(f"\nSelect model ({','.join(available_choices)}): ").strip()
        if choice in algorithms:
            if os.path.exists(algorithms[choice][1]):
                return algorithms[choice]
            else:
                print(f"✗ Model file not found.")
        else:
            print(f"✗ Invalid choice.")

def load_model(algo_name, model_path, model_class):
    """Load the selected model."""
    print(f"\nLoading {algo_name} model...")
    
    if not os.path.exists(model_path):
        print(f"✗ Model not found at {model_path}")
        return None
    
    try:
        if algo_name == "REINFORCE":
            model = Policy(hidden_size=256)
            model.load_state_dict(torch.load(model_path))
            model.eval()
        else:
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

def run_episode(env, model, algo_name):
    """Run one episode and collect frame data with action visualization."""
    frames = []
    obs, _ = env.reset()
    total_reward = 0
    step = 0
    
    action_names = {0: "Move", 1: "Pickup", 2: "Dropoff", 3: "Stop", 4: "SpeedUp"}
    
    # First frame: starting position with no action yet
    x, y = env.route[env.pos_idx]
    frame_data = {
        'step': env.step_count,
        'pos_x': x,
        'pos_y': y,
        'passengers': env.passengers,
        'money': env.money,
        'speed': env.speed,
        'fined': env.fined,
        'police_checkpoints': env.police_checkpoints.copy(),
        'traffic_lights': env.traffic_lights.copy(),
        'high_demand_stops': env.high_demand_stops,
        'action': "START",
        'action_id': -1,
        'reward': 0.0,
        'light_cycle': env.light_cycle,
        'phase': 'observation',  # Phase: observation, action_decision, movement
    }
    frames.append(frame_data)
    
    while True:
        # PHASE 1: DECISION FRAME - Show the state and the decision being made
        action = predict_action(model, obs, algo_name)
        action = int(action) if isinstance(action, np.ndarray) else action
        
        # Add decision frame (agent thinks before acting)
        x, y = env.route[env.pos_idx]
        decision_frame = {
            'step': env.step_count,
            'pos_x': x,
            'pos_y': y,
            'passengers': env.passengers,
            'money': env.money,
            'speed': env.speed,
            'fined': env.fined,
            'police_checkpoints': env.police_checkpoints.copy(),
            'traffic_lights': env.traffic_lights.copy(),
            'high_demand_stops': env.high_demand_stops,
            'action': action_names[action],
            'action_id': action,
            'reward': 0.0,
            'light_cycle': env.light_cycle,
            'phase': 'decision',  # Deciding what to do
        }
        frames.append(decision_frame)
        
        # PHASE 2: EXECUTE ACTION
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Add effect frame - Show result of action at current position
        x, y = env.route[env.pos_idx] if env.pos_idx < len(env.route) else (14, 0)
        effect_frame = {
            'step': env.step_count,
            'pos_x': x,
            'pos_y': y,
            'passengers': env.passengers,
            'money': env.money,
            'speed': env.speed,
            'fined': env.fined,
            'police_checkpoints': env.police_checkpoints.copy(),
            'traffic_lights': env.traffic_lights.copy(),
            'high_demand_stops': env.high_demand_stops,
            'action': action_names[action],
            'action_id': action,
            'reward': reward,
            'light_cycle': env.light_cycle,
            'phase': 'effect',  # Showing the effect/result
        }
        frames.append(effect_frame)
        
        total_reward += reward
        step += 1
        
        if terminated or truncated:
            break
    
    return frames, total_reward, env.passengers, env.fined

def create_gif(frames, algo_name, total_reward, final_passengers, was_fined):
    """Create animated GIF from frame data."""
    print(f"\n✓ Episode complete! Creating slow-motion GIF with {len(frames)} frames...")
    print("  Duration: ~2-3 minutes (super detailed view of every action)")
    
    # Create figure with larger size for better visibility
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Get frame data for first frame to set up layout
    first_frame = frames[0]
    
    def animate(frame_idx):
        ax.clear()
        frame = frames[frame_idx]
        
        # Draw grid
        for i in range(16):
            ax.axhline(y=i, color='lightgray', linewidth=0.5, alpha=0.5)
            ax.axvline(x=i, color='lightgray', linewidth=0.5, alpha=0.5)
        
        # Draw high-demand stops (gold circles)
        for idx, (sx, sy) in enumerate(frame['high_demand_stops']):
            circle = Circle((sx, sy), 0.35, color='gold', ec='darkgoldenrod', linewidth=2)
            ax.add_patch(circle)
            names = ["Ubungo", "Morocco", "Kariakoo", "Posta"]
            ax.text(sx, sy, names[idx], ha='center', va='center', fontsize=7, fontweight='bold')
        
        # Draw police checkpoints (red squares)
        for px, py in frame['police_checkpoints']:
            rect = Rectangle((px-0.4, py-0.4), 0.8, 0.8, color='red', ec='darkred', linewidth=2)
            ax.add_patch(rect)
            ax.text(px, py, 'P', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        
        # Draw traffic lights (circles with color based on cycle)
        light_is_red = (frame['light_cycle'] % 2 == 0)
        for tx, ty in frame['traffic_lights']:
            light_color = 'red' if light_is_red else 'green'
            circle = Circle((tx, ty), 0.3, color=light_color, ec='black', linewidth=2)
            ax.add_patch(circle)
        
        # Draw agent (bus) - green square with passenger count
        agent_x, agent_y = frame['pos_x'], frame['pos_y']
        if frame['passengers'] <= 33:
            bus_color = 'darkgreen'
            text_color = 'white'
        elif frame['passengers'] <= 40:
            bus_color = 'orange'
            text_color = 'black'
        else:
            bus_color = 'darkred'
            text_color = 'white'
        
        rect = Rectangle((agent_x-0.4, agent_y-0.4), 0.8, 0.8, color=bus_color, ec='black', linewidth=3)
        ax.add_patch(rect)
        ax.text(agent_x, agent_y, str(frame['passengers']), ha='center', va='center', 
               fontsize=14, color=text_color, fontweight='bold')
        
        # Set up axes
        ax.set_xlim(-1, 15.5)
        ax.set_ylim(-1, 15.5)
        ax.set_aspect('equal')
        ax.invert_yaxis()
        ax.set_title(f'{algo_name} Agent - Slow-Motion Episode Analysis\nStep {frame["step"]}/350', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('X Position', fontsize=12, fontweight='bold')
        ax.set_ylabel('Y Position', fontsize=12, fontweight='bold')
        
        # === ACTION PANEL (LEFT SIDE) ===
        action_color_map = {
            'Move': 'lightblue',
            'Pickup': 'lightgreen',
            'Dropoff': 'lightyellow',
            'Stop': 'lightcoral',
            'SpeedUp': 'lightpink',
            'START': 'lightgray'
        }
        action = frame['action']
        action_bg_color = action_color_map.get(action, 'lightgray')
        phase = frame.get('phase', 'observation')
        
        # Add phase indicator
        phase_indicator = {
            'decision': '🤔 DECIDING',
            'effect': '✓ EXECUTED',
            'observation': '👀 START'
        }.get(phase, '?')
        
        action_text = f"""{phase_indicator}

ACTION: {action.upper()}

Reward: {frame['reward']:+.1f}
"""
        ax.text(-0.8, 7.5, action_text, fontsize=13, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.8', facecolor=action_bg_color, 
                        edgecolor='black', linewidth=3, alpha=0.95),
               verticalalignment='center', horizontalalignment='right', family='monospace')
        
        # === METRICS PANEL (RIGHT SIDE) ===
        metrics_text = f"""STATE:
Passengers: {frame['passengers']}/50
Money: TSh {int(frame['money']):,}
Speed: {frame['speed']}/3
Fined: {'YES' if frame['fined'] else 'NO'}
Pos: ({frame['pos_x']}, {frame['pos_y']})
"""
        ax.text(15.8, 10, metrics_text, fontsize=11, verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.8', facecolor='wheat', 
                        edgecolor='black', linewidth=2, alpha=0.9),
               family='monospace', fontweight='bold')
        
        # === SAFETY STATUS (BOTTOM RIGHT) ===
        if frame['passengers'] <= 33 and not frame['fined']:
            status = "✓ SAFE"
            status_color = 'green'
            status_bg = 'lightgreen'
        elif frame['passengers'] <= 40:
            status = "⚠ WARNING"
            status_color = 'orange'
            status_bg = 'lightyellow'
        else:
            status = "✗ OVERLOAD"
            status_color = 'darkred'
            status_bg = 'lightcoral'
        
        ax.text(15.8, 2, status, fontsize=14, fontweight='bold', color=status_color,
               bbox=dict(boxstyle='round,pad=0.8', facecolor=status_bg, 
                        edgecolor='black', linewidth=2, alpha=0.9),
               verticalalignment='center', horizontalalignment='right')
        
        # Add legend
        legend_text = """LEGEND:
🟡 = High-Demand Stop
🔴 = Police Checkpoint
🟢/🔴 = Traffic Light
"""
        ax.text(-0.8, -0.5, legend_text, fontsize=9,
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                        edgecolor='black', linewidth=1, alpha=0.8),
               verticalalignment='top', horizontalalignment='right', family='monospace')
    
    # Create animation - EXTREMELY SLOW: 1000ms per frame = 1 FPS
    # This gives ~5-10 minutes for a typical episode - SUPER DETAILED
    anim = animation.FuncAnimation(fig, animate, frames=len(frames), 
                                   interval=1000, repeat=True, repeat_delay=5000)
    
    # Save GIF
    output_path = f"agent_demo_{algo_name.lower()}_slow.gif"
    try:
        anim.save(output_path, writer='pillow', fps=1)
        print(f"\n✓ GIF saved successfully: {output_path}")
        print(f"  Frames: {len(frames)}")
        print(f"  Speed: 1 FPS (1000ms per frame) - ULTRA SLOW for maximum detail")
        print(f"  Duration: ~{len(frames)} seconds (~{len(frames)/60:.1f} minutes)")
        print(f"  Total Reward: {total_reward:+.2f}")
        print(f"  Final Passengers: {final_passengers}/50")
        print(f"  Legal Completion: {'Yes' if final_passengers <= 33 and not was_fined else 'No'}")
    except Exception as e:
        print(f"✗ Failed to save GIF: {e}")
    
    plt.close(fig)

def main():
    print("\n" + "="*80)
    print("AGENT PERFORMANCE RECORDER - GIF GENERATION")
    print("="*80)
    print("\nThis script records an agent's episode and saves it as an animated GIF")
    print("The GIF plays at 10 FPS (100ms per frame) so you can see every action clearly")
    
    # Choose model
    result = choose_model()
    if result is None:
        return
    
    algo_name, model_path, model_class = result
    
    # Load model
    model = load_model(algo_name, model_path, model_class)
    if model is None:
        return
    
    # Create environment
    env = DaladalaEnv(render_mode=None)  # No real-time rendering
    
    print(f"\nRunning episode with {algo_name}...")
    print("This may take a moment as frames are collected...")
    
    # Run episode and collect frames
    frames, total_reward, final_passengers, was_fined = run_episode(env, model, algo_name)
    
    env.close()
    
    # Create GIF
    create_gif(frames, algo_name, total_reward, final_passengers, was_fined)
    
    print("\n" + "="*80)
    print("✓ Recording complete!")
    print("="*80)

if __name__ == "__main__":
    main()
