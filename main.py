# main.py
"""
Run any trained RL agent in the Daladala environment.
Displays real-time visualization with verbose console output.

This script lets you choose which algorithm (DQN, PPO, A2C, REINFORCE) to run.
Shows the agent's decision-making process and performance metrics.
"""

import pygame
import numpy as np
import math
import time
import os
import torch
from stable_baselines3 import DQN, PPO, A2C
from environment import DaladalaEnv
from training.reinforce_training import PolicyNetwork

# ============================================================================
# CONFIGURATION
# ============================================================================
WINDOW_SIZE = 600
HUD_HEIGHT = 120
GRID_SIZE = 15
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
FPS = 60
STEP_DELAY = 0.5

# COLORS
COLOR_ROAD = (50, 50, 50)
COLOR_GRASS = (34, 139, 34)
COLOR_SAND = (194, 178, 128)
COLOR_MARKING = (255, 255, 255)
COLOR_BUS_BODY = (255, 215, 0)
COLOR_BUS_STRIPE = (0, 100, 0)
COLOR_POLICE_BLUE = (0, 0, 139)
COLOR_POLICE_WHITE = (255, 255, 255)
COLOR_STOP_SIGN = (200, 0, 0)

class RealisticRenderer:
    def __init__(self, env):
        self.env = env
        pygame.init()
        # Create a resizable window
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + HUD_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Daladala Agent - Realistic View")
        self.clock = pygame.time.Clock()
        
        # Create a fixed-size canvas for drawing
        self.canvas = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE + HUD_HEIGHT))
        
        # Fonts
        self.font_title = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_hud = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 12)
        
        # Pre-calculate road path for drawing
        self.road_rects = []
        for x, y in env.route:
            px = x * CELL_SIZE
            py = WINDOW_SIZE - (y + 1) * CELL_SIZE
            self.road_rects.append(pygame.Rect(px, py, CELL_SIZE, CELL_SIZE))

    def to_screen_coords(self, grid_x, grid_y):
        """Convert grid coordinates to screen coordinates (center of cell)."""
        px = grid_x * CELL_SIZE + CELL_SIZE // 2
        py = WINDOW_SIZE - (grid_y + 1) * CELL_SIZE + CELL_SIZE // 2
        return px, py

    def draw_road(self):
        """Draw the road network with markings."""
        self.canvas.fill(COLOR_SAND)
        
        # Draw road segments
        for rect in self.road_rects:
            pygame.draw.rect(self.canvas, COLOR_ROAD, rect)
            
        # Draw lane markings (dashed lines)
        for i, (x, y) in enumerate(self.env.route):
            if i == len(self.env.route) - 1: continue
            
            px, py = self.to_screen_coords(x, y)
            next_x, next_y = self.env.route[i+1]
            npx, npy = self.to_screen_coords(next_x, next_y)
            
            pygame.draw.line(self.canvas, COLOR_MARKING, (px, py), (npx, npy), 2)

    def draw_bus(self, grid_x, grid_y, passengers):
        """Draw a detailed Daladala bus."""
        cx, cy = self.to_screen_coords(grid_x, grid_y)
        w, h = int(CELL_SIZE * 0.8), int(CELL_SIZE * 0.6)
        
        angle = 0
        if grid_y == 14 and grid_x < 14:
            angle = 0 # Facing Right
        elif grid_x == 14:
            angle = -90 # Facing Down
            
        bus_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        pygame.draw.rect(bus_surf, COLOR_BUS_BODY, (0, 0, w, h), border_radius=5)
        pygame.draw.rect(bus_surf, COLOR_BUS_STRIPE, (0, h//3, w, h//3))
        pygame.draw.rect(bus_surf, (200, 240, 255), (w*0.1, h*0.1, w*0.2, h*0.2))
        pygame.draw.rect(bus_surf, (50, 50, 50), (w*0.4, h*0.1, w*0.5, h*0.2))
        pygame.draw.circle(bus_surf, (0,0,0), (int(w*0.2), h), 4)
        pygame.draw.circle(bus_surf, (0,0,0), (int(w*0.8), h), 4)
        pygame.draw.circle(bus_surf, (0,0,0), (int(w*0.2), 0), 4)
        pygame.draw.circle(bus_surf, (0,0,0), (int(w*0.8), 0), 4)
        
        rotated_bus = pygame.transform.rotate(bus_surf, angle)
        rect = rotated_bus.get_rect(center=(cx, cy))
        self.canvas.blit(rotated_bus, rect)
        
        badge_color = (0, 200, 0) if passengers <= 33 else (255, 165, 0) if passengers <= 40 else (255, 0, 0)
        pygame.draw.circle(self.canvas, badge_color, (cx, cy - 15), 10)
        pygame.draw.circle(self.canvas, (255,255,255), (cx, cy - 15), 10, 1)
        text = self.font_small.render(str(passengers), True, (255, 255, 255))
        text_rect = text.get_rect(center=(cx, cy - 15))
        self.canvas.blit(text, text_rect)

    def draw_police(self, grid_x, grid_y):
        """Draw a police car/checkpoint."""
        cx, cy = self.to_screen_coords(grid_x, grid_y)
        
        w, h = int(CELL_SIZE * 0.7), int(CELL_SIZE * 0.4)
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (cx, cy + CELL_SIZE//3)
        
        pygame.draw.rect(self.canvas, COLOR_POLICE_WHITE, rect, border_radius=3)
        pygame.draw.rect(self.canvas, COLOR_POLICE_BLUE, (rect.left, rect.top, w//3, h), border_top_left_radius=3, border_bottom_left_radius=3)
        pygame.draw.rect(self.canvas, COLOR_POLICE_BLUE, (rect.right - w//3, rect.top, w//3, h), border_top_right_radius=3, border_bottom_right_radius=3)
        
        if (pygame.time.get_ticks() // 200) % 2 == 0:
            pygame.draw.circle(self.canvas, (255, 0, 0), (cx - 5, cy), 4)
            pygame.draw.circle(self.canvas, (0, 0, 255), (cx + 5, cy), 4)
        else:
            pygame.draw.circle(self.canvas, (0, 0, 255), (cx - 5, cy), 4)
            pygame.draw.circle(self.canvas, (255, 0, 0), (cx + 5, cy), 4)
            
        text = self.font_small.render("POLICE", True, (255, 255, 255))
        self.canvas.blit(text, (cx - 15, cy + 10))

    def draw_traffic_light(self, grid_x, grid_y, is_red):
        """Draw a traffic light."""
        cx, cy = self.to_screen_coords(grid_x, grid_y)
        
        housing_rect = pygame.Rect(0, 0, 20, 40)
        housing_rect.center = (cx + CELL_SIZE//3, cy - CELL_SIZE//3)
        pygame.draw.rect(self.canvas, (20, 20, 20), housing_rect, border_radius=4)
        
        red_color = (255, 0, 0) if is_red else (50, 0, 0)
        green_color = (0, 255, 0) if not is_red else (0, 50, 0)
        
        pygame.draw.circle(self.canvas, red_color, (housing_rect.centerx, housing_rect.top + 10), 6)
        pygame.draw.circle(self.canvas, green_color, (housing_rect.centerx, housing_rect.bottom - 10), 6)

    def draw_stop(self, grid_x, grid_y, name):
        """Draw a bus stop."""
        cx, cy = self.to_screen_coords(grid_x, grid_y)
        
        pygame.draw.rect(self.canvas, (139, 69, 19), (cx - 15, cy - 25, 30, 10))
        pygame.draw.line(self.canvas, (100, 100, 100), (cx - 10, cy - 15), (cx - 10, cy + 10), 2)
        pygame.draw.line(self.canvas, (100, 100, 100), (cx + 10, cy - 15), (cx + 10, cy + 10), 2)
        
        text = self.font_small.render(name, True, (0, 0, 0))
        self.canvas.blit(text, (cx - 20, cy - 40))

    def draw_hud(self, step, passengers, money, speed, action, reward, fined, algo_name):
        """Draw the Heads-Up Display."""
        hud_rect = pygame.Rect(0, WINDOW_SIZE, WINDOW_SIZE, HUD_HEIGHT)
        pygame.draw.rect(self.canvas, (30, 30, 30), hud_rect)
        
        col1_x = 20
        col2_x = 250
        col3_x = 450
        
        # Column 1: Stats
        self.draw_text(f"STEP: {step}/350", col1_x, WINDOW_SIZE + 20, (200, 200, 200))
        self.draw_text(f"PASSENGERS: {passengers}/50", col1_x, WINDOW_SIZE + 50, 
                       (0, 255, 0) if passengers <= 33 else (255, 0, 0))
        self.draw_text(f"MONEY: TSh {int(money):,}", col1_x, WINDOW_SIZE + 80, (255, 215, 0))
        
        # Column 2: Action & Reward
        action_names = ["MOVE", "PICKUP", "DROPOFF", "STOP", "SPEED UP"]
        act_str = action_names[action] if action is not None and action < 5 else "START"
        self.draw_text(f"ACTION: {act_str}", col2_x, WINDOW_SIZE + 20, (255, 255, 255))
        self.draw_text(f"REWARD: {reward:+.1f}", col2_x, WINDOW_SIZE + 50, 
                       (0, 255, 0) if reward > 0 else (255, 0, 0))
        self.draw_text(f"SPEED: {speed}/3", col2_x, WINDOW_SIZE + 80, (100, 200, 255))
        
        # Column 3: Status & Model
        status = "LEGAL"
        color = (0, 255, 0)
        if fined:
            status = "FINED!"
            color = (255, 0, 0)
        elif passengers > 40:
            status = "DANGEROUS"
            color = (255, 0, 0)
        elif passengers > 33:
            status = "OVERLOADED"
            color = (255, 165, 0)
            
        self.draw_text(f"STATUS: {status}", col3_x, WINDOW_SIZE + 20, color)
        self.draw_text(f"MODEL: {algo_name}", col3_x, WINDOW_SIZE + 50, (200, 200, 255))
        self.draw_text("Running Agent...", col3_x, WINDOW_SIZE + 80, (150, 150, 150), font=self.font_small)

    def draw_text(self, text, x, y, color, font=None):
        if font is None: font = self.font_hud
        surf = font.render(text, True, color)
        self.canvas.blit(surf, (x, y))

    def render(self, action, reward, algo_name="Agent"):
        self.draw_road()
        
        stop_names = ["Ubungo", "Morocco", "Kariakoo", "Posta"]
        for i, (sx, sy) in enumerate(self.env.high_demand_stops):
            name = stop_names[i] if i < len(stop_names) else "Stop"
            self.draw_stop(sx, sy, name)
            
        for px, py in self.env.police_checkpoints:
            self.draw_police(px, py)
            
        for tx, ty in self.env.traffic_lights:
            is_red = self.env.traffic_light_states.get((tx, ty), 0)
            self.draw_traffic_light(tx, ty, is_red)
            
        if self.env.pos_idx < len(self.env.route):
            ax, ay = self.env.route[self.env.pos_idx]
            self.draw_bus(ax, ay, self.env.passengers)
            
        self.draw_hud(self.env.step_count, self.env.passengers, self.env.money, 
                      self.env.speed, action, reward, self.env.fined, algo_name)
        
        # Scale canvas to fit screen
        screen_w, screen_h = self.screen.get_size()
        canvas_w, canvas_h = self.canvas.get_size()
        
        # Calculate scale to fit while maintaining aspect ratio
        scale = min(screen_w / canvas_w, screen_h / canvas_h)
        new_w = int(canvas_w * scale)
        new_h = int(canvas_h * scale)
        
        scaled_surf = pygame.transform.scale(self.canvas, (new_w, new_h))
        
        # Center on screen
        x_pos = (screen_w - new_w) // 2
        y_pos = (screen_h - new_h) // 2
        
        self.screen.fill((0, 0, 0)) # Fill borders with black
        self.screen.blit(scaled_surf, (x_pos, y_pos))
        
        pygame.display.flip()

def choose_model():
    """Display menu and get user choice of algorithm."""
    print("\n" + "="*80)
    print("DALADALA AGENT - SELECT MODEL")
    print("="*80)
    
    algorithms = {
        "1": ("DQN", "models/dqn/best_dqn.zip", DQN),
        "2": ("PPO", "models/ppo/best_ppo.zip", PPO),
        "3": ("A2C", "models/a2c/best_a2c.zip", A2C),
        "4": ("REINFORCE", "models/reinforce/best_reinforce_policy.pth", None),
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
            # State dim: 14, Action dim: 5 (from environment specs)
            # Note: The best saved model uses hidden_dim=64 based on the checkpoint file
            model = PolicyNetwork(state_dim=14, action_dim=5, hidden_dim=64)
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
    
    # Disable internal rendering to prevent conflict
    env = DaladalaEnv(render_mode=None)
    renderer = RealisticRenderer(env)
    
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
    print(f">>> Rendering at {FPS} FPS with {STEP_DELAY}s delay per step")
    print(">>> Close the window when done\n")
    
    obs, info = env.reset()
    total_reward = 0
    episode_data = []
    last_action = None
    last_reward = 0.0
    
    running = True
    while running:
        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
        
        if not running:
            break

        # Get action from model
        action = predict_action(model, obs, algo_name)
        
        # Step environment
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        # Render frame
        renderer.render(action, reward, algo_name)
        
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
        
        # Delay for visibility
        time.sleep(STEP_DELAY)
        renderer.clock.tick(FPS)
        
        if terminated or truncated:
            break
    
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
    
    # Keep window open for a moment if finished
    if running:
        time.sleep(2)
    
    pygame.quit()
    env.close()

if __name__ == "__main__":
    main()