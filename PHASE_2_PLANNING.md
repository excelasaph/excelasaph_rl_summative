# Phase 2 Planning: 3D Render Integration with RL Project

**Date:** November 20, 2025  
**Status:** Planning Phase (Ready for Implementation)

---

## 🎨 Design Preservation Principle

**IMPORTANT:** The 3D rendering design is beautiful and complete. We are NOT redesigning visuals.
- ✅ Keep Road.tsx exactly as is
- ✅ Keep Environment.tsx lighting and atmosphere
- ✅ Keep Props.tsx objects and placement
- ✅ Keep all visual effects (post-processing, materials, etc.)
- ✅ Keep camera system and movement
- ⚠️ UPDATE ONLY: Data flow, state logic, and action mappings
- ⚠️ UPDATE ONLY: How data flows from Flask → Zustand → Components

**Philosophy:** Feed it the right data, keep the beautiful rendering.

---

## 🎯 Strategic Decisions Made

### 1. ✅ API Method: **WebSocket (with Flask)**
- **Rationale:** Real-time updates, lower latency, scalable for future features
- **Implementation:** Add WebSocket support to Flask API
- **Approach:** Use `flask-socketio` for WebSocket handling
- **Data Flow:** Python RL Agent → WebSocket → 3D Render (live visualization)

### 2. ✅ Action System: **Redesign HUD for 5 Actions**
- **Rationale:** Authentic to your actual RL system, no force-mapping confusion
- **Your 5 Actions:**
  ```
  0: Move         (Continue/Progress)
  1: Pickup       (Collect passengers at stop)
  2: Dropoff      (Release passengers at stop)
  3: Stop         (Wait/Brake for hazards)
  4: SpeedUp      (Accelerate)
  ```
- **Implementation:** Update HUD to show these actual actions with visual clarity
- **Visuals:** Each action gets distinct color/icon/animation

### 3. ✅ Environment: **Linear Road (MVP)**
- **Rationale:** Keep existing beautiful road design, update only the data it consumes
- **Grid to Linear Mapping:** Position (x, y) on grid → Z-position on road
  - Road length: 29 cells (15 right + 14 up) = 29 segments
  - Bus moves along Z-axis from start to end
  - Stops/hazards rendered using existing visual system
- **Important:** Road.tsx rendering stays identical - NO visual changes
- **Future Enhancement:** Can expand to isometric 3D grid representation later without touching current Road

---

## 📋 Detailed Implementation Roadmap

### **Key Principle: Data Layer Only**

We are updating the DATA FLOW and LOGIC, NOT the visual design.

```
BEFORE (Current):
├── Scene.tsx (mock RL data)
├── useGameStore (8-action system)
├── HUD.tsx (displays mock data)
└── Road.tsx, Daladala.tsx, Props.tsx (render visuals)

AFTER (Phase 3):
├── Flask API (WebSocket events)
├── useRLConnection.ts (Socket.IO client)
├── useGameStore (5-action system + state mapping)
├── HUD.tsx (displays real RL data)
└── Road.tsx, Daladala.tsx, Props.tsx (same visuals, real data)
```

The rendering layer is untouched. We're just feeding it real data instead of mock data.

### **Phase 2a: Backend Modifications (Flask)**

#### File: `flask_api.py`

**2a.1 - Add WebSocket Support**
- Install: `pip install flask-socketio python-socketio python-engineio`
- Import socketio
- Initialize SocketIO with Flask app
- Configure CORS for WebSocket

**2a.2 - Create WebSocket Event Handlers**
- `@socketio.on('connect')` - Client connects to visualization
- `@socketio.on('disconnect')` - Client disconnects
- `@socketio.on('start_episode')` - Begin simulation
- `@socketio.on('step')` - Execute one RL step

**2a.3 - Create WebSocket Emitters**
- `emit('rl-update', {...state...})` - Send state to connected clients
- `emit('episode-complete', {...stats...})` - Episode finished
- `emit('connection-status', {...})` - Status updates

**2a.4 - Modify Endpoints to Emit Over WebSocket**
- When `/api/step` is called, also emit via WebSocket
- Allow both HTTP and WebSocket modes

#### Tasks:
```
[ ] Install flask-socketio dependencies
[ ] Add SocketIO initialization to Flask
[ ] Create WebSocket event handlers
[ ] Create state serialization function for WebSocket
[ ] Test WebSocket connection locally
[ ] Document WebSocket API
```

---

### **Phase 2b: Frontend State Management Updates**

