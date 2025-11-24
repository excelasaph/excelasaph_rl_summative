# Complete Integration Flow Guide: Flask API + 3D Render + Trained Models

## 🎯 Executive Summary

The integration follows a **client-server WebSocket architecture** where:
- **Backend (Flask)**: Runs the RL environment, loads trained models, manages game state
- **Frontend (React 3D)**: Visualizes the environment in real-time, sends user input, receives state updates
- **Communication**: WebSocket (Socket.IO) for real-time bidirectional communication

This replaces the old **pygame-based rendering** with a **web-based 3D visualization**, while keeping all RL logic intact.

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAINED MODELS (Disk)                         │
│  models/dqn/best_dqn.zip | models/ppo/best_ppo.zip | etc.      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ↓
                    ┌─────────────────────┐
                    │   Flask API (5000)   │
                    │   ─────────────────  │
                    │ • Load models        │
                    │ • Run environment    │
                    │ • WebSocket server   │
                    │ • State management   │
                    └──────────────┬───────┘
                                   │
                    ╔══════════════╩══════════════╗
                    ║     WebSocket (Socket.IO)    ║
                    ║  Bidirectional Real-time    ║
                    ╚══════════════╦══════════════╝
                                   │
                    ┌──────────────┴─────────────┐
                    ↓                            ↓
         ┌────────────────────┐      ┌────────────────────┐
         │  Browser Tab       │      │  Browser Tab N     │
         │  React (5173)      │      │  React (5173)      │
         │  ─────────────────  │      │  ─────────────────  │
         │ • Zustand store    │      │ • Zustand store    │
         │ • Socket.IO client │      │ • Socket.IO client │
         │ • Three.js 3D      │      │ • Three.js 3D      │
         │ • HUD/UI           │      │ • HUD/UI           │
         └────────────────────┘      └────────────────────┘
```

---

## 🔄 Complete Integration Flow

### Phase 1: Startup (Developer Initiates)

```
1. Developer starts Flask backend:
   $ python flask_api.py
   ✓ Flask server starts on http://localhost:5000
   ✓ Socket.IO server ready for WebSocket connections
   ✓ No model loaded yet (waiting for frontend request)

2. Developer starts React frontend:
   $ cd 3d-render && npm run dev
   ✓ Vite dev server starts on http://localhost:5173
   ✓ React app loads in browser
   
3. Browser opens http://localhost:5173
   ✓ Scene.tsx loads
   ✓ useRLConnection hook initializes Socket.IO client
   ✓ Socket.IO connects to Flask backend at http://localhost:5000
   ✓ HUD shows "Connected" status
```

### Phase 2: Model Loading (Frontend Initiated)

```
Frontend Action (HUD Button - NOT YET IMPLEMENTED):
  onClick={async () => {
    const res = await fetch('http://localhost:5000/api/load-model', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ algorithm: 'PPO' })
    })
    const data = await res.json()
    // Shows: "PPO model loaded successfully"
  }}

Backend (Flask):
  @app.route('/api/load-model', methods=['POST'])
  1. Extract algorithm name from request
  2. Find model file (models/ppo/best_ppo.zip)
  3. Load model using stable-baselines3
  4. Initialize DaladalaEnv environment
  5. Return success response

Frontend (Zustand):
  1. Store model ready status
  2. Update UI to show "Ready to start episode"
```

### Phase 3: Episode Start (Frontend Initiated)

```
Frontend Action (HUD Button):
  onClick={() => socket.emit('start-episode')}

Backend (Flask) - WebSocket Handler:
  @socketio.on('start-episode')
  1. Call env.reset()
  2. Get initial observation
  3. Initialize episode_data (step=0, total_reward=0)
  4. Call emit_rl_state() to broadcast current state
  
  emit_rl_state():
    - Collects: position, passengers, money, speed, hazards, etc.
    - Broadcasts via: socketio.emit('rl-update', {...}, broadcast=True)
    - Sends to ALL connected clients

Frontend (Zustand):
  @socketio.on('rl-update')
  1. Receive state update from Flask
  2. Call updateFromRL(data)
  3. Update Zustand store with new values:
     - position, passengers, money, speed, hazards, etc.
  4. React re-renders components with new values

Frontend (Scene Components):
  1. Daladala component reads position from store
  2. Moves bus from [7, 7] to new position with animation
  3. HUD component reads all state values
  4. HUD displays: passengers, money, rewards, hazards, etc.
  5. Camera follows bus
