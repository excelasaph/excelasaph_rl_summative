# Flask API + 3D Render: Visual Cheat Sheet

## 🎯 The Big Picture (One Page)

```
                    DALADALA RL SYSTEM
                    
┌──────────────────────────────────────────────────────┐
│                   TRAINED MODELS                      │
│  models/ppo/best_ppo.zip  models/dqn/best_dqn.zip   │
│  models/a2c/best_a2c.zip  models/reinforce/*.pth    │
└──────────────────────────┬──────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   FLASK API  │
                    │ (Port 5000)  │
                    │              │
                    │  • Load model│
                    │  • Run env   │
                    │  • Broadcast│
                    │    state     │
                    └──────┬───────┘
                           │
                    WebSocket (SO)
                    Bidirectional
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼──┐          ┌────▼──┐         ┌────▼──┐
   │Browser│          │Browser│         │Browser│
   │  Tab1 │          │  Tab2 │         │  N    │
   │ React │          │ React │         │ React │
   │3D View│          │3D View│         │3D View│
   └───────┘          └───────┘         └───────┘
   
All viewers SYNC perfectly! ✓
```

---

## 🚀 Startup Sequence (Copy-Paste)

### Terminal 1: Backend
```bash
cd "c:\Users\Excel\Desktop\Github Projects\excelasaph_rl_summative"
python flask_api.py
```
✓ Shows: "Available at: http://localhost:5000"

### Terminal 2: Frontend
```bash
cd "c:\Users\Excel\Desktop\Github Projects\excelasaph_rl_summative\3d-render"
npm run dev
```
✓ Shows: "Local: http://localhost:5173"

### Browser: Open
```
http://localhost:5173
```
✓ Shows: 3D road, bus, HUD with "Connected" green dot

---

## 🔄 One Episode = One Data Flow

```
STEP 0: Start
│
├─→ FRONTEND: socket.emit('step', {})
│   └─ Sends WebSocket message
│
├─→ BACKEND: @socketio.on('step')
│   ├─ obs = env._get_obs()
│   ├─ action = model.predict(obs)
│   ├─ obs, reward, done, _, _ = env.step(action)
│   └─ socketio.emit('rl-update', {...}, broadcast=True)
│
└─→ ALL BROWSERS: @socket.on('rl-update')
    ├─ updateFromRL(data)
    ├─ Zustand.setState({position, passengers, money, ...})
    ├─ React re-renders
    └─ Three.js animates bus to new position

RESULT: Bus moves, HUD updates, all viewers sync
TIME: ~50-100ms
```

---

## 📊 State Mapping at a Glance

```
FLASK SENDS:                    ZUSTAND STORES:              HUD DISPLAYS:
────────────                    ────────────────              ─────────────
step: 350                       step: 350                     Step: 350
position: [8, 5]       ────→    position: [8, 5]    ────→    Position: (8, 5)
passengers: 38                  passengers: 38               Passengers: 38/50
money: 45000                    money: 45000                 Money: TSh 45,000
speed: 1.2                      speed: 1.2                   Speed: 1.2 km/h
light_red: 1           ────→    light_red: 1        ────→    🚦 RED LIGHT
police_here: 0                  police_here: 0               (no alert)
must_stop: 1           ────→    must_stop: 1        ────→    ⛔ MUST STOP
action: 0                       action: 0                    Action: Move (blue)
reward: +5.2           ────→    reward: +5.2        ────→    Last: +5.2
total_reward: 150.23            total_reward: 150.23         Total: +150.23
terminated: false               terminated: false            (episode running)
```

---

## 🎮 Control Flow (What Happens When)

```
USER CLICKS          FRONTEND DOES           BACKEND DOES        UI UPDATES
─────────────        ──────────────          ────────────        ──────────

[Start Episode]  →   emit('start-episode')  →  env.reset()       • Episode #1
                                               emit state         • Position [7,7]
                                                                  • Passengers: 0
                                                                  • Money: 0

[Step]          →   emit('step', {})       →  env.step()         • Position changed
                                               update reward      • HUD refreshed
                                               emit state         • Bus animated

[Auto Run]      →   setInterval(           →  Repeats step       • Bus moves
                     emit('step'),             every loop        • Animation smooth
                     500ms)                                       • HUD continuous

[Auto Run Stop]  →   clearInterval()        →  (same)            • Stops animation

[Reset]         →   emit('reset')          →  env.reset()        • Back to [7,7]
                                               emit state         • Passengers: 0
```

---

## 🔌 WebSocket Messages (Reference)

