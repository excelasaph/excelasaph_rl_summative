# Phase 3a: WebSocket Support - Setup & Integration Guide

**Status:** ✅ Implementation Complete  
**Date:** November 20, 2025  
**Components:** Flask Backend WebSocket Integration

---

## 📋 What Was Added

### 1. **New Dependencies**

Added to `requirements.txt`:
```
flask-socketio>=5.3.0
python-socketio>=5.9.0
python-engineio>=4.7.0
```

These handle WebSocket connections with automatic fallbacks.

### 2. **Flask Modifications** (`flask_api.py`)

#### Imports Added:
```python
from flask_socketio import SocketIO, emit, disconnect
```

#### Initialization:
```python
# Initialize WebSocket support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# WebSocket connection tracking
connected_clients = set()
is_streaming = False
```

#### Global State Enhancement:
```python
episode_data = {
    'step': 0,
    'total_reward': 0.0,
    'episode_history': [],
    'terminated': False,
    'last_action': 0,
    'last_reward': 0
}
```

---

## 🔌 WebSocket Event Handlers

### **1. Connection Events**

#### `@socketio.on('connect')`
- Triggers when 3D render connects via WebSocket
- Adds client to `connected_clients` set
- Sends initial connection status
- **Logs:** Connection with client ID and total connected count

**Emits to client:**
```json
{
  "status": "connected",
  "model_loaded": false,
  "env_ready": false,
  "algorithm": null
}
```

#### `@socketio.on('disconnect')`
- Triggers when 3D render disconnects
- Removes client from `connected_clients` set
- **Logs:** Disconnection with remaining client count

---

### **2. Episode Control Events**

#### `@socketio.on('start-episode')`
- Starts a new RL episode
- Resets environment: `env.reset()`
- Resets episode data
- **Emits:** Initial state via `emit_rl_state()`
- **Returns:**
```json
{
  "status": "success",
  "episode": 1
}
```

#### `@socketio.on('reset')`
- Same as start-episode but called explicitly
- Resets environment and episode data
- **Emits:** Updated state
- **Returns:**
```json
{
  "status": "success"
}
```

---

### **3. Step Execution Event**

#### `@socketio.on('step')`
**Purpose:** Execute one RL step and broadcast state update

**Incoming Data:**
```json
{
  "action": 1  // Optional: if not provided, agent decides
}
```

**Process:**
1. If action not provided: Agent decides via model
2. Execute `env.step(action)`
3. Update episode data
4. Broadcast new state to all clients
5. Check if episode terminated
6. If terminated, emit `episode-complete`

**Emits:**
- `rl-update` (broadcast to all)
- `episode-complete` (if done)

---

### **4. State Query Event**

#### `@socketio.on('get-state')`
- Request current environment state
- Immediately emits `rl-update` with current state
- No parameters needed

---

## 📤 Broadcast Events (Server → All Clients)

### **`rl-update` Event**

Broadcast to all connected clients with complete state:

```json
{
  "type": "state-update",
  "data": {
    "action": 0,
    "passengers": 15,
    "capacity": 50,
    "money": 45000.0,
    "speed": 2.5,
    "position": [5, 10],
    "light_red": 0,
    "police_here": 0,
    "must_stop": 0,
    "fined": 0,
    "hazards": [
      [3, 8, "police"],
      [7, 6, "trafficLight"]
    ],
    "police_checkpoints": [[3, 8], [7, 6]],
    "traffic_lights": [[7, 6]],
    "high_demand_stops": [[4, 14], [8, 14], [14, 8], [14, 3]],
    "light_cycle": 5,
    "step": 42,
    "episode": 1,
    "total_reward": 450.8,
    "terminated": false,
    "reward": 15.3
  },
  "timestamp": 3
}
```

**Broadcast Frequency:** After every step or state query

### **`episode-complete` Event**

Emitted when episode terminates or truncates:

```json
{
  "status": "completed",
  "total_reward": 450.8,
  "steps": 42,
  "reason": "terminated"  // or "truncated"
}
```

### **`connection-status` Event**

Sent to client on connection:

```json
{
  "status": "connected",
  "model_loaded": true,
  "env_ready": true,
  "algorithm": "DQN"
}
```

### **`error` Event**

Sent on any error:

```json
{
  "message": "No model loaded"
}
```

---

## 🚀 Installation & Testing

### **Step 1: Install Dependencies**

```bash
pip install flask-socketio python-socketio python-engineio
```

Or update all at once:
```bash
pip install -r requirements.txt
```

### **Step 2: Start Flask Server**

```bash
python flask_api.py
```

**Expected Output:**
```
================================================================================
DALADALA RL - FLASK API SERVER
================================================================================

✓ Flask API Server starting...
✓ Available at: http://localhost:5000
✓ API Documentation at: http://localhost:5000/api/health

Endpoints:
  GET  /api/health              - Health check
  GET  /api/models              - List available models
  POST /api/load-model          - Load a trained model
  POST /api/reset               - Reset environment
  POST /api/step                - Execute one step
  GET  /api/environment-info    - Get environment details
  GET  /api/current-state       - Get current state
  GET  /api/episode-data        - Get episode history

WebSocket Events (via Socket.IO):
  EMIT: connect                 - Client connects
  EMIT: disconnect              - Client disconnects
  LISTEN: start-episode         - Start new episode
  LISTEN: step                  - Execute one step
  LISTEN: reset                 - Reset environment
  LISTEN: get-state             - Request current state
  BROADCAST: rl-update          - State update (all clients)
  BROADCAST: episode-complete   - Episode finished
  BROADCAST: connection-status  - Connection status

================================================================================
```

