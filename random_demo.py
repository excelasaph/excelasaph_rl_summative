# random_demo.py
"""
Random Action Demonstration
Shows the environment visualization with random agent actions (no RL training).
Generates an animated GIF of the daladala traversing the route with random decisions.

This demonstrates the environment without any trained model - purely random exploration.
Useful for understanding environment mechanics and visualization quality.
"""

import imageio
from environment import DaladalaEnv
from environment.rendering import render_frame

print("\n" + "="*70)
print("RANDOM AGENT DEMO - Environment Visualization")
print("="*70)
print("\nThis generates a GIF showing the environment with random agent actions.")
print("No RL training involved - purely for visualization purposes.\n")

env = DaladalaEnv(render_mode="rgb_array")
images = []
obs, _ = env.reset()

total_reward = 0
action_counts = [0, 0, 0, 0, 0]
step_count = 0

print("Recording episode frames...")
while True:
    # Sample random action from action space
    action = env.action_space.sample()
    action_counts[action] += 1
    obs, reward, terminated, truncated, _ = env.step(action)
    total_reward += reward
    step_count += 1
    
    # Capture frame with rendering
    frame = render_frame(env, action, reward, rgb=True)
    images.append(frame)
    
    if step_count % 50 == 0:
        action_names = ["Forward", "Stop", "Pick Up", "Drop Off", "Speed Up"]
        print(f"  Step {step_count:3d} | Passengers: {env.passengers:2d} | "
              f"Money: TSh {int(env.money):7,d} | Reward: {reward:+6.2f} | "
              f"Action: {action_names[action]}")
    
    if terminated or truncated:
        print(f"\nEpisode ended at step {step_count}")
        print(f"  Final passengers: {env.passengers}")
        print(f"  Total reward: {total_reward:+.1f}")
        break

print(f"\nTotal frames captured: {len(images)}")

# Save animation
print("Saving animation to random_demo.gif...")
try:
    imageio.mimsave("random_demo.gif", images, fps=12)
    print("✓ random_demo.gif created successfully!")
    print(f"  File size: {len(images)} frames at 12 FPS")
except Exception as e:
    print(f"✗ Failed to save GIF: {e}")
    print("  Ensure imageio and imageio-ffmpeg are installed")

# Statistics
print("\n" + "-"*70)
print("Random Agent Statistics:")
print("-"*70)
action_names = ["Forward", "Stop", "Pick Up", "Drop Off", "Speed Up"]
for i, (action_name, count) in enumerate(zip(action_names, action_counts)):
    percentage = (count / step_count) * 100 if step_count > 0 else 0
    print(f"  {action_name:<12}: {count:3d} times ({percentage:5.1f}%)")
print(f"\n  Total steps: {step_count}")
print(f"  Average passengers: {env.passengers if terminated or truncated else 'N/A'}")

env.close()
print("\n✓ Random demo complete!")

