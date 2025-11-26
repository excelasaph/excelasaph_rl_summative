"""
Flask API Server for Daladala RL Environment
Exposes trained models via REST API for web/Unity visualization
Real-time WebSocket support for 3D rendering
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, disconnect
import os
import numpy as np
from stable_baselines3 import DQN, PPO, A2C
from environment import DaladalaEnv
import torch
import torch.nn as nn
import json

# ============================================================================
# CUSTOM POLICY CLASS FOR REINFORCE
# ============================================================================
class ReinforcePolicy(nn.Module):
    def __init__(self, hidden_size=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(14, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 5),
            nn.Softmax(dim=-1)
        )

    def forward(self, x):
        return self.net(x)

# ============================================================================
# COMPATIBILITY FIX: Handle older model files with missing schedule classes
# ============================================================================
# These are placeholder classes for deserialization of older model files
class FloatSchedule:
    """Placeholder for FloatSchedule from older stable-baselines3 versions"""
    def __init__(self, x):
        self.x = x
    def __call__(self, fraction):
        return self.x

class LinearSchedule:
    """Placeholder for LinearSchedule from older stable-baselines3 versions"""
    def __init__(self, initial_value, final_value=None):
        self.initial_value = initial_value
        self.final_value = final_value if final_value is not None else 0
    def __call__(self, fraction):
        return self.initial_value

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for web frontend

# Initialize WebSocket support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
env = None
model = None
current_algo = None
episode_data = {
    'step': 0,
    'total_reward': 0.0,
    'episode_history': []
}

# WebSocket connection tracking
connected_clients = set()
is_streaming = False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_model(algo_name, model_path):
    """Load a trained model based on algorithm."""
    global model, current_algo, env
    
    if not os.path.exists(model_path):
        return False, f"Model not found: {model_path}"
    
    try:
        # Custom objects for deserializing older model files
        custom_objects = {
            'FloatSchedule': FloatSchedule,
            'LinearSchedule': LinearSchedule,
        }
        
        if algo_name == "REINFORCE":
            # Load the custom PyTorch model
            # Architecture matches the saved checkpoint: Input 14 -> Hidden 64 -> Output 5
            model = ReinforcePolicy(hidden_size=64)
            model.load_state_dict(torch.load(model_path))
            model.eval()
        elif algo_name == "DQN":
            # Load with force_reset to ignore optimizer state mismatches
            model = DQN.load(model_path, custom_objects=custom_objects, env=None, device='cpu')
        elif algo_name == "PPO":
            model = PPO.load(model_path, custom_objects=custom_objects, env=None, device='cpu')
        elif algo_name == "A2C":
            model = A2C.load(model_path, custom_objects=custom_objects, env=None, device='cpu')
        else:
            return False, f"Unknown algorithm: {algo_name}"
        
        current_algo = algo_name
        return True, f"{algo_name} model loaded successfully"
    
    except Exception as e:
        import traceback
        print(f"Error loading model: {e}")
        print(traceback.format_exc())
        return False, f"Error loading model: {str(e)}"

def predict_action(obs):
    """Get action from current model."""
    if model is None:
        return None, "No model loaded"
    
    try:
        if current_algo == "REINFORCE":
            obs_tensor = torch.from_numpy(obs).float()
            with torch.no_grad():
                probs = model(obs_tensor)
                action = torch.argmax(probs).item()
        else:
            action, _ = model.predict(obs, deterministic=True)
            action = int(action) if isinstance(action, np.ndarray) else action
        
        return action, None
    except Exception as e:
        return None, f"Error predicting action: {str(e)}"

def env_state_to_dict():
    """Convert environment state to JSON-serializable dict."""
    if env is None:
        return {}
    
    # Get agent position
    pos_x = int(env.route[env.pos_idx][0]) if env.pos_idx < len(env.route) else 14
    pos_y = int(env.route[env.pos_idx][1]) if env.pos_idx < len(env.route) else 0
    
    # Build hazards array with [x, y, type]
    hazards = []
    for checkpoint in env.police_checkpoints:
        hazards.append([int(checkpoint[0]), int(checkpoint[1]), 'police'])
    for light in env.traffic_lights:
        hazards.append([int(light[0]), int(light[1]), 'trafficLight'])
    
    # Check current hazard states
    current_pos = (pos_x, pos_y)
    # Use the environment's static traffic light state
    light_red = int(env.traffic_light_states.get(current_pos, 0))
    police_here = int(1 if current_pos in env.police_checkpoints else 0)
    must_stop = int(1 if (light_red or police_here) else 0)
    
    return {
        'step': int(env.step_count),
        'x': pos_x,
        'y': pos_y,
        'pos_x': pos_x,
        'pos_y': pos_y,
        'position': [pos_x, pos_y],
        'passengers': int(env.passengers),
        'capacity': int(env.physical_max),
        'money': float(env.money),
        'speed': float(env.speed),
        'fined': int(env.fined),
        'light_red': light_red,
        'police_here': police_here,
        'must_stop': must_stop,
        'hazards': hazards,
        'police_checkpoints': [[int(cp[0]), int(cp[1])] for cp in env.police_checkpoints],
        'traffic_lights': [[int(tl[0]), int(tl[1])] for tl in env.traffic_lights],
        # Send the full traffic light state map to the frontend
        'traffic_light_states': {f"{k[0]},{k[1]}": int(v) for k, v in env.traffic_light_states.items()},
        'high_demand_stops': [[int(hs[0]), int(hs[1])] for hs in env.high_demand_stops],
        'light_cycle': int(env.light_cycle),
    }

# ============================================================================
# WEBSOCKET EVENT HANDLERS
# ============================================================================

def emit_rl_state():
    """Emit current RL state to all connected WebSocket clients."""
    if env is None:
        return
    
    try:
        state_data = env_state_to_dict()
        state_data['episode'] = episode_data['step'] // 350 + 1
        state_data['total_reward'] = episode_data['total_reward']
        state_data['action'] = episode_data.get('last_action', 0)
        state_data['reward'] = episode_data.get('last_reward', 0)
        state_data['terminated'] = episode_data.get('terminated', False)
        
        socketio.emit('rl-update', {
            'type': 'state-update',
            'data': state_data,
            'timestamp': len(connected_clients)
        }, skip_sid=None, namespace='/')
    except Exception as e:
        print(f"Error emitting RL state: {str(e)}")

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket client connection."""
    connected_clients.add(request.sid)
    print(f"✓ Client connected: {request.sid} (Total: {len(connected_clients)})")
    
    # Send initial status
    emit('connection-status', {
        'status': 'connected',
        'model_loaded': model is not None,
        'env_ready': env is not None,
        'algorithm': current_algo
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket client disconnection."""
    connected_clients.discard(request.sid)
    print(f"✗ Client disconnected: {request.sid} (Total: {len(connected_clients)})")

@socketio.on('start-episode')
def handle_start_episode():
    """Start a new RL episode."""
    global env, episode_data
    
    if env is None:
        emit('error', {'message': 'No model loaded'})
        return
    
    try:
        obs, info = env.reset()
        episode_data = {
            'step': 0,
            'total_reward': 0.0,
            'episode_history': [],
            'terminated': False,
            'last_action': 0,
            'last_reward': 0
        }
        
        # Send initial state
        emit_rl_state()
        
        emit('episode-started', {
            'status': 'success',
            'episode': episode_data['step'] // 350 + 1
        })
        print(f"✓ Episode started for client {request.sid}")
    except Exception as e:
        emit('error', {'message': f'Failed to start episode: {str(e)}'})
        print(f"✗ Error starting episode: {str(e)}")

@socketio.on('step')
def handle_step(data):
    """Execute one step in the environment."""
    global env, model, episode_data
    
    if env is None or model is None:
        emit('error', {'message': 'Model not loaded'})
        return
    
    try:
        action = data.get('action')
        if action is None:
            # Agent decides action automatically
            obs_tensor = torch.FloatTensor(env._get_obs()).unsqueeze(0)
            with torch.no_grad():
                if current_algo == "REINFORCE":
                    probs = model(obs_tensor)
                    action = torch.argmax(probs).item()
                else:
                    action, _ = model.predict(env._get_obs())
        
        # Execute step
        obs, reward, terminated, truncated, info = env.step(int(action))
        
        # Update episode data
        episode_data['step'] += 1
        episode_data['total_reward'] += reward
        episode_data['last_action'] = int(action)
        episode_data['last_reward'] = float(reward)
        episode_data['terminated'] = terminated or truncated
        episode_data['episode_history'].append({
            'step': episode_data['step'],
            'action': int(action),
            'reward': float(reward)
        })
        
        # Emit updated state
        emit_rl_state()
        
        # Emit episode complete if terminated
        if terminated or truncated:
            emit('episode-complete', {
                'status': 'completed',
                'total_reward': episode_data['total_reward'],
                'steps': episode_data['step'],
                'reason': 'terminated' if terminated else 'truncated'
            })
            print(f"✓ Episode completed. Reward: {episode_data['total_reward']:.2f}")
    
    except Exception as e:
        emit('error', {'message': f'Step failed: {str(e)}'})
        print(f"✗ Error during step: {str(e)}")

@socketio.on('reset')
def handle_reset():
    """Reset the environment for a new episode."""
    global env, episode_data
    
    if env is None:
        emit('error', {'message': 'Environment not initialized'})
        return
    
    try:
        obs, info = env.reset()
        episode_data = {
            'step': 0,
            'total_reward': 0.0,
            'episode_history': [],
            'terminated': False,
            'last_action': 0,
            'last_reward': 0
        }
        
        emit_rl_state()
        emit('episode-reset', {'status': 'success'})
        print(f"✓ Environment reset for client {request.sid}")
    
    except Exception as e:
        emit('error', {'message': f'Reset failed: {str(e)}'})
        print(f"✗ Error during reset: {str(e)}")

@socketio.on('get-state')
def handle_get_state():
    """Get current environment state."""
    if env is None:
        emit('error', {'message': 'Environment not initialized'})
        return
    
    try:
        emit_rl_state()
    except Exception as e:
        emit('error', {'message': f'Failed to get state: {str(e)}'})

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'flask_running': True,
        'model_loaded': model is not None,
        'current_algo': current_algo,
        'env_ready': env is not None
    })

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """List available trained models."""
    models = {
        'DQN': 'models/dqn/best_dqn.zip',
        'PPO': 'models/ppo/best_ppo.zip',
        'A2C': 'models/a2c/best_a2c.zip',
        'REINFORCE': 'models/reinforce/best_reinforce_policy.pth'
    }
    
    available = {}
    for algo, path in models.items():
        available[algo] = {
            'path': path,
            'exists': os.path.exists(path)
        }
    
    return jsonify(available)

@app.route('/api/load-model', methods=['POST'])
def load_model_endpoint():
    """Load a trained model."""
    global env, model, current_algo, episode_data
    
    data = request.json or {}
    algo_name = data.get('algorithm')
    
    if not algo_name:
        return jsonify({'error': 'Algorithm not specified'}), 400
    
    model_paths = {
        'DQN': 'models/dqn/best_dqn.zip',
        'PPO': 'models/ppo/best_ppo.zip',
        'A2C': 'models/a2c/best_a2c.zip',
        'REINFORCE': 'models/reinforce/best_reinforce_policy.pth'
    }
    
    model_path = model_paths.get(algo_name)
    if not model_path:
        return jsonify({'error': f'Unknown algorithm: {algo_name}'}), 400
    
    success, message = load_model(algo_name, model_path)
    
    if success:
        # Initialize environment
        env = DaladalaEnv(render_mode=None)
        episode_data['step'] = 0
        episode_data['total_reward'] = 0.0
        episode_data['episode_history'] = []
        
        return jsonify({
            'algorithm': algo_name,
            'status': 'success',
            'message': message
        })
    else:
        return jsonify({'error': message}), 400

@app.route('/api/reset', methods=['POST'])
def reset_environment():
    """Reset the environment and start a new episode."""
    global env, episode_data
    
    if env is None:
        return jsonify({'error': 'No model loaded. Load a model first.'}), 400
    
    try:
        obs, info = env.reset()
        episode_data['step'] = 0
        episode_data['total_reward'] = 0.0
        episode_data['episode_history'] = []
        
        # Get environment info
        police_checkpoints = getattr(env, 'police_checkpoints', [])
        traffic_lights = getattr(env, 'traffic_lights', [])
        high_demand_stops = getattr(env, 'high_demand_stops', [])
        
        environment_info = {
            'grid_size': 15,
            'route': env.route,
            'stops': env.route,
            'high_demand_stops': high_demand_stops,
            'police_checkpoints': police_checkpoints,
            'traffic_lights': traffic_lights,
            'max_steps': env.max_steps,
            'physical_max_passengers': env.physical_max,
            'legal_capacity': 33,
            'observation_space': list(env.observation_space.shape),
            'action_space': env.action_space.n,
            'actions': ["Move", "Pickup", "Dropoff", "Stop", "SpeedUp"]
        }
        
        return jsonify({
            'observation': obs.tolist(),
            'state': env_state_to_dict(),
            'environmentInfo': environment_info
        })
    except Exception as e:
        return jsonify({'error': f'Reset failed: {str(e)}'}), 500

@app.route('/api/step', methods=['POST'])
def step_environment():
    """Execute one step in the environment."""
    global env, model, episode_data
    
    if env is None or model is None:
        return jsonify({'error': 'No model loaded'}), 400
    
    data = request.json or {}
    use_model = data.get('use_model', True)
    action = data.get('action', None)
    
    try:
        # Check if episode is done
        if hasattr(env, 'step_count') and env.step_count >= env.max_steps:
            return jsonify({'error': 'Episode is done'}), 400
        
        # Get observation
        obs = env._get_obs()
        
        # Determine action
        if use_model:
            action, error = predict_action(obs)
            if error:
                return jsonify({'error': error}), 400
        elif action is not None:
            action = int(action)
        else:
            return jsonify({'error': 'No action provided'}), 400
        
        # Execute step
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Track episode data
        episode_data['step'] += 1
        episode_data['total_reward'] += reward
        episode_data['episode_history'].append({
            'step': env.step_count,
            'action': action,
            'reward': float(reward),
            'position': env.route[env.pos_idx] if env.pos_idx < len(env.route) else (14, 0)
        })
        
        action_names = {0: "Move", 1: "Pickup", 2: "Dropoff", 3: "Stop", 4: "SpeedUp"}
        
        response = {
            'action': action_names.get(int(action), "Unknown"),
            'reward': float(reward),
            'done': bool(terminated or truncated),
            'observation': obs.tolist(),
            'state': env_state_to_dict(),
            'episode_stats': {
                'total_reward': float(episode_data['total_reward']),
                'steps': episode_data['step']
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': f'Step error: {str(e)}'}), 500

@app.route('/api/episode-data', methods=['GET'])
def get_episode_data():
    """Get current episode data."""
    return jsonify(episode_data)

@app.route('/api/environment-info', methods=['GET'])
def get_environment_info():
    """Get information about the environment."""
    if env is None:
        return jsonify({'error': 'Environment not initialized'}), 400
    
    try:
        # Safe attribute access with defaults
        police_checkpoints = getattr(env, 'police_checkpoints', [])
        traffic_lights = getattr(env, 'traffic_lights', [])
        high_demand_stops = getattr(env, 'high_demand_stops', [])
        
        return jsonify({
            'grid_size': 15,
            'route': env.route,
            'stops': env.route,
            'high_demand_stops': high_demand_stops,
            'police_checkpoints': police_checkpoints,
            'traffic_lights': traffic_lights,
            'max_steps': env.max_steps,
            'physical_max_passengers': env.physical_max,
            'legal_capacity': 33,
            'observation_space': list(env.observation_space.shape),
            'action_space': env.action_space.n,
            'actions': ["Move", "Pickup", "Dropoff", "Stop", "SpeedUp"]
        })
    except Exception as e:
        return jsonify({'error': f'Environment info error: {str(e)}'}), 500

@app.route('/api/current-state', methods=['GET'])
def get_current_state():
    """Get current environment state."""
    if env is None:
        return jsonify({'error': 'Environment not initialized'}), 400
    
    try:
        return jsonify({
            'state': env_state_to_dict(),
            'episode': episode_data
        })
    except Exception as e:
        return jsonify({'error': f'State retrieval failed: {str(e)}'}), 500

# ============================================================================
# SERVE STATIC WEB FILES
# ============================================================================

@app.route('/', methods=['GET'])
def serve_index():
    """Serve the web interface."""
    return app.send_static_file('index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serve static files."""
    return app.send_static_file(path)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("DALADALA RL - FLASK API SERVER")
    print("="*80)
    print("\n✓ Flask API Server starting...")
    print("✓ Available at: http://localhost:5000")
    print("✓ API Documentation at: http://localhost:5000/api/health")
    print("\nEndpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/models              - List available models")
    print("  POST /api/load-model          - Load a trained model")
    print("  POST /api/reset               - Reset environment")
    print("  POST /api/step                - Execute one step")
    print("  GET  /api/environment-info    - Get environment details")
    print("  GET  /api/current-state       - Get current state")
    print("  GET  /api/episode-data        - Get episode history")
    
    print("\nWebSocket Events (via Socket.IO):")
    print("  EMIT: connect                 - Client connects")
    print("  EMIT: disconnect              - Client disconnects")
    print("  LISTEN: start-episode         - Start new episode")
    print("  LISTEN: step                  - Execute one step")
    print("  LISTEN: reset                 - Reset environment")
    print("  LISTEN: get-state             - Request current state")
    print("  BROADCAST: rl-update          - State update (all clients)")
    print("  BROADCAST: episode-complete   - Episode finished")
    print("  BROADCAST: connection-status  - Connection status")
    
    print("\n" + "="*80 + "\n")
    
    # Run with SocketIO support
    # Disable reloader to prevent server restarts during model loading (which wipes state)
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