```

### Phase 4: Episode Progression (Automated Loop)

```
Frontend (HUD Button):
  onClick={() => {
    setInterval(() => socket.emit('step', {}), 500)  // 500ms per step
  }}

Backend (Flask) - WebSocket Handler:
  @socketio.on('step')
  LOOP (for each step):
    1. Get current observation from environment
    2. Call predict_action(obs) to get action from loaded model
    3. Execute: obs, reward, terminated, truncated, info = env.step(action)
    4. Update episode_data:
       - step += 1
       - total_reward += reward
       - last_action = action
       - last_reward = reward
       - terminated = terminated or truncated
    5. Call emit_rl_state() to broadcast new state
    6. If terminated or truncated:
       - Emit 'episode-complete' event
       - Stop stepping

Frontend (Zustand) - Each Step:
  1. Receive 'rl-update' event
  2. updateFromRL(data) updates store:
     - position: [x, y]         (where bus is on grid)
     - passengers: N            (how many passengers)
     - money: M                 (total earnings)
     - speed: S                 (current speed)
     - light_red: 0/1           (red light active)
     - police_here: 0/1         (police checkpoint)
     - must_stop: 0/1           (combined flag)
     - reward: R                (reward from this step)
     - total_reward: TR         (cumulative)
     - action: A                (what agent did)

Frontend (3D Scene) - Each Update:
  1. Daladala component:
     - Reads new position from store
     - Converts grid [x, y] to world coords via gridToWorld()
     - Animates bus to new position (0.5s lerp)
     - Rotates bus to face direction
  
  2. HUD component:
     - Displays new values: passengers, money, speed
     - Shows alerts if hazards triggered
     - Updates action color indicator
     - Shows "Overloaded!" if > 33 passengers

Frontend (Browser):
  - See bus smoothly moving on 3D road
  - See HUD update with latest stats
  - See camera follow bus
  - See alerts pop up when hazards encountered
```

### Phase 5: Episode Complete (Terminal Condition)

```
Backend (Flask):
  if (env.step_count >= env.max_steps):
    Emit 'episode-complete' event
    Include: total_reward, final_passengers, final_money, etc.

Frontend (Zustand):
  @socketio.on('episode-complete')
  1. Set terminated = true
  2. Stop auto-stepping loop
  3. Display episode summary
  4. Enable "Start New Episode" button

Frontend (HUD):
  Shows summary like:
  ┌─────────────────────────────────┐
  │ EPISODE COMPLETE                │
  │ ─────────────────────────────── │
  │ Total Reward: 150.23            │
  │ Steps: 350                      │
  │ Final Passengers: 38 (overload) │
  │ Final Money: TSh 45,000         │
  │ Route Progress: 100%            │
  └─────────────────────────────────┘
```

---

## 💾 Data Flow Details

### Request from Frontend → Backend

```javascript
// Frontend (React)
socket.emit('step', { 
  action: undefined  // Agent decides automatically
})

// What happens:
// 1. Socket.IO serializes the data to JSON
// 2. Sends to Flask server at http://localhost:5000
// 3. Flask receives in @socketio.on('step')
```

### Response from Backend → Frontend

```python
# Backend (Flask)
def emit_rl_state():
    state_data = {
        'step': 350,
        'x': 7, 'y': 5,                    # Grid position
        'position': [7, 5],                # Position array
        'passengers': 38,                  # Current occupancy
        'capacity': 50,                    # Max capacity
        'money': 45000.50,                 # Earnings
        'speed': 1.2,                      # Movement speed
        'fined': 0,                        # Penalty flag
        'light_red': 1,                    # Red light active
        'police_here': 0,                  # Police present
        'must_stop': 1,                    # Combined safety flag
        'hazards': [
            [5, 3, 'trafficLight'],
            [8, 2, 'police']
        ],
        'police_checkpoints': [[8, 2], [11, 4]],
        'traffic_lights': [[5, 3], [12, 7]],
        'high_demand_stops': [[2, 1], [9, 8]],
        'light_cycle': 7,                  # Traffic light state
        'episode': 5,
        'action': 3,                       # Action taken: STOP
        'reward': -1.5,                    # Reward from this step
        'total_reward': 150.23,            # Cumulative reward
        'terminated': False                # Episode still running
    }
    
    socketio.emit('rl-update', {
        'type': 'state-update',
        'data': state_data,
        'timestamp': 1234567890
    }, broadcast=True)
    