#### File: `3d-render/src/store/gameStore.ts`

**2b.1 - Update State Interface for 5 Actions**
```typescript
export interface RLState {
  action: number;          // 0-4 (our 5 actions)
  passengers: number;      // Current passengers onboard
  capacity: number;        // Bus capacity (50)
  money: number;           // Money earned
  speed: number;           // Current speed
  position: [number, number];  // (x, y) grid position
  light_red: boolean;      // Traffic light status
  police_here: boolean;    // Police checkpoint here?
  must_stop: boolean;      // Must stop now?
  fined: boolean;          // Agent was fined?
  hazards: Array<[number, number, string]>;  // [[x,y,'police'|'light'], ...]
  step: number;            // Current step count
  terminated: boolean;     // Episode over?
  reward: number;          // Last step reward
  total_reward: number;    // Cumulative reward
  episode: number;         // Episode number
}
```

**2b.2 - Action Definitions**
```typescript
export const ACTION_NAMES: Record<number, { en: string; sw: string }> = {
  0: { en: 'Move', sw: 'Endelea' },
  1: { en: 'Pickup', sw: 'Chukua' },
  2: { en: 'Dropoff', sw: 'Buzezesha' },
  3: { en: 'Stop', sw: 'Simama' },
  4: { en: 'SpeedUp', sw: 'Ongeza Kasi' },
};

export const ACTION_COLORS: Record<number, string> = {
  0: '#3B82F6',  // Blue - Move
  1: '#10B981',  // Green - Pickup
  2: '#F59E0B',  // Amber - Dropoff
  3: '#EF4444',  // Red - Stop
  4: '#8B5CF6',  // Purple - SpeedUp
};
```

#### Tasks:
```
[ ] Update RLState interface
[ ] Add ACTION_NAMES with 5 actions
[ ] Add ACTION_COLORS for visual distinction
[ ] Update updateFromRL() to handle new state
[ ] Add field mappings from Flask to store
```

---

### **Phase 2c: API Connection Hook**

#### File: `3d-render/src/hooks/useRLConnection.ts`

**2c.1 - Replace WebSocket Hook with Socket.IO**
- Current: Raw WebSocket
- New: Socket.IO client library (handles reconnection, events better)
- Install: `npm install socket.io-client`

**2c.2 - Event Listeners**
```typescript
socket.on('rl-update', (data) => {
  // Update game state
  updateFromRL(data);
});

socket.on('episode-complete', (stats) => {
  // Handle episode completion
  handleEpisodeComplete(stats);
});

socket.on('connection-status', (status) => {
  // Update connection indicator
  setConnectionStatus(status);
});
```

**2c.3 - Event Emitters (3D to Backend)**
```typescript
socket.emit('start_episode', {});
socket.emit('step', { action: agentAction });
socket.emit('reset', {});
```

#### Tasks:
```
[ ] Install socket.io-client
[ ] Replace raw WebSocket with Socket.IO
[ ] Create event listener for 'rl-update'
[ ] Create event listener for 'episode-complete'
[ ] Create event emitter for 'step'
[ ] Add automatic reconnection logic
[ ] Add connection status feedback
```

---

### **Phase 2d: HUD Redesign for 5 Actions**

#### File: `3d-render/src/components/game/HUD.tsx`

**2d.1 - Remove 8-Action Bribe System**
- Remove bribe_offered display
- Remove "Accept Bribe"/"Reject Bribe" logic
- Remove legal_capacity comparison (replace with simple passenger count)

**2d.2 - Add 5-Action Display**
```typescript
// Current Action Display
- Large card showing action name + Swahili
- Color-coded by ACTION_COLORS
- Icon/emoji for each action

// Action History (Optional)
- Last 5 actions taken
- With rewards for each
```

**2d.3 - Update State Displays**
- Passengers: `{passengers} / {capacity}` with progress bar
- Money: Earned (TSh format)
- Speed: Current speed value
- Position: Current grid position (x, y)
- Hazard Status: Show light_red, police_here, must_stop indicators
- Step Counter: Current step / max steps (350)

**2d.4 - Add Environmental Feedback**
```
If light_red → "🚦 Red Light Ahead"
If police_here → "🚨 Police Checkpoint"
If must_stop → "⚠️ MUST STOP NOW"
If passengers > capacity → "⛔ OVERLOADED!"
```

#### Tasks:
```
[ ] Remove bribe system from HUD
[ ] Remove 8 action references
[ ] Add 5-action display with colors/icons
[ ] Add hazard status indicators
[ ] Add step counter
[ ] Add position display
[ ] Update passenger overflow indicator
[ ] Test all state updates render correctly
```

