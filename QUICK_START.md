# Quick Start - Run Everything

## 🚀 Start System (3 Steps, 2 Minutes)

### Terminal 1: Flask Backend
```bash
cd c:\Users\Excel\Desktop\Github\ Projects\excelasaph_rl_summative
python flask_api.py
```

Wait for:
```
✓ Flask API Server starting...
✓ Available at: http://localhost:5000
```

### Terminal 2: React Frontend  
```bash
cd c:\Users\Excel\Desktop\Github\ Projects\excelasaph_rl_summative\3d-render
npm run dev
```

Wait for:
```
➜  Local:   http://localhost:5173/
```

### Browser: Open & Run
```
1. Open: http://localhost:5173
2. Press F12 (open console)
3. Paste in console:

socket.emit('start-episode')

// Then repeatedly:
socket.emit('step', {})
```

Watch the HUD and bus move!

---

## ✅ Verify It's Working

**Check Flask is running:**
```bash
curl http://localhost:5000/api/health
# Should return: {"status": "ok", "message": "API Server Ready"}
```

**Check Frontend loads:**
- Open http://localhost:5173
- Should see 3D bus on road
- HUD visible (top-left corner)

**Check WebSocket connected:**
- Open console (F12)
- Should see: `✓ Connected to Flask WebSocket (Socket.IO)`

---

## 🎮 Run Full Episode

In browser console:

```javascript
// Load a model first
fetch('http://localhost:5000/api/load-model', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({algorithm: 'DQN'})
}).then(r => r.json()).then(d => console.log(d.message))

// Start watching changes
let lastPos = null
gameStore.subscribe((s) => {
  if (s.position !== lastPos) {
    console.log(`Step ${s.step}: Pos [${s.position}], Reward +${s.reward.toFixed(1)}`)
    lastPos = s.position
  }
})

// Start episode
socket.emit('start-episode')

// Run 30 steps (one every 300ms)
let i = 0
setInterval(() => {
  if (i++ < 30) socket.emit('step', {})
}, 300)
```

---

## 🧪 Run Tests

### Backend Tests
```bash
python test_integration.py
```

### Frontend Tests
```javascript
// In browser console:
runAllFrontendTests()
```

---

## 📊 What You'll See

✓ Beautiful 3D Daladala bus  
✓ Real-time HUD updates  
✓ Bus moves smoothly on road  
✓ Environmental hazards (red lights, police)  
✓ Rewards and passengers updating  
✓ Smooth 60 FPS animation  

---

## ❌ Troubleshooting

**Port 5000 already in use:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Port 5173 already in use:**
```bash
# Change Vite port in 3d-render/vite.config.ts
# Or kill process on 5173
```

**WebSocket not connecting:**
- Ensure Flask running in terminal 1
- Check browser console for errors (F12)
- Browser must be at http://localhost:5173 (exact)

**React dependencies missing:**
```bash
cd 3d-render
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 📋 Architecture Quick Reference

```
Browser (http://localhost:5173)
    ↓ Socket.IO WebSocket
Flask (http://localhost:5000)
    ↓
DaladalaEnv (15×15 grid, 5 actions)
    ↓
RL Algorithm (DQN, PPO, A2C, etc.)
```

State flows every step:
```
RL Env → Flask → WebSocket → React → Zustand → Components → Screen
```

---

## 🎯 System Components

| Component | Port | Status |
|-----------|------|--------|
| Flask Backend | 5000 | ✓ Running |
| React Frontend | 5173 | ✓ Running |
| WebSocket | 5000/socket.io | ✓ Active |
| 3D Canvas | Browser | ✓ Rendering |

---

## 📞 Common Commands

```bash
# Check Python version
python --version

# Check Node version  
node --version

# Check npm version
npm --version

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd 3d-render
npm install

# Clean frontend cache
rm -rf node_modules package-lock.json
npm install

# Kill Python processes
taskkill /F /IM python.exe

# Check Flask health
curl http://localhost:5000/api/health

# Check environment info
curl http://localhost:5000/api/environment-info
```

---

## 🎬 That's It!

You now have a fully integrated RL environment with beautiful 3D visualization.

Enjoy! 🎉

