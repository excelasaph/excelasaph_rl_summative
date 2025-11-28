# Daladala: The Corruption Dilemma

A stunning, AAA-quality 3D reinforcement learning visualization of Dar es Salaam's daladala (minibus) transportation system, built with React Three Fiber.

![Daladala Banner](https://images.unsplash.com/photo-1464037866556-6812c9d1c72e?w=1200&h=400&fit=crop)

## Features

### Visual Fidelity
- **Photorealistic African sunset lighting** with HDR environment
- **PBR materials** with realistic wear and reflections
- **Volumetric atmosphere** with fog and dynamic clouds
- **60 FPS performance** optimized for desktop and mobile

### Authentic Dar es Salaam Experience
- Classic yellow Toyota HiAce daladala
- African urban environment: palm trees, buildings, signage
- Swahili UI elements and translations
- Overloaded passenger mechanics with visual indicators

### Interactive Elements
- **Animated passengers** that board and alight based on agent actions
- **Dynamic bus stops** at Morocco, Kariakoo, Ubungo
- **Police checkpoints** and **Traffic lights** with penalty logic
- **Real-time HUD** showing speed, earnings, and passenger count

### Camera System
Press keyboard numbers or use the UI to switch views:
- **1** - Chase Cam (cinematic third-person)
- **2** - Driver POV (see dashboard and passengers)
- **3** - Top-Down (tactical overhead view)
- **4** - Cinematic (auto fly-around)

### RL Integration
Real-time WebSocket connection (Socket.IO) to the Flask RL backend:
```json
{
  "action": 0-4,
  "passengers": 42,
  "money": 124000,
  "must_stop": true,
  "terminated": false,
  "reward": 15.3
}
```

## Actions

| Action | English | Swahili | Description |
|--------|---------|---------|-------------|
| 0 | Move | Songa | Advance to next position |
| 1 | Pickup | Pakia | Load passengers at stop |
| 2 | Dropoff | Shusha | Unload passengers for revenue |
| 3 | Stop | Simama | Wait/Slow down (for hazards) |
| 4 | Speed Up | Kimbiza | Increase speed (risky) |

## Architecture

The project consists of two main parts:

1.  **Frontend (React + Three.js)**: Handles the 3D visualization, physics, and UI.
2.  **Backend (Flask + Socket.IO)**: Hosts the trained RL models (PPO, DQN, A2C, REINFORCE) and runs the simulation logic.

### Connecting Your Agent

The system is designed to run pre-trained models hosted on the Flask backend. The frontend connects via Socket.IO to:
- Start episodes
- Receive state updates
- Visualize actions

## Getting Started

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

## Design System

The project uses a warm African sunset color palette:

- **Primary**: Sunset orange (#E67E22)
- **Secondary**: Daladala yellow (#FFD700)
- **Success**: TSh green (#2ECC71)
- **Destructive**: Fine red (#E74C3C)
- **Atmosphere**: Dusty amber with deep blue sky gradients

All colors use HSL format and are defined in `src/index.css`.

## Tech Stack

- **React 18** + TypeScript
- **React Three Fiber** (Three.js for React)
- **@react-three/drei** (3D helpers)
- **@react-three/rapier** (Physics engine)
- **Socket.IO Client** (Real-time communication)
- **Zustand** (State management)
- **Tailwind CSS** (UI styling)
- **shadcn/ui** (UI components)

## Project Structure

```
src/
├── components/
│   ├── game/
│   │   ├── Scene.tsx          # Main 3D canvas
│   │   ├── Daladala.tsx       # Hero vehicle physics & mesh
│   │   ├── Environment.tsx    # Lighting, sky, clouds
│   │   ├── Road.tsx           # Procedural road generation
│   │   ├── Passengers.tsx     # Passenger system & animation
│   │   ├── HUD.tsx            # UI overlay & controls
│   │   └── Minimap.tsx        # Navigation aid
├── store/
│   └── gameStore.ts           # Zustand state
├── hooks/
│   └── useRLConnection.ts     # Socket.IO hook
└── pages/
    └── Index.tsx              # Entry point
```

## Cultural Authenticity

This project respects and celebrates Tanzanian culture:
- **Swahili language** integrated throughout
- **Real daladala aesthetics** (colors, overloading)
- **Dar es Salaam landmarks** (Kariakoo, Ubungo, Posta)
- **East African sunset** atmosphere

## License

MIT License - Use for research, education, or commercial projects

**Mungu akubariki!** 🇹🇿