### **Step 3: Test WebSocket Connection**

#### Using Browser Console:

```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Listen for connection
socket.on('connect', () => {
  console.log('Connected to Flask');
});

// Listen for state updates
socket.on('rl-update', (data) => {
  console.log('State update:', data);
});

// Listen for errors
socket.on('error', (error) => {
  console.error('Error:', error);
});

// Send step command
socket.emit('step', { action: 1 });
```

#### Using Python (for testing):

```python
import socketio
import time

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to Flask')

@sio.event
def rl_update(data):
    print(f"Step {data['data']['step']}: Reward={data['data']['reward']}")

@sio.event
def error(data):
    print(f"Error: {data['message']}")

sio.connect('http://localhost:5000')

# Load model
# (Make HTTP request to /api/load-model first)

# Start episode
sio.emit('start-episode')
time.sleep(1)

# Run steps
for i in range(10):
    sio.emit('step', {'action': 0})  # Move action
    time.sleep(0.5)

sio.disconnect()
```

---

## 🔍 Debugging WebSocket

### **Enable Flask Debug Logging**

Add to `flask_api.py` after app initialization:

```python
import logging
logging.getLogger('flask_socketio').setLevel(logging.DEBUG)
logging.getLogger('socketio').setLevel(logging.DEBUG)
logging.getLogger('engineio').setLevel(logging.DEBUG)
```

### **Check Connected Clients**

Add an HTTP endpoint to check active connections:

```python
@app.route('/api/ws-status', methods=['GET'])
def ws_status():
    return jsonify({
        'connected_clients': len(connected_clients),
        'is_streaming': is_streaming,
        'client_ids': list(connected_clients)
    })
```

### **Common Issues**

**Issue:** "Connection refused"
- Flask not running on port 5000
- Check: `python flask_api.py` is executing

**Issue:** "Model not loaded" error
- Load model first via `/api/load-model`
- Check: Model file exists in `models/` directory

**Issue:** Events not received
- Check browser console for errors
- Verify Socket.IO client library loaded
- Ensure CORS enabled: `cors_allowed_origins="*"`

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│           3D Render (React/Three.js)                    │
│         ────────────────────────────────────            │
│                                                           │
│    useRLConnection.ts (Socket.IO Client)               │
│         ↓ emit('step')                                   │
│         ↑ on('rl-update')                               │
└──────────────┬──────────────────────────────────────────┘
               │ WebSocket
               │ (Socket.IO)
               │
┌──────────────▼──────────────────────────────────────────┐
│           Flask API Server                              │
│         ────────────────────────────────────            │
│                                                           │
│  @socketio.on('step')                                  │
│    → env.step(action)                                   │
│    → emit('rl-update', state)                           │
│    → broadcast to all clients                           │
│                                                           │
│  Global State:                                          │
│    - env (DaladalaEnv)                                 │
│    - model (DQN/PPO/A2C/REINFORCE)                     │
│    - episode_data (step, reward, history)              │
│    - connected_clients (set of IDs)                    │
└─────────────────────────────────────────────────────────┘
         ↑        ↑        ↑        ↑
         │        │        │        │
    DQN Model  Environment  Rewards  State
```

---

## ✅ Verification Checklist

- [x] Dependencies added to `requirements.txt`
- [x] Flask SocketIO initialized
- [x] Connection/disconnect handlers implemented
- [x] start-episode handler implemented
- [x] step handler implemented
- [x] reset handler implemented
- [x] get-state handler implemented
- [x] emit_rl_state() helper function
- [x] State mapping complete
- [x] Error handling in place
- [x] Logging for debugging
- [x] CLI output updated with WebSocket endpoints

---

## 🎯 Next Steps (Phase 3b)

Now that WebSocket backend is ready:

1. **Update 3D Render Connection Hook**
   - Replace raw WebSocket with Socket.IO client
   - Update event listeners to match Flask events

2. **Update Zustand Store**
   - Add 5-action mapping
   - Add state mapping from Flask

3. **Update HUD Component**
   - Display correct 5 actions
   - Show real RL state data

4. **Integration Testing**
   - Connect Flask to 3D render
   - Verify real-time state updates
   - Run full episode

---

## 📝 Files Modified

1. **`flask_api.py`** - Added WebSocket support
2. **`requirements.txt`** - Added Socket.IO dependencies

---

## 🚨 Important Notes

1. **Backward Compatibility:** HTTP REST API still works alongside WebSocket
   - Clients can use either or both
   - `/api/step`, `/api/reset`, etc. still functional

2. **Broadcasting:** All clients receive `rl-update` events
   - Multiple 3D renders can visualize same agent
   - Useful for monitoring/debugging

3. **Performance:** Each step broadcasts to all clients
   - Monitor with `/api/ws-status` if needed
   - Add throttling if >50 clients expected

4. **Thread Safety:** Uses `async_mode='threading'`
   - Safe for Flask's development server
   - Use `async_mode='gevent'` for production with `pip install gevent gevent-websocket`

---

**Status:** ✅ Phase 3a Complete - Ready for Phase 3b