# Frontend receives (Zustand):
{
  type: 'state-update',
  data: { ...all the above fields... },
  timestamp: 1234567890
}
```

### State Mapping (Flask → Zustand)

```typescript
// Zustand store receives from Flask and maps it:
updateFromRL: (data) => {
  const flaskData = data.data || data;
  return {
    step: flaskData.step,                    // 350
    position: flaskData.position,            // [7, 5]
    passengers: flaskData.passengers,        // 38
    capacity: flaskData.capacity,            // 50
    money: flaskData.money,                  // 45000.50
    speed: flaskData.speed,                  // 1.2
    light_red: flaskData.light_red,          // 1
    police_here: flaskData.police_here,      // 0
    must_stop: flaskData.must_stop,          // 1
    fined: flaskData.fined,                  // 0
    hazards: flaskData.hazards,              // [[5,3,'trafficLight'], ...]
    police_checkpoints: flaskData.police_checkpoints,
    traffic_lights: flaskData.traffic_lights,
    high_demand_stops: flaskData.high_demand_stops,
    light_cycle: flaskData.light_cycle,      // 7
    episode: flaskData.episode,              // 5
    action: flaskData.action,                // 3 (STOP)
    reward: flaskData.reward,                // -1.5
    total_reward: flaskData.total_reward,    // 150.23
    terminated: flaskData.terminated,        // false
    isConnected: true
  }
}

// React components read from Zustand:
const { position, passengers, money } = useGameStore()
// Now they have latest values and automatically re-render
```

---

## 🎮 User Interaction Flow

### From pygame to Web-based 3D

**Old Flow (pygame):**
```
User runs: python main.py
  → pygame window opens
  → model predicts actions every frame
  → pygame renders
  → User watches (no interaction)
  → Loop until episode done
  → Window closes
```

**New Flow (Web 3D):**
```
1. Developer: python flask_api.py
2. Developer: cd 3d-render && npm run dev
3. User opens browser: http://localhost:5173
4. Frontend HUD shows connection status and buttons:
   ┌─────────────────────────────────┐
   │ [Load Model: PPO]               │
   │ [Start Episode] [Step] [Reset]  │
   │ [Auto-run (every 500ms)]        │
   └─────────────────────────────────┘
5. User clicks "Load Model: PPO"
   → Flask loads model from disk
   → Zustand updates: modelReady = true
6. User clicks "Start Episode"
   → Flask resets environment
   → State broadcast to frontend
   → 3D bus appears at starting position
   → HUD shows initial stats
7. User clicks "Auto-run"
   → Frontend sends 'step' events every 500ms
   → Flask executes environment steps
   → States broadcast back
   → 3D bus animates along road
   → HUD updates in real-time
8. Episode completes (350 steps)
   → Backend emits 'episode-complete'
   → Frontend shows summary
   → User can start new episode
```

---

## 🔧 Implementation Details

### 1. Flask Backend Structure

```python
# flask_api.py

# Global state
env = None                    # DaladalaEnv instance
model = None                  # Trained model (DQN, PPO, A2C, or REINFORCE)
current_algo = None           # Algorithm name
connected_clients = set()     # WebSocket clients
episode_data = {}            # Current episode tracking

# REST Endpoints (synchronous HTTP)
@app.route('/api/health')                    # ✓ Check if running
@app.route('/api/load-model', methods=['POST'])  # ✓ Load trained model
@app.route('/api/reset', methods=['POST'])       # ✓ Reset environment
@app.route('/api/step', methods=['POST'])        # ✓ Execute one step
@app.route('/api/environment-info')              # ✓ Get env metadata

# WebSocket Handlers (async events via Socket.IO)
@socketio.on('connect')          # ✓ Client connected
@socketio.on('start-episode')    # ✓ Start new episode
@socketio.on('step')             # ✓ Execute step
@socketio.on('reset')            # ✓ Reset environment
@socketio.on('get-state')        # ✓ Request state
@socketio.on('disconnect')       # ✓ Client disconnected

# Broadcast function
def emit_rl_state():             # ✓ Send state to all clients
```

### 2. React Frontend Structure

```typescript
// 3d-render/src/

// hooks/useRLConnection.ts
export const useRLConnection = (wsUrl = 'http://localhost:5000') => {
  const socketRef = useRef<Socket | null>(null)
  
  // Initialization
  const connect = useCallback(() => {
    const socket = io(wsUrl, { /* config */ })
    socket.on('rl-update', (data) => updateFromRL(data))
    socketRef.current = socket
  }, [])
  
  // Public methods
  const startEpisode = () => socketRef.current?.emit('start-episode')
  const step = (action?: number) => socketRef.current?.emit('step', { action })
  const reset = () => socketRef.current?.emit('reset')
  const getState = () => socketRef.current?.emit('get-state')
  
  return { startEpisode, step, reset, getState, isConnected, socket }
}

