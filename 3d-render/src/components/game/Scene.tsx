import { useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { EffectComposer, Bloom, DepthOfField, Vignette, Noise } from '@react-three/postprocessing';
import { Daladala } from './Daladala';
import { DarEnvironment } from './Environment';
import { Road } from './Road';
import { SceneProps } from './Props';
import { CameraController } from './CameraController';
import { TrafficLights } from './TrafficLight';
import { Hazards } from './Hazards';
import { BusStops } from './BusStops';
import { SoundController } from './SoundController';
import { PassengerSystem } from './Passengers';
import { useGameStore } from '@/store/gameStore';
import { useRLConnection } from '@/hooks/useRLConnection';
import * as THREE from 'three';
import { Physics } from '@react-three/rapier';

export const Scene = () => {
  const daladalaRef = useRef<THREE.Group>(null);
  const { cameraMode } = useGameStore();
  
  // Initialize WebSocket connection to Flask backend
  useRLConnection('http://localhost:5000');

  return (
    <div className="fixed inset-0 bg-gradient-to-b from-game-sunset to-game-dust">
      <Canvas
        shadows
        dpr={[1, 2]} // Optimize for high-DPI screens
        camera={{ 
          position: [0, 10, 0], // Neutral position - will be overridden by CameraController
          fov: 60,
          near: 0.1,
          far: 1000
        }}
        gl={{ 
          antialias: true,
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.2,
        }}
      >
        <Physics gravity={[0, -9.81, 0]}>
          {/* Audio System */}
          <SoundController />

          {/* Environment & Lighting */}
          <DarEnvironment />

          {/* Scene Elements */}
          <Road />
          <SceneProps />
          
          {/* Dynamic Hazards & Game Elements */}
          <TrafficLights />
          <Hazards />
          <BusStops />
          <PassengerSystem />
          
          {/* Hero - The Daladala */}
          <Daladala busRef={daladalaRef} />
        </Physics>

        {/* Camera System - GTA-style camera with built-in mouse controls */}
        <CameraController targetRef={daladalaRef} />

        {/* Post-processing for AAA visual quality */}
        <EffectComposer>
          <Bloom 
            intensity={0.5}
            luminanceThreshold={0.8}
            luminanceSmoothing={0.9}
          />
          {/* DepthOfField removed for clarity */}
          <Vignette
            offset={0.3}
            darkness={0.5}
          />
          <Noise
            opacity={0.02}
          />
        </EffectComposer>
      </Canvas>
    </div>
  );
};