### Client → Server
```javascript
// Start new episode
socket.emit('start-episode')

// Execute one step
socket.emit('step', { action: undefined })  // Auto-decide
socket.emit('step', { action: 0 })          // Manual: MOVE

// Reset environment
socket.emit('reset')

// Request current state
socket.emit('get-state')
```

### Server → All Clients
```python
# State update (BROADCAST to all)
socketio.emit('rl-update', {
    'data': {
        'step': 350,
        'position': [8, 5],
        'passengers': 38,
        'money': 45000,
        'action': 0,
        'reward': 5.2,
        'total_reward': 150.23,
        # ... 14 more fields
    }
}, broadcast=True)

# Episode finished
socketio.emit('episode-complete', {
    'status': 'completed',
    'total_reward': 150.23,
    'steps': 350
}, broadcast=True)
```

---

## ✅ Verification: Is Everything Working?

```
CHECK 1: Flask Running?
$ curl http://localhost:5000/api/health
✓ Returns: {"status": "ok", "flask_running": true}

CHECK 2: React Running?
✓ Open: http://localhost:5173
✓ See: 3D road with bus

CHECK 3: Connected?
Browser Console (F12):
$ socket.connected
✓ true

$ socket.emit('get-state')
✓ Console shows: "rl-update" event received

CHECK 4: State Flowing?
Browser Console (F12):
$ useGameStore.getState()
✓ Shows: {step: 0, position: [7,7], passengers: 0, ...}

CHECK 5: Can Start Episode?
Browser Console (F12):
$ socket.emit('start-episode')
✓ HUD shows episode started

CHECK 6: Can Step?
Browser Console (F12):
$ socket.emit('step', {})
✓ Bus moves on screen
✓ HUD updates
```

---

## 🎨 Architecture in ASCII

### Request Response Flow
```
┌─ FRONTEND ────────────────────────┐
│  User clicks button               │
│  ↓                                │
│  socket.emit('step', {})          │
│  └─────────────────────────────→ │
└─────────────────────────────────┘ │
                                    │
┌─ BACKEND (FLASK) ─────────────────┤
│                                   │
│  @socketio.on('step')             │
│  ├─ obs = env._get_obs()          │
│  ├─ action = model.predict(obs)   │
│  ├─ obs, r, done, _, _ = env.step│
│  ├─ emit_rl_state()               │
│  │                                │
│  └──→ socketio.emit(..., broad=T) │
│      ↓                            │
└─ BROADCAST TO ALL CLIENTS ────────┤
                                    │
┌─ ALL BROWSERS ────────────────────┤
│  @socket.on('rl-update', (data))  │
│  ├─ updateFromRL(data)            │
│  ├─ Zustand.setState({...})       │
│  ├─ React re-renders              │
│  └─ Three.js animates             │
└────────────────────────────────────┘
```

### Component Stack
```
Browser Tab
  │
  ├─ <Canvas> (Three.js)
  │  ├─ <Road>
  │  ├─ <Daladala> ←─ reads position from Zustand
  │  ├─ <CameraController>
  │  └─ <EffectComposer>
  │
  ├─ <HUD> ←─ reads all state from Zustand
  │  ├─ Connection status
  │  ├─ Episode/Step display
  │  ├─ Position display
  │  ├─ Passengers/Money display
  │  ├─ Rewards display
  │  └─ Alerts (lights, police, etc)
  │
  └─ useRLConnection() ←─ Socket.IO to Flask
     ├─ Receives 'rl-update'
     ├─ Calls updateFromRL()
     └─ Updates Zustand
```

---

## 🔑 Key Variables

| Variable | Type | Range | What It Means |
|----------|------|-------|----------------|
| `step` | int | 0-350 | Current step number |
| `position` | [int, int] | [0-14, 0-14] | Grid position (x, y) |
| `passengers` | int | 0-50 | How many people on bus |
| `money` | float | 0+ | Total earnings (TSh) |
| `speed` | float | 0-2 | Movement speed multiplier |
| `action` | int | 0-4 | Action taken (0=Move, 1=Pickup, 2=Dropoff, 3=Stop, 4=SpeedUp) |
| `reward` | float | -∞ to +∞ | Reward from last step |
| `total_reward` | float | -∞ to +∞ | Cumulative reward |
| `light_red` | 0\|1 | 0 or 1 | Red light active? |
| `police_here` | 0\|1 | 0 or 1 | Police checkpoint? |
| `must_stop` | 0\|1 | 0 or 1 | Must stop flag |
| `terminated` | bool | true\|false | Episode finished? |