// store/gameStore.ts (Zustand)
export const useGameStore = create<GameState>((set) => ({
  // RL state from Flask
  step: 0,
  position: [7, 7],
  passengers: 0,
  money: 0,
  speed: 0,
  light_red: 0,
  police_here: 0,
  must_stop: 0,
  action: 0,
  reward: 0,
  total_reward: 0,
  
  // Actions
  updateFromRL: (data) => set((state) => ({
    step: data.data.step,
    position: data.data.position,
    passengers: data.data.passengers,
    // ... all other fields
  })),
}))

// components/game/Scene.tsx
export const Scene = () => {
  useRLConnection('http://localhost:5000')  // Connect to Flask
  
  return (
    <Canvas>
      <Road />
      <Daladala />      {/* Reads position from Zustand */}
      <CameraController /> {/* Follows Daladala */}
    </Canvas>
  )
}

// components/game/HUD.tsx
export const HUD = () => {
  const { passengers, money, position, action } = useGameStore()
  
  return (
    <div>
      {/* Display all state from Zustand */}
      <Card>Passengers: {passengers}/50</Card>
      <Card>Money: TSh {money}</Card>
      <Card>Position: ({position[0]}, {position[1]})</Card>
      {/* Buttons for user interaction */}
      <Button onClick={() => socket.emit('start-episode')}>Start</Button>
    </div>
  )
}
```

### 3. State Mapping (Critical Connection Points)

```
Flask Environment State              Zustand Store              3D Rendering
─────────────────────────            ────────────────           ───────────
env.pos_idx → [x, y]  ─────────→    position: [x, y]  ─────→  Daladala.position
                                                               (via gridToWorld)
                                                               
env.passengers ────────────────→    passengers: N    ─────→   HUD.passengers
                                                               
env.money ─────────────────────→    money: M         ─────→   HUD.money
                                                               
env.speed ─────────────────────→    speed: S         ─────→   HUD.speed
                                                               Bus animation
                                                               
env.step_count ────────────────→    step: S          ─────→   HUD.step
                                                               
[light_red, police] ───────────→    light_red: 0/1   ─────→   HUD alerts
                                    police_here: 0/1          (red pulse)
                                    must_stop: 0/1
                                    
env.fined ─────────────────────→    fined: 0/1       ─────→   HUD alert
                                                               (fine notification)
                                                               
Hazard arrays ─────────────────→    hazards: [...]   ─────→   Scene rendering
                                    police_check...           (renders hazard
                                    traffic_lights            markers)
```

---

## 🚀 Complete Startup Procedure

### Terminal 1 - Flask Backend
```bash
cd "c:\Users\Excel\Desktop\Github Projects\excelasaph_rl_summative"
python flask_api.py

# Expected output:
# ================================================================================
# DALADALA RL - FLASK API SERVER
# ================================================================================
# ✓ Flask API Server starting...
# ✓ Available at: http://localhost:5000
# ✓ Endpoints:
#   GET  /api/health              - Health check
#   POST /api/load-model          - Load a trained model
#   POST /api/reset               - Reset environment
#   POST /api/step                - Execute one step
#   ...WebSocket Events listed...
```

### Terminal 2 - React Frontend
```bash
cd "c:\Users\Excel\Desktop\Github Projects\excelasaph_rl_summative\3d-render"
npm run dev

# Expected output:
# ✓ built in 2.34s
# 
# ➜  Local:   http://localhost:5173/
# ➜  press h to show help
```

### Browser Tab
```
1. Open: http://localhost:5173
2. See: 3D Daladala bus on road
3. Check: Console (F12) for connection logs
   "✓ Connected to Flask WebSocket (Socket.IO)"
4. HUD shows connection status: green dot + "Connected"
```

---

## 📋 Next Steps to Complete Integration

### TODO: Add HUD Buttons for Manual Control

Currently, the HUD displays state but doesn't have buttons to control the flow. Add to `HUD.tsx`:

```typescript
import { Button } from '@/components/ui/button'

const [autoRunning, setAutoRunning] = useState(false)

