"""
Random Action Demonstration
Shows the environment visualization with random agent actions (no RL training).
Generates an animated GIF of the daladala traversing the route with random decisions.

This demonstrates the environment without any trained model - purely random exploration.
Useful for understanding environment mechanics and visualization quality.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle
from environment import DaladalaEnv

def run_random_episode(env):
    """Run one episode with random actions and collect frame data."""
    frames = []
    obs, _ = env.reset()

    # Force 2 Red, 2 Green traffic lights for better visualization variety
    if len(env.traffic_lights) >= 4:
        states = [1, 1, 0, 0]  # 2 Reds, 2 Greens
        np.random.shuffle(states)
        for i, light_pos in enumerate(env.traffic_lights[:4]):
            env.traffic_light_states[light_pos] = states[i]

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
        'traffic_light_states': env.traffic_light_states.copy() if hasattr(env, 'traffic_light_states') else {},
        'high_demand_stops': env.high_demand_stops,
        'action': "START",
        'action_id': -1,
        'reward': 0.0,
        'light_cycle': env.light_cycle,
        'phase': 'observation',
    }
    frames.append(frame_data)
    
    while True:
        # PHASE 1: DECISION FRAME
        # Random action
        action = env.action_space.sample()
        
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
            'traffic_light_states': env.traffic_light_states.copy() if hasattr(env, 'traffic_light_states') else {},
            'high_demand_stops': env.high_demand_stops,
            'action': action_names[action],
            'action_id': action,
            'reward': 0.0,
            'light_cycle': env.light_cycle,
            'phase': 'decision',
        }
        frames.append(decision_frame)
        
        # PHASE 2: EXECUTE ACTION
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Add effect frame
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
            'traffic_light_states': env.traffic_light_states.copy() if hasattr(env, 'traffic_light_states') else {},
            'high_demand_stops': env.high_demand_stops,
            'action': action_names[action],
            'action_id': action,
            'reward': reward,
            'light_cycle': env.light_cycle,
            'phase': 'effect',
        }
        frames.append(effect_frame)
        
        total_reward += reward
        step += 1
        
        if terminated or truncated:
            break
            
    return frames, total_reward, env.passengers, env.fined

def create_gif(frames, total_reward, final_passengers, was_fined):
    """Create animated GIF from frame data (Visual style from record_agent_demo.py)."""
    print(f"\n✓ Episode complete! Creating GIF with {len(frames)} frames...")
    
    # Create figure with larger size for better visibility
    fig, ax = plt.subplots(figsize=(14, 12))
    
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
        
        # Draw traffic lights
        for tx, ty in frame['traffic_lights']:
            if 'traffic_light_states' in frame and frame['traffic_light_states']:
                is_red = frame['traffic_light_states'].get((tx, ty), 1) == 1
            else:
                is_red = (frame['light_cycle'] % 2 == 0)
                
            light_color = 'red' if is_red else 'green'
            circle = Circle((tx, ty), 0.3, color=light_color, ec='black', linewidth=2)
            ax.add_patch(circle)
        
        # Draw agent (bus)
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
        ax.set_title(f'Random Agent - Episode Analysis\nStep {frame["step"]}/350', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('X Position', fontsize=12, fontweight='bold')
        ax.set_ylabel('Y Position', fontsize=12, fontweight='bold')
        
        # === ACTION PANEL ===
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
        
        # === METRICS PANEL ===
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
        
        # === SAFETY STATUS ===
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
    
    # Create animation
    target_duration = 30.0
    n_frames = len(frames)
    fps = max(1, n_frames / target_duration)
    interval = 1000 / fps
    
    anim = animation.FuncAnimation(fig, animate, frames=n_frames, 
                                   interval=interval, repeat=True, repeat_delay=2000)
    
    # Save GIF
    output_path = "random_demo.gif"
    try:
        anim.save(output_path, writer='pillow', fps=fps)
        print(f"\n✓ GIF saved successfully: {output_path}")
        print(f"  Frames: {n_frames}")
        print(f"  Target Duration: {target_duration}s")
        print(f"  Calculated FPS: {fps:.2f}")
        print(f"  Total Reward: {total_reward:+.2f}")
    except Exception as e:
        print(f"✗ Failed to save GIF: {e}")
    
    plt.close(fig)

def main():
    print("\n" + "="*80)
    print("RANDOM AGENT DEMO - Environment Visualization")
    print("="*80)
    print("\nThis generates a GIF showing the environment with random agent actions.")
    print("No RL training involved - purely for visualization purposes.\n")
    
    # Create environment
    env = DaladalaEnv(render_mode=None)
    
    print("Running random episode...")
    frames, total_reward, final_passengers, was_fined = run_random_episode(env)
    
    env.close()
    
    # Create GIF
    create_gif(frames, total_reward, final_passengers, was_fined)
    
    print("\n" + "="*80)
    print("✓ Random demo complete!")
    print("="*80)

if __name__ == "__main__":
    main()