---

## 🚨 Quick Troubleshooting

```
PROBLEM: "Cannot get http://localhost:5000"
└─→ FIX: Start Flask: python flask_api.py

PROBLEM: "WebSocket connection refused"
└─→ FIX: Check Flask port (5000) open and running

PROBLEM: "HUD shows Disconnected"
└─→ FIX: Check browser console for errors, reload page

PROBLEM: "Bus doesn't move"
└─→ FIX: 
   1. Check: socket.emit('get-state') in console
   2. Verify: useGameStore.getState() shows position changing
   3. Debug: Check 3D coordinate conversion

PROBLEM: "Multiple tabs out of sync"
└─→ FIX: They SHOULD be in sync (that's the feature!)
   └─ If not: Check socketio.emit(..., broadcast=True)

PROBLEM: "Episode doesn't start"
└─→ FIX: Load model first via /api/load-model endpoint
```

---

## 📱 Mobile/Network Access

### From Same Machine
```
Browser: http://localhost:5173  ✓ Works
```

### From Same Network
```
Find IP: ipconfig (Windows)
Replace: http://YOUR_IP:5173

Browser: http://192.168.1.5:5173  ✓ Works
```

### From Different Network (Internet)
```
Use: Ngrok or similar tunneling
ngrok http 5000
ngrok http 5173

Then share tunnel URL
```

---

## 🎓 Important Concepts

1. **WebSocket** = Real-time bidirectional connection
2. **Broadcast** = Send to ALL connected clients at once
3. **Zustand** = React state management (like Redux, but simpler)
4. **Socket.IO** = WebSocket library with automatic reconnection
5. **Grid Coordinates** = [0-14, 0-14] (integer positions)
6. **World Coordinates** = 3D coordinates for Three.js
7. **Lerp** = Linear interpolation (smooth animation between values)
8. **HUD** = Heads-Up Display (UI overlay showing game stats)

---

## ⚡ Performance Baseline

```
Network Overhead: ~150 bytes per state update (gzipped)
Update Frequency: Every 500ms (2 per second)
Data Rate: ~300 bytes/sec = 0.3 KB/sec
Per Minute: ~18 KB
Per 5-min Episode: ~90 KB

For 10 simultaneous users:
Per Episode: ~900 KB total

Negligible. No bandwidth issues.
```

---

## 🎬 Example Session

```
Developer:
  T=0:   python flask_api.py (Backend running)
  T=1:   npm run dev (Frontend running)

User:
  T=2:   Open http://localhost:5173
  T=3:   See bus at [7, 7], HUD shows "Connected"
  T=4:   Browser console: fetch /api/load-model → PPO
  T=5:   Browser console: socket.emit('start-episode')
  T=6:   See episode started, HUD updated
  T=7:   Browser console: setInterval(() => socket.emit('step'), 500)
  T=8:   Watch bus move on road, HUD update
  T=9-356: Bus driving, picking up passengers, avoiding hazards
  T=357: Episode finished (350 steps reached)
  T=358: See "Episode Complete" summary
  T=359: Click "Start New Episode"

Total Time: ~6 minutes
Result: Watched AI navigate Daladala safely!
```

---

## 📚 Documentation Map

```
📖 INTEGRATION_COMPLETE_SUMMARY.md
   └─ TL;DR + quick verification

📖 PRACTICAL_IMPLEMENTATION_GUIDE.md
   └─ Step-by-step how-to + debugging

📖 INTEGRATION_FLOW_GUIDE.md
   └─ Complete technical architecture

📖 INTEGRATION_BEST_PRACTICES.md
   └─ Patterns + performance + edge cases

📖 PYGAME_VS_WEBSOCKET.md
   └─ Why web 3D is better than pygame

📖 INTEGRATION_DOCUMENTATION_INDEX.md
   └─ Navigation + learning paths

📖 THIS FILE (CHEAT SHEET)
   └─ One-page visual summary
```

---

## ✨ Summary

**Flask + WebSocket + React = Real-time 3D Multi-viewer Experience**

1. Backend loads trained model
2. Frontend connects via Socket.IO
3. Each step: Backend calculates → Broadcasts state → All clients render
4. Result: Multiple browsers watch same episode perfectly synced
5. No pygame needed
6. Beautiful 3D visualization
7. Real-time HUD updates
8. Network-native architecture

**Status:** ✅ Complete and ready to run

---

*Last Updated: November 21, 2025*
*Quick Reference Card*