---

### **Phase 2e: Bus Movement Logic**

#### File: `3d-render/src/components/game/Daladala.tsx`

**⚠️ Design Stays the Same - Logic Only**
The bus 3D model and animations are perfect as-is. We're only updating:
- Where position data comes from (state instead of mock)
- How position translates to movement
- How animations trigger based on actions

**2e.1 - Update Position Data Source**
```typescript
// BEFORE: Uses mock/internal state
// AFTER: Consumes position from Zustand store

const { position, passengers, action } = useGameStore();

// Map grid position (x, y) → current 3D position
const currentWorldPos = gridToWorldPosition(position[0], position[1]);
```

**2e.2 - Smooth Movement (Already in Place)**
- Current animation/interpolation logic remains
- Just feed it real position data instead of mock
- Visual smoothing/easing stays the same
- Bus model and animations untouched

**2e.3 - Action-Based Triggers (Logic Only)**
```typescript
// Trigger animations based on action (visual effect already exists)
if (action === 1) triggerPickupAnimation();  // Already implemented
if (action === 2) triggerDropoffAnimation(); // Already implemented
if (action === 3) triggerBrakeEffect();       // Already implemented
if (action === 4) triggerSpeedupEffect();     // Already implemented
```

#### Tasks:
```
[ ] Connect position from Zustand store
[ ] Connect action from Zustand store
[ ] Map grid coordinates to existing animation system
[ ] Verify animations trigger on correct actions
[ ] Test smooth movement along road
[ ] NO changes to bus model or 3D assets
```

---

### **Phase 2f: Environment Updates**

#### File: `3d-render/src/components/game/Props.tsx` + `Road.tsx`

**⚠️ IMPORTANT: Visual Design Unchanged**
- Road.tsx stays exactly as is - keep all visuals
- Props.tsx stays exactly as is - keep all 3D objects
- We are NOT redesigning the environment visually

**2f.1 - Data Binding Only (No Visual Changes)**
- The hazards array from state updates component properties
- Position updates cause bus to move (visuals already handle it)
- No changes to Road geometry, materials, or rendering
- No changes to Props placement or appearance
- Logic layer only - pass data to existing components

**2f.2 - State Flow (Not Visual Changes)**
- Subscribe to state changes from Zustand
- Pass `hazards` array as props (already implemented)
- Pass `position` as props (already implemented)
- Pass `passengers` to affect bus appearance (if implemented)
- The rendering pipeline remains untouched

**2f.3 - What Actually Changes**
- How data gets INTO the components (from Zustand vs mock)
- How frequently components re-render (based on state updates)
- NO changes to: geometry, materials, cameras, effects, animations

#### Tasks:
```
[ ] NO visual changes to Road.tsx
[ ] NO model changes to Props.tsx
[ ] Update Daladala.tsx to consume position/passengers from state
[ ] Ensure components re-render on state updates
[ ] Test that rendering stays smooth
[ ] Verify no performance regression
```

---

### **Phase 2g: Camera & Controls**

#### File: `3d-render/src/components/game/CameraController.tsx`

**2g.1 - Camera Modes (Keep Existing)**
- Chase Cam (behind bus)
- Driver POV (from bus cabin)
- Top-Down (overhead view)
- Cinematic (auto flyby)

**2g.2 - Road-Aware Positioning**
- Update camera to follow bus along linear road
- Adjust camera for Z-axis movement instead of mixed directions

#### Tasks:
```
[ ] Test camera follows bus on linear road
[ ] Adjust camera distance/angle for road layout
[ ] Verify all 4 camera modes work
```

---

### **Phase 2h: Testing & Integration**

#### Local Testing Setup:

**2h.1 - Backend Testing**
```bash
# Terminal 1: Start Flask with WebSocket
cd /path/to/project
python flask_api.py

# Terminal 2: Test WebSocket connection
# Use websocket client or browser console
```

**2h.2 - Frontend Testing**
```bash
# Terminal 3: Start 3D render dev server
cd 3d-render
npm run dev

# Open http://localhost:5173
# Check browser console for connection status
```

**2h.3 - Integration Test**
- Load Flask API
- Load 3D render on browser
- Verify WebSocket connection established
- Load model via API
- Watch 3D visualization update in real-time
- Run episode and watch bus move

