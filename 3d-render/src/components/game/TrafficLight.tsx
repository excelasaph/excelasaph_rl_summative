import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGameStore } from '@/store/gameStore';
import { gridToWorld } from '@/lib/gridToWorld';
import * as THREE from 'three';

interface TrafficLightProps {
  gridPosition: [number, number];
  rotation: number;
}

export const TrafficLight = ({ gridPosition, rotation }: TrafficLightProps) => {
  const lightRef = useRef<THREE.Group>(null);
  const { traffic_light_states, position: busPosition } = useGameStore();
  
  // Convert grid position to world position
  const worldPos = gridToWorld(gridPosition[0], gridPosition[1]);
  
  // Check if bus is at this traffic light location
  const isAtLight = busPosition[0] === gridPosition[0] && busPosition[1] === gridPosition[1];
  
  // Get state for this specific traffic light from RL environment
  // Key format matches Python: "x,y"
  const lightKey = `${gridPosition[0]},${gridPosition[1]}`;
  const lightState = traffic_light_states[lightKey];
  
  // 1 = Red, 0 = Green
  // If undefined, show Yellow (Warning/Loading) to prevent flickering
  const isRed = lightState === 1;
  const isGreen = lightState === 0;
  const isLoading = lightState === undefined;

  // Subtle animation when light is active
  useFrame((state) => {
    if (lightRef.current && isAtLight) {
      lightRef.current.position.y = worldPos[1] + Math.sin(state.clock.elapsedTime * 2) * 0.05;
    }
  });

  return (
    <group ref={lightRef} position={[worldPos[0], worldPos[1], worldPos[2]]} rotation={[0, rotation, 0]}>
      <group position={[4.5, 0, -12]}> {/* Offset pole relative to rotated group: Side + Forward */}
      {/* Vertical Pole (realistic height ~5-6 meters) */}
      <mesh position={[0, 3, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[0.12, 0.15, 6, 16]} />
        <meshStandardMaterial 
          color="#2c3e50"
          metalness={0.7}
          roughness={0.3}
        />
      </mesh>

      {/* Horizontal arm extending over road */}
      <mesh position={[-1.5, 6, 0]} rotation={[0, 0, Math.PI / 2]} castShadow receiveShadow>
        <cylinderGeometry args={[0.08, 0.08, 3, 12]} />
        <meshStandardMaterial 
          color="#2c3e50"
          metalness={0.7}
          roughness={0.3}
        />
      </mesh>

      {/* Traffic Light Housing (black box) */}
      <mesh position={[-3, 5.8, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.4, 1.2, 0.4]} />
        <meshStandardMaterial 
          color="#1a1a1a"
          metalness={0.4}
          roughness={0.6}
        />
      </mesh>

      {/* RED Light (top) */}
      <mesh position={[-3, 6.2, 0.21]}>
        <circleGeometry args={[0.15, 16]} />
        <meshStandardMaterial 
          color={isRed ? "#ff0000" : "#330000"}
          emissive={isRed ? "#ff0000" : "#000000"}
          emissiveIntensity={isRed ? 2 : 0}
          metalness={0.5}
          roughness={0.2}
        />
      </mesh>
      {/* Red light glow */}
      {isRed && (
        <pointLight 
          position={[-3, 6.2, 0.3]} 
          color="#ff0000" 
          intensity={3} 
          distance={8}
          decay={2}
        />
      )}

      {/* YELLOW Light (middle) - Active if loading/undefined */}
      <mesh position={[-3, 5.8, 0.21]}>
        <circleGeometry args={[0.15, 16]} />
        <meshStandardMaterial 
          color={isLoading ? "#ffcc00" : "#332200"}
          emissive={isLoading ? "#ffcc00" : "#000000"}
          emissiveIntensity={isLoading ? 2 : 0}
          metalness={0.5}
          roughness={0.2}
        />
      </mesh>
      {/* Yellow light glow */}
      {isLoading && (
        <pointLight 
          position={[-3, 5.8, 0.3]} 
          color="#ffcc00" 
          intensity={2} 
          distance={8}
          decay={2}
        />
      )}

      {/* GREEN Light (bottom) */}
      <mesh position={[-3, 5.4, 0.21]}>
        <circleGeometry args={[0.15, 16]} />
        <meshStandardMaterial 
          color={isGreen ? "#00ff00" : "#003300"}
          emissive={isGreen ? "#00ff00" : "#000000"}
          emissiveIntensity={isGreen ? 2 : 0}
          metalness={0.5}
          roughness={0.2}
        />
      </mesh>
      {/* Green light glow */}
      {isGreen && (
        <pointLight 
          position={[-3, 5.4, 0.3]} 
          color="#00ff00" 
          intensity={3} 
          distance={8}
          decay={2}
        />
      )}

      {/* Visor/Hood over lights (to prevent sun glare) */}
      <mesh position={[-3, 6.2, 0.15]} rotation={[Math.PI / 12, 0, 0]}>
        <boxGeometry args={[0.42, 0.05, 0.25]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>
      <mesh position={[-3, 5.8, 0.15]} rotation={[Math.PI / 12, 0, 0]}>
        <boxGeometry args={[0.42, 0.05, 0.25]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>
      <mesh position={[-3, 5.4, 0.15]} rotation={[Math.PI / 12, 0, 0]}>
        <boxGeometry args={[0.42, 0.05, 0.25]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>

      {/* Base plate on ground */}
      <mesh position={[0, 0.05, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <cylinderGeometry args={[0.5, 0.5, 0.1, 8]} />
        <meshStandardMaterial 
          color="#555555"
          metalness={0.3}
          roughness={0.7}
        />
      </mesh>

      {/* Warning stripe on pole (yellow and black) */}
      <mesh position={[0, 1, 0]}>
        <cylinderGeometry args={[0.13, 0.14, 0.3, 16]} />
        <meshStandardMaterial 
          color="#FFD700"
          roughness={0.4}
        />
      </mesh>
      </group>
    </group>
  );
};

// Component to render all traffic lights from game state
export const TrafficLights = () => {
  const { traffic_lights } = useGameStore();

  // Debug: Log when traffic lights change
  console.log('TrafficLights rendering:', traffic_lights.length, 'lights at positions:', traffic_lights);

  return (
    <group>
      {traffic_lights.map((lightPos, index) => {
        const pos = lightPos as [number, number];
        // Determine rotation based on road segment
        // Horizontal (Y=14): Road along X. Pole needs to be on side (Z offset). Rotation -90 deg.
        // Vertical (X=14): Road along Z. Pole needs to be on side (X offset). Rotation 180 deg (Face North).
        const rotation = (pos[1] === 14) ? -Math.PI / 2 : Math.PI;
        
        return (
          <TrafficLight 
            key={`traffic-light-${index}`} 
            gridPosition={pos} 
            rotation={rotation}
          />
        );
      })}
    </group>
  );
};
