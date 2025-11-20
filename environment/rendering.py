# environment/rendering.py
"""
Advanced pygame rendering for the Daladala environment.
Provides real-time visualization of agent, hazards, and performance metrics.
"""

import pygame
import numpy as np

def render_frame(env, last_action, last_reward, rgb=False):
    """
    Render the current environment state.
    
    Args:
        env: DaladalaEnv instance
        last_action: Last action taken (0-4)
        last_reward: Reward from last step
        rgb: If True, return RGB array instead of displaying
    """
    if not hasattr(env, "screen"):
        pygame.init()
        size = 800  # Reduced from 1000 to fit better on screens
        env.screen = pygame.display.set_mode((size, size + 180))
        pygame.display.set_caption("Daladala RL Environment - Training Simulation")
        env.clock = pygame.time.Clock()
        env.font_large = pygame.font.SysFont("Arial", 20, bold=True)
        env.font_medium = pygame.font.SysFont("Arial", 16)
        env.font_small = pygame.font.SysFont("Arial", 12)
        
        # Bring window to focus (Windows-specific)
        import ctypes
        hwnd = pygame.display.get_surface()
        if hwnd:
            try:
                ctypes.windll.user32.SetForegroundWindow(pygame.display.get_wm_info()['window'])
            except:
                pass  # Fallback if method fails

    screen = env.screen
    screen.fill((245, 240, 220))  # Light cream background (road)

    cell = 800 // 15
    
    # Draw grid
    for i in range(16):
        pygame.draw.line(screen, (150, 140, 130), (i*cell, 0), (i*cell, 800), 1)
        pygame.draw.line(screen, (150, 140, 130), (0, i*cell), (800, i*cell), 1)

    # Draw route (emphasize the path)
    for x, y in env.route:
        pygame.draw.rect(screen, (200, 170, 120), (x*cell, y*cell, cell, cell))

    # ===== Draw Hazards =====
    
    # High demand stops (gold circles with label)
    for idx, (x, y) in enumerate(env.high_demand_stops):
        pygame.draw.circle(screen, (255, 215, 0), (int(x*cell + cell/2), int(y*cell + cell/2)), cell//3)
        pygame.draw.circle(screen, (184, 134, 11), (int(x*cell + cell/2), int(y*cell + cell/2)), cell//3, 3)
        # Label
        if idx == 0:
            label = "Ubungo"
        elif idx == 1:
            label = "Morocco"
        elif idx == 2:
            label = "Kariakoo"
        else:
            label = "Posta"
        txt = env.font_small.render(label, True, (0, 0, 0))
        screen.blit(txt, (x*cell + 10, y*cell + 5))

    # Police checkpoints (red squares with label)
    for x, y in env.police_checkpoints:
        pygame.draw.rect(screen, (200, 0, 0), (x*cell + 5, y*cell + 5, cell - 10, cell - 10))
        pygame.draw.rect(screen, (0, 0, 0), (x*cell + 5, y*cell + 5, cell - 10, cell - 10), 2)
        txt = env.font_small.render("POLICE", True, (255, 255, 255))
        screen.blit(txt, (x*cell + 10, y*cell + 20))

    # Traffic lights (dynamic color based on cycle)
    light_cycle = (env.step_count // 40) % 2
    for x, y in env.traffic_lights:
        if light_cycle == 0:  # Red
            color = (255, 0, 0)
            light_text = "🔴"
        else:  # Green
            color = (0, 200, 0)
            light_text = "🟢"
        
        pygame.draw.circle(screen, color, (int(x*cell + cell/2), int(y*cell + cell/2)), cell//3)
        pygame.draw.circle(screen, (0, 0, 0), (int(x*cell + cell/2), int(y*cell + cell/2)), cell//3, 2)
        txt = env.font_small.render("LIGHT", True, (255, 255, 255))
        screen.blit(txt, (x*cell + 15, y*cell + 20))

    # ===== Draw Agent (Daladala Bus) =====
    if env.pos_idx < len(env.route):
        dx, dy = env.route[env.pos_idx]
        # Main bus body
        pygame.draw.rect(screen, (34, 139, 34), (dx*cell + 5, dy*cell + 5, cell - 10, cell - 10))
        pygame.draw.rect(screen, (0, 0, 0), (dx*cell + 5, dy*cell + 5, cell - 10, cell - 10), 3)
        
        # Windows (indicate agent presence)
        pygame.draw.circle(screen, (173, 216, 230), (int(dx*cell + cell/3), int(dy*cell + cell/3)), 8)
        pygame.draw.circle(screen, (173, 216, 230), (int(dx*cell + 2*cell/3), int(dy*cell + cell/3)), 8)
        
        # Passenger count (in center)
        txt = env.font_large.render(str(env.passengers), True, (255, 255, 255))
        txt_rect = txt.get_rect(center=(int(dx*cell + cell/2), int(dy*cell + cell/2)))
        screen.blit(txt, txt_rect)
        
        # Overload warning
        if env.passengers > 40:
            pygame.draw.circle(screen, (255, 165, 0), (int(dx*cell + cell/2), int(dy*cell + cell/2)), cell//2, 4)

    # ===== HUD Panel =====
    hud_y = 1005
    
    # Background for HUD
    pygame.draw.rect(screen, (200, 200, 200), (0, hud_y - 5, 1000, 145))
    pygame.draw.line(screen, (0, 0, 0), (0, hud_y - 5), (1000, hud_y - 5), 2)

    # Left column
    hud_texts_left = [
        ("STEP", f"{env.step_count}/350", (0, 200, 0) if env.step_count < 300 else (200, 0, 0)),
        ("PASSENGERS", f"{env.passengers}/50", (0, 150, 0) if env.passengers <= 33 else (200, 100, 0) if env.passengers <= 40 else (200, 0, 0)),
        ("MONEY", f"TSh {int(env.money):,}", (0, 0, 200)),
    ]
    
    x_offset = 20
    for idx, (label, value, color) in enumerate(hud_texts_left):
        txt_label = env.font_medium.render(label, True, (0, 0, 0))
        txt_value = env.font_large.render(value, True, color)
        screen.blit(txt_label, (x_offset, hud_y + idx * 40))
        screen.blit(txt_value, (x_offset + 130, hud_y + idx * 40 - 5))
    
    # Right column
    action_names = ["Forward", "Stop", "Pick Up", "Drop Off", "Speed Up"]
    action_name = action_names[last_action] if last_action is not None and last_action < len(action_names) else "—"
    
    reward_color = (0, 150, 0) if last_reward > 0 else (150, 0, 0) if last_reward < 0 else (100, 100, 100)
    
    hud_texts_right = [
        ("ACTION", action_name, (0, 0, 0)),
        ("REWARD", f"{last_reward:+.1f}", reward_color),
        ("TOTAL", f"{getattr(env, '_total_reward', 0):+.1f}", (0, 100, 200)),
    ]
    
    x_offset = 450
    for idx, (label, value, color) in enumerate(hud_texts_right):
        txt_label = env.font_medium.render(label, True, (0, 0, 0))
        txt_value = env.font_large.render(value, True, color)
        screen.blit(txt_label, (x_offset, hud_y + idx * 40))
        screen.blit(txt_value, (x_offset + 130, hud_y + idx * 40 - 5))
    
    # Status indicators
    status_x = 820
    safety_status = "✓ SAFE" if not env.fined and env.passengers <= 33 else "⚠ WARNING" if env.passengers <= 40 else "✗ OVERLOAD"
    safety_color = (0, 200, 0) if not env.fined and env.passengers <= 33 else (200, 100, 0) if env.passengers <= 40 else (200, 0, 0)
    txt_status = env.font_medium.render(safety_status, True, safety_color)
    screen.blit(txt_status, (status_x, hud_y + 10))

    if rgb:
        return np.transpose(pygame.surfarray.array3d(screen), axes=(1, 0, 2))
    
    pygame.display.flip()
    env.clock.tick(2)  # 2 FPS = 500ms per frame (easy to follow)