// Add to return JSX:
<div className="absolute bottom-20 left-4 flex gap-2">
  <Button 
    onClick={() => socket.emit('start-episode')}
    className="pointer-events-auto"
  >
    Start Episode
  </Button>
  
  <Button 
    onClick={() => socket.emit('step', {})}
    className="pointer-events-auto"
  >
    Single Step
  </Button>
  
  <Button 
    onClick={() => {
      setAutoRunning(!autoRunning)
      if (!autoRunning) {
        const interval = setInterval(
          () => socket.emit('step', {}),
          500  // 500ms per step
        )
      }
    }}
    className="pointer-events-auto"
  >
    {autoRunning ? 'Stop Auto' : 'Auto Run'}
  </Button>
  
  <Button 
    onClick={() => socket.emit('reset')}
    className="pointer-events-auto"
  >
    Reset
  </Button>
</div>
```

### TODO: Add Model Selection Dropdown

Add to `HUD.tsx`:

```typescript
<select 
  onChange={(e) => {
    fetch('http://localhost:5000/api/load-model', {
      method: 'POST',
      body: JSON.stringify({ algorithm: e.target.value }),
      headers: { 'Content-Type': 'application/json' }
    })
  }}
  className="pointer-events-auto"
>
  <option value="">Select Model...</option>
  <option value="DQN">DQN</option>
  <option value="PPO">PPO</option>
  <option value="A2C">A2C</option>
  <option value="REINFORCE">REINFORCE</option>
</select>
```

### TODO: Add Episode Summary Modal

After episode completes, show:
```
┌─────────────────────────────────────────┐
│ EPISODE COMPLETE                        │
│ ─────────────────────────────────────── │
│ Algorithm: PPO                          │
│ Total Reward: +150.23                   │
│ Steps: 350 / 350                        │
│ Final Position: (14, 0) ✓ Reached      │
│ Final Passengers: 38 / 50 ⚠ Overload   │
│ Final Money: TSh 45,000                 │
│ Safety Rating: ★★★☆☆                   │
│                                         │
│ [Start New Episode]  [Back to Menu]    │
└─────────────────────────────────────────┘
```

---

## ⚡ Key Advantages of Web-based Integration

| Aspect | Old (pygame) | New (Web 3D) |
|--------|-------------|------------|
| **Rendering** | 2D grid + text | AAA 3D visualizations |
| **Flexibility** | Local only | Network accessible |
| **Multi-view** | Single window | Multiple browser tabs |
| **UI Design** | Custom pygame | React + Tailwind CSS |
| **State sharing** | In-process only | Any connected client |
| **Real-time** | Frame-based | Event-based WebSocket |
| **Development** | Python only | Full-stack (Python + TS) |
| **Testing** | Manual | Automated tests |

---

## 🐛 Troubleshooting

### Issue: "Cannot GET /api/health"
**Cause:** Flask backend not running
**Fix:** Start Flask: `python flask_api.py`

### Issue: "WebSocket connection failed"
**Cause:** Flask port mismatch or CORS issue
**Fix:** Check Flask running on 5000, React connecting to correct URL

### Issue: HUD shows "Disconnected"
**Cause:** Socket.IO connection not established
**Fix:** Check browser console (F12) for errors, check CORS settings

### Issue: Bus doesn't move
**Cause:** Position not updating from Flask
**Fix:** Check `useGameStore.setState` is being called with position data

### Issue: Episode doesn't start
**Cause:** Model not loaded
**Fix:** Ensure `python flask_api.py` ran `/api/load-model` first, or add model selector to HUD

---

## 📚 Related Files

- **Backend:** `flask_api.py`
- **Frontend State:** `3d-render/src/store/gameStore.ts`
- **WebSocket Hook:** `3d-render/src/hooks/useRLConnection.ts`
- **Scene:** `3d-render/src/components/game/Scene.tsx`
- **HUD:** `3d-render/src/components/game/HUD.tsx`
- **Visualization:** `3d-render/src/components/game/Daladala.tsx`
- **Utilities:** `3d-render/src/lib/gridToWorld.ts`

---

## 🎓 Summary

**The integration flow is:**

1. **Startup:** Flask backend + React frontend + Browser
2. **Connection:** useRLConnection hook connects frontend to Flask via Socket.IO
3. **Initialization:** Load trained model via `/api/load-model`
4. **Episode:** Frontend starts episode via `socket.emit('start-episode')`
5. **Loop:** Frontend sends `socket.emit('step')` every 500ms
6. **Updates:** Flask broadcasts `rl-update` events to all clients
7. **Rendering:** Zustand store updates trigger React re-renders
8. **Visualization:** 3D bus moves, HUD updates, alerts show hazards
9. **Complete:** Episode ends, frontend shows summary

**Replace pygame** by simply not calling `render_frame()` and instead relying on WebSocket updates to drive the 3D visualization.

---

*Last Updated: November 21, 2025*
*Status: Complete Integration Architecture*

