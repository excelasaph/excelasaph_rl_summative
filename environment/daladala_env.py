# environment/daladala_env.py
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from environment.rendering import render_frame

class DaladalaEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 12}

    def __init__(self, render_mode=None):
        super().__init__()
        self.observation_space = spaces.Box(-1, 1, shape=(14,), dtype=np.float32)
        self.action_space = spaces.Discrete(5)  # 0:Move, 1:Pickup, 2:Dropoff, 3:Stop, 4:SpeedUp
        self.render_mode = render_mode

        # Fixed route Ubungo → Posta (right then up)
        self.route = [(x, 14) for x in range(15)] + [(14, y) for y in range(13, -1, -1)]
        self.high_demand_stops = [(4,14), (8,14), (14,8), (14,3)]
        
        # These will be randomized each reset
        self.police_checkpoints = []
        self.traffic_lights = []
        self.traffic_light_states = {}  # Stores state (Red=1, Green=0) for each light
        
        # Pools for randomization
        self.available_positions = [pos for pos in self.route if pos not in self.high_demand_stops]

        self.max_steps = 350
        self.physical_max = 50
        self.light_cycle = 0  # Track light cycle deterministically

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.step_count = 0
        self.passengers = 0
        self.money = 0.0
        self.pos_idx = 0
        self.speed = 0
        self.fined = False
        self.light_cycle = 0
        
        # Randomize hazard positions each episode
        available = [pos for pos in self.route if pos not in self.high_demand_stops]
        if len(available) >= 7:  # 3 police + 4 traffic lights
            sampled = np.random.choice(len(available), 7, replace=False)
            self.police_checkpoints = [available[i] for i in sampled[:3]]
            self.traffic_lights = [available[i] for i in sampled[3:7]]
            
            # Assign random constant state (Red=1, Green=0) for each light this episode
            # This ensures the light stays the same throughout the episode
            self.traffic_light_states = {pos: np.random.randint(0, 2) for pos in self.traffic_lights}
        
        # Initialize deterministic passenger counts per stop (seeded by position)
        self.passengers_at_stop = {}
        for stop in self.high_demand_stops:
            # Deterministic: same stop always has same initial count
            seed_val = hash(stop) % 11  # 0-10 passengers
            self.passengers_at_stop[stop] = seed_val
        
        return self._get_obs(), {}

    def _get_obs(self):
        """
        Generate observation based on current location and environment state.
        Observations are DETERMINISTIC per location to match training/visualization.
        """
        if self.pos_idx >= len(self.route):
            x, y = 14, 0
        else:
            x, y = self.route[self.pos_idx]

        # === CURRENT LOCATION HAZARDS ===
        # Traffic light: Constant state for this episode (Red=1, Green=0)
        light_is_red = self.traffic_light_states.get((x, y), 0)
        
        # Police checkpoint detection
        police_here = 1 if (x, y) in self.police_checkpoints else 0
        
        # Must stop at THIS location?
        must_stop_now = 1 if (light_is_red or police_here) else 0
        
        # === NEXT LOCATION HAZARDS ===
        next_idx = min(self.pos_idx + 1, len(self.route) - 1)
        next_x, next_y = self.route[next_idx]
        
        # Check what's ahead
        next_light_is_red = self.traffic_light_states.get((next_x, next_y), 0)
        police_ahead = 1 if (next_x, next_y) in self.police_checkpoints else 0
        must_stop_next = 1 if (next_light_is_red or police_ahead) else 0
        
        # === PASSENGER STATE ===
        # At high-demand stop: passengers waiting (deterministic)
        at_stop = 1 if (x, y) in self.high_demand_stops else 0
        passengers_waiting = self.passengers_at_stop.get((x, y), 0) if at_stop else 0
        
        # === DISTANCE AHEAD (for lookahead) ===
        # Distance to next traffic light (in next 5 cells)
        dist_to_light = 5
        for i in range(self.pos_idx + 1, min(self.pos_idx + 6, len(self.route))):
            if self.route[i] in self.traffic_lights:
                dist_to_light = i - self.pos_idx
                break
        
        # Distance to next police (in next 5 cells)
        dist_to_police = 5
        for i in range(self.pos_idx + 1, min(self.pos_idx + 6, len(self.route))):
            if self.route[i] in self.police_checkpoints:
                dist_to_police = i - self.pos_idx
                break
        
        # === BUILD OBSERVATION VECTOR (all normalized to [-1, 1]) ===
        obs = np.array([
            x / 14.0 * 2 - 1,                      # [0] position_x
            y / 14.0 * 2 - 1,                      # [1] position_y
            self.passengers / self.physical_max * 2 - 1,  # [2] current_passengers
            self.money / 150000.0 * 2 - 1,        # [3] money_earned
            self.speed / 3.0 * 2 - 1,              # [4] current_speed
            light_is_red * 2 - 1,                  # [5] light_is_red_HERE (critical)
            police_here * 2 - 1,                   # [6] police_checkpoint_HERE
            must_stop_now * 2 - 1,                 # [7] must_stop_now_HERE (critical)
            at_stop * 2 - 1,                       # [8] at_high_demand_stop
            passengers_waiting / 10.0 * 2 - 1,    # [9] passengers_waiting_at_stop
            must_stop_next * 2 - 1,                # [10] must_stop_next_location
            dist_to_light / 5.0 * 2 - 1,          # [11] distance_to_traffic_light
            dist_to_police / 5.0 * 2 - 1,         # [12] distance_to_police
            self.step_count / self.max_steps * 2 - 1,  # [13] episode_progress
        ], dtype=np.float32)
        
        return obs

    def step(self, action):
        """
        Action: 0=Move, 1=Pickup, 2=Dropoff, 3=Stop, 4=SpeedUp
        Movement is ALWAYS automatic. Actions are overlaid on movement.
        Rewards guide agent toward optimal actions based on current state.
        """
        self.step_count += 1
        self.light_cycle += 1  # Update traffic light cycle
        
        terminated = truncated = False
        x, y = self.route[self.pos_idx]
        
        # === PHASE 1: AUTOMATIC MOVEMENT (always happens) ===
        if self.pos_idx < len(self.route) - 1:
            self.pos_idx += 1
        else:
            terminated = True
        
        # === PHASE 2: EXECUTE ACTION ===
        reward = 0.0
        
        # Observe the CURRENT location (before action)
        light_is_red = self.traffic_light_states.get((x, y), 0)
        police_here = 1 if (x, y) in self.police_checkpoints else 0
        must_stop_here = 1 if (light_is_red or police_here) else 0
        at_stop = 1 if (x, y) in self.high_demand_stops else 0
        
        # === INTELLIGENT REWARD SYSTEM ===
        # We know the "right" action for each state, so rewards guide strongly
        
        if action == 0:  # MOVE action (advance to next cell)
            # Movement already happened automatically
            # This action is mostly for consistency; reward small progress bonus
            reward += 2
            
            # PENALTY: Moved through hazard without stopping
            if must_stop_here:
                reward -= 40  # Heavy penalty: ran through red light or police checkpoint
        
        elif action == 1:  # PICKUP action
            if at_stop and self.passengers < self.physical_max:
                # GOOD: Picking up at a stop
                base_add = max(3, self.passengers_at_stop.get((x, y), 0))
                add = min(base_add, self.physical_max - self.passengers)
                self.passengers += add
                reward += 15  # High reward for correct action
                
                # Deduct waiting passengers
                if (x, y) in self.passengers_at_stop:
                    self.passengers_at_stop[(x, y)] = max(0, self.passengers_at_stop[(x, y)] - add)
            else:
                # BAD: Picked up when not at stop
                reward -= 5
            
            # PENALTY: Picking up at hazard zone
            if must_stop_here:
                reward -= 10
        
        elif action == 2:  # DROPOFF action
            if at_stop and self.passengers > 0:
                # GOOD: Dropping off at a stop
                drop = min(self.passengers, max(3, self.passengers // 2 + 1))
                self.passengers -= drop
                self.money += drop * 1000
                reward += 12  # Good reward for revenue
            else:
                # BAD: Dropped off when not at stop
                reward -= 8
            
            # PENALTY: Dropping off at hazard zone
            if must_stop_here:
                reward -= 10
        
        elif action == 3:  # STOP action (slows down / waits)
            self.speed = max(0, self.speed - 1)
            
            # GOOD: Stopped at hazard location
            if must_stop_here:
                reward += 25  # Strong reward: correct safety action
            else:
                # BAD: Unnecessary stop
                reward -= 3
        
        elif action == 4:  # SPEEDUP action
            # GOOD: Speeding up in safe zones
            if not must_stop_here and self.passengers <= 40:
                self.speed = min(self.speed + 1, 3)
                reward += 3
            else:
                # BAD: Speeding in danger or when overloaded
                if must_stop_here:
                    reward -= 15  # Dangerous
                if self.passengers > 40:
                    reward -= 30  # Could crash
                    terminated = True  # Crash!
        
        # === PHASE 3: SAFETY VIOLATIONS ===
        # Check destination after automatic movement
        new_x, new_y = self.route[self.pos_idx] if self.pos_idx < len(self.route) else (14, 0)
        
        # Police checkpoint consequences
        if (new_x, new_y) in self.police_checkpoints:
            if self.passengers > 40:
                reward -= 50  # Severe: overloaded at police
                self.fined = True
                terminated = True
            elif self.passengers > 33:
                reward -= 20  # Violation: illegal capacity
                self.fined = True
        
        # === PHASE 4: PROGRESS & COMPLETION ===
        # Base movement reward (small, to encourage progress)
        reward += 1
        
        # Destination completion bonus
        if terminated:
            reward += 100  # Large bonus for reaching destination
            if self.passengers <= 33 and not self.fined:
                reward += 50  # Bonus for legal completion
        
        # === PHASE 5: STATE UPDATES ===
        truncated = self.step_count >= self.max_steps
        
        # === RENDER ===
        if self.render_mode:
            render_frame(self, action, reward)
        
        return self._get_obs(), reward, terminated, truncated, {}

    def render(self):
        if self.render_mode == "rgb_array":
            return render_frame(self, None, 0, rgb=True)