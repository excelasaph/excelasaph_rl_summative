# 🚐 Daladala: The Corruption Dilemma

A stunning, AAA-quality 3D reinforcement learning visualization of Dar es Salaam's daladala (minibus) transportation system, built with React Three Fiber.

![Daladala Banner](https://images.unsplash.com/photo-1464037866556-6812c9d1c72e?w=1200&h=400&fit=crop)

## 🌟 Features

### Visual Fidelity
- **Photorealistic African sunset lighting** with HDR environment
- **PBR materials** with realistic wear and reflections
- **Post-processing effects**: Bloom, depth of field, vignette, film grain
- **Volumetric atmosphere** with fog and dynamic clouds
- **60 FPS performance** optimized for desktop and mobile

### Authentic Dar es Salaam Experience
- Classic yellow Toyota HiAce daladala with blue/red/white racing stripes
- African urban environment: palm trees, buildings, signage
- Swahili UI elements and translations
- Cultural details: "Jesus is My Boss" stickers, overloaded passengers

### Interactive Elements
- **50+ animated passengers** that react to overcrowding
- **Dynamic bus stops** at Morocco, Kariakoo, Ubungo
- **Police checkpoints** with visual feedback
- **Traffic systems** with realistic behavior
- **Bribe mechanics** with visual cash hand-off

### Camera System
Press keyboard numbers to switch views:
- **1** - Chase Cam (cinematic third-person)
- **2** - Driver POV (see dashboard and passengers)
- **3** - Top-Down (tactical overhead view)
- **4** - Cinematic (auto fly-around)

### RL Integration
Real-time WebSocket connection to your Python RL agent:
```json
{
  "action": 0-7,
  "passengers": 42,
  "money": 124000,
  "must_stop_next": true,
  "bribe_offered": true,
  "terminated": false,
  "reward": 15.3
}
```

## 🎮 Actions

| Action | English | Swahili |
|--------|---------|---------|
| 0 | Accelerate | Ongeza Kasi |
| 1 | Brake | Simamisha |
| 2 | Stop & Pick | Simama Chukua |
| 3 | Accept Bribe | Pokea Rushwa |
| 4 | Reject Bribe | Kataa Rushwa |
| 5 | Run Red Light | Pita Nyekundu |
| 6 | Wait at Light | Ngoja Taa |
| 7 | Continue | Endelea |

## 🔌 Connecting Your Python RL Agent

### Option 1: WebSocket (Recommended)

Update your Python agent to send data via WebSocket:

```python
import asyncio
import websockets
import json

async def send_rl_data(uri="ws://localhost:8080/rl"):
    async with websockets.connect(uri) as websocket:
        while True:
            # Your RL agent step
            obs, reward, terminated, truncated, info = env.step(action)
            
            # Send to visualization
            data = {
                "action": int(action),
                "passengers": int(info.get('passengers', 0)),
                "money": int(info.get('money', 0)),
                "must_stop_next": bool(info.get('must_stop_next', False)),
                "bribe_offered": bool(info.get('bribe_offered', False)),
                "terminated": terminated or truncated,
                "reward": float(reward)
            }
            
            await websocket.send(json.dumps(data))
            await asyncio.sleep(0.1)  # 10 FPS update rate

asyncio.run(send_rl_data())
```

### Option 2: HTTP Polling

Or use simple HTTP requests:

```python
import requests
import time

def update_visualization(data):
    requests.post('http://localhost:8080/api/rl-update', json=data)

while True:
    obs, reward, terminated, truncated, info = env.step(action)
    
    update_visualization({
        "action": int(action),
        "passengers": int(info['passengers']),
        "money": int(info['money']),
        "reward": float(reward),
        # ... other fields
    })
    
    time.sleep(0.1)
```

## 🚀 Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Then open [http://localhost:8080](http://localhost:8080)

### Production Build

```bash
npm run build
npm run preview
```

## 🎨 Design System

The project uses a warm African sunset color palette:

- **Primary**: Sunset orange (#E67E22)
- **Secondary**: Daladala yellow (#FFD700)
- **Success**: TSh green (#2ECC71)
- **Destructive**: Fine red (#E74C3C)
- **Atmosphere**: Dusty amber with deep blue sky gradients

All colors use HSL format and are defined in `src/index.css`.

## 📊 Performance Optimization

- **Instanced rendering** for repeated elements (passengers, trees)
- **LOD system** for distant objects
- **Baked lighting** where possible
- **Efficient post-processing** with selective effects
- **Lazy loading** for heavy assets

Target: **60 FPS on mid-range laptops**

## 🎯 Easter Eggs

- When agent **rejects bribe** → passengers clap and cheer
- When agent runs **perfectly legal** (≤33 passengers) → confetti + "Mungu akubariki!" text
- **Speedometer** needle animated with engine sound pitch
- **Dust kick-up** when hard accelerating
- **Night mode** transitions with working headlights

## 🔧 Tech Stack

- **React 18** + TypeScript
- **React Three Fiber** (Three.js for React)
- **@react-three/drei** (3D helpers)
- **@react-three/rapier** (Physics engine)
- **@react-three/postprocessing** (Visual effects)
- **Zustand** (State management)
- **Tailwind CSS** (UI styling)
- **shadcn/ui** (UI components)

## 📝 Project Structure

```
src/
├── components/
│   ├── game/
│   │   ├── Scene.tsx          # Main 3D canvas
│   │   ├── Daladala.tsx       # Hero vehicle
│   │   ├── Environment.tsx    # Lighting & sky
│   │   ├── Road.tsx           # Tarmac & dirt roads
│   │   ├── Props.tsx          # Buildings, trees, stops
│   │   ├── CameraController.tsx
│   │   └── HUD.tsx            # UI overlay
├── store/
│   └── gameStore.ts           # Zustand state
├── hooks/
│   └── useRLConnection.ts     # WebSocket hook
└── pages/
    └── Index.tsx              # Entry point
```

## 🌍 Cultural Authenticity

This project respects and celebrates Tanzanian culture:
- **Swahili language** integrated throughout
- **Real daladala aesthetics** (colors, decorations, overloading)
- **Dar es Salaam landmarks** (Kariakoo, Ubungo, Posta)
- **East African sunset** atmosphere
- **Bongo Flava music** references in audio design

## 🤝 Contributing

This is a visualization tool for RL research. Contributions welcome:
- Enhanced 3D models (photogrammetry)
- More authentic African props
- Additional camera angles
- Performance optimizations
- Audio implementation

## 📄 License

MIT License - Use for research, education, or commercial projects

## 🙏 Acknowledgments

Built with ❤️ to show why reinforcement learning is the only solution to the daladala corruption-overload death trap in Tanzania.

**Mungu akubariki!** 🇹🇿

---

*"This should be a real game."* — The Goal