#### Tasks:
```
[ ] Test WebSocket connection establishment
[ ] Test state updates over WebSocket
[ ] Test bus position updates
[ ] Test action display
[ ] Test hazard visualization
[ ] Test camera controls
[ ] Run full episode start-to-finish
[ ] Verify rewards display correctly
```

---

## 🔧 Technical Specifications

### WebSocket Data Format

**From Backend (Flask) to Frontend (3D Render):**
```json
{
  "type": "rl-update",
  "data": {
    "action": 0,
    "passengers": 15,
    "capacity": 50,
    "money": 45000,
    "speed": 2.5,
    "position": [5, 10],
    "light_red": false,
    "police_here": false,
    "must_stop": false,
    "fined": false,
    "hazards": [
      [3, 8, "police"],
      [7, 6, "light"]
    ],
    "step": 42,
    "terminated": false,
    "reward": 15.3,
    "total_reward": 450.8,
    "episode": 3
  }
}
```

**From Frontend (3D Render) to Backend (Flask):**
```json
{
  "type": "step",
  "action": 1
}
```

### State Mapping: Flask → Zustand

| Flask Field | Zustand Field | Type | Notes |
|------------|---------------|------|-------|
| `x, y` | `position` | `[number, number]` | Grid coordinates |
| `passengers` | `passengers` | `number` | Onboard count |
| `capacity` | `capacity` | `number` | Bus max capacity |
| `money` | `money` | `number` | TSh earned |
| `speed` | `speed` | `number` | Current speed |
| `light_red` | `light_red` | `boolean` | Traffic light status |
| `police_here` | `police_here` | `boolean` | Police checkpoint |
| `must_stop` | `must_stop` | `boolean` | Must stop flag |
| `fined` | `fined` | `boolean` | Fine status |
| `hazards` | `hazards` | `Array` | Hazard positions |
| `step` | `step` | `number` | Episode step |
| `terminated` | `terminated` | `boolean` | Episode end |
| N/A | `action` | `number` | Last action taken |
| N/A | `reward` | `number` | Last step reward |
| N/A | `total_reward` | `number` | Cumulative reward |
| N/A | `episode` | `number` | Episode count |

---

## 📦 Dependencies to Add

### Backend (Flask):
```bash
pip install flask-socketio python-socketio python-engineio python-dotenv
```

### Frontend (3D Render):
```bash
npm install socket.io-client
```

---

## 📊 Implementation Timeline

| Phase | Task | Duration | Dependency |
|-------|------|----------|------------|
| 2a | WebSocket Backend Setup | 2-3 hours | None |
| 2b | State Management Update | 1-2 hours | 2a |
| 2c | Connection Hook | 1.5 hours | 2a, 2b |
| 2d | HUD Redesign | 2-3 hours | 2b, 2c |
| 2e | Bus Movement Logic | 2-3 hours | 2b, 2c |
| 2f | Environment Updates | 1.5-2 hours | 2b, 2c |
| 2g | Camera/Controls | 1 hour | 2e |
| 2h | Integration Testing | 2-3 hours | All |

**Total Estimated Time:** 13.5 - 18.5 hours

---

## ✅ Success Criteria

### MVP Definition (Rendering Design Preserved):
- [x] WebSocket connection established between Flask and 3D render
- [x] Real-time state updates flowing correctly
- [x] 5 actions displayed correctly in HUD
- [x] Bus position updates with grid movement using existing visuals
- [x] Episode can run start-to-finish in 3D
- [x] Rewards display correctly
- [x] NO visual regressions - Road.tsx looks identical
- [x] NO console errors
- [x] Smooth 30+ FPS performance with real data

### Nice-to-Have:
- Additional state displays
- Statistics dashboard
- Replay functionality
- (Visual enhancements only after logic is solid)

---

## 🎯 Next Steps (Phase 3: Implementation)

Once Phase 2 planning is approved:

1. **Start 2a:** Add WebSocket support to Flask
2. **Parallel 2b:** Update Zustand store for 5 actions
3. **Then 2c:** Implement connection hook
4. **Then 2d:** Redesign HUD
5. **Then 2e & 2f:** Update environment rendering
6. **Finally 2h:** Integration testing

---

## 📝 Notes

- All changes are **additive** - not removing existing good code
- WebSocket allows live monitoring - can pause/resume episodes
- 5-action display is more authentic to RL research
- Linear road is MVP - can enhance to grid later
- Keep iterating and testing throughout
- Each phase has clear deliverables

---

**Status:** ✅ Ready for Phase 3 Implementation  
**Next Review:** After Phase 2a (WebSocket Backend) complete
