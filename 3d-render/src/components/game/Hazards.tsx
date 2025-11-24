import { useGameStore, RLAction } from '@/store/gameStore';
import { gridToWorld } from '@/lib/gridToWorld';
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const PoliceCheckpoint = ({ position, rotation, isOpen }: { position: [number, number, number], rotation: number, isOpen: boolean }) => {
  const barrierRef = useRef<THREE.Group>(null);
  const copRef = useRef<THREE.Group>(null);

  useFrame((state, delta) => {
    if (barrierRef.current) {
      // Animate barrier: Closed = Y:0, Open = Y:-1.5 (Sunk into ground)
      const targetY = isOpen ? -1.5 : 0;
      barrierRef.current.position.y = THREE.MathUtils.lerp(barrierRef.current.position.y, targetY, delta * 5);
    }

    if (copRef.current) {
      // Animate Cop: Closed = Z:0 (Center of road), Open = Z:3.5 (Side of road)
      // We move along Z because the barrier is aligned along Z, so Z is the "width" of the road here
      const targetZ = isOpen ? 3.5 : 0;
      copRef.current.position.z = THREE.MathUtils.lerp(copRef.current.position.z, targetZ, delta * 3);
    }
  });

  return (
    <group position={position} rotation={[0, rotation, 0]}>
      {/* === Road Barrier (Animatable) === */}
      <group ref={barrierRef}>
        <mesh position={[0, 0.5, 0]} castShadow>
          <boxGeometry args={[0.5, 1, 4]} />
          <meshStandardMaterial color="#FF0000" roughness={0.4} />
        </mesh>
        <mesh position={[0, 0.5, 0]}>
          <boxGeometry args={[0.55, 1.05, 1]} />
          <meshStandardMaterial color="#FFFFFF" />
        </mesh>
        <mesh position={[0, 0.5, 2]}>
          <boxGeometry args={[0.55, 1.05, 1]} />
          <meshStandardMaterial color="#FFFFFF" />
        </mesh>
        <mesh position={[0, 0.5, -2]}>
          <boxGeometry args={[0.55, 1.05, 1]} />
          <meshStandardMaterial color="#FFFFFF" />
        </mesh>
      </group>

      {/* === Traffic Cones === */}
      <group position={[2, 0, 2]}>
        <mesh position={[0, 0.5, 0]} castShadow>
          <coneGeometry args={[0.3, 1, 16]} />
          <meshStandardMaterial color="#FF4500" />
        </mesh>
        <mesh position={[0, 0.05, 0]}>
          <boxGeometry args={[0.7, 0.1, 0.7]} />
          <meshStandardMaterial color="#111111" />
        </mesh>
      </group>
      <group position={[2, 0, -2]}>
        <mesh position={[0, 0.5, 0]} castShadow>
          <coneGeometry args={[0.3, 1, 16]} />
          <meshStandardMaterial color="#FF4500" />
        </mesh>
        <mesh position={[0, 0.05, 0]}>
          <boxGeometry args={[0.7, 0.1, 0.7]} />
          <meshStandardMaterial color="#111111" />
        </mesh>
      </group>

      {/* === Police Officer (Abstract) === */}
      <group ref={copRef} position={[-2, 0, 0]}>
        {/* Body */}
        <mesh position={[0, 0.9, 0]} castShadow>
          <cylinderGeometry args={[0.3, 0.3, 0.8, 8]} />
          <meshStandardMaterial color="#00008B" /> {/* Dark Blue Uniform */}
        </mesh>
        {/* Head */}
        <mesh position={[0, 1.5, 0]} castShadow>
          <sphereGeometry args={[0.2, 16, 16]} />
          <meshStandardMaterial color="#8B4513" />
        </mesh>
        {/* Hat */}
        <mesh position={[0, 1.65, 0]} castShadow>
          <cylinderGeometry args={[0.25, 0.25, 0.1, 16]} />
          <meshStandardMaterial color="#FFFFFF" />
        </mesh>
        {/* Legs */}
        <mesh position={[-0.15, 0.4, 0]} castShadow>
          <cylinderGeometry args={[0.1, 0.1, 0.8, 8]} />
          <meshStandardMaterial color="#000000" />
        </mesh>
        <mesh position={[0.15, 0.4, 0]} castShadow>
          <cylinderGeometry args={[0.1, 0.1, 0.8, 8]} />
          <meshStandardMaterial color="#000000" />
        </mesh>
      </group>
    </group>
  );
};

export const Hazards = () => {
  const { police_checkpoints, position: busPos, action } = useGameStore();

  return (
    <group>
      {police_checkpoints.map((pos, index) => {
        const worldPos = gridToWorld(pos[0], pos[1]);
        
        // Determine rotation based on road segment
        // Horizontal (Y=14): Road along X. Barrier (Length Z) is correct. Rotation 0.
        // Vertical (X=14): Road along Z. Barrier needs to be along X. Rotation 90 deg.
        const isVertical = pos[0] === 14 && pos[1] < 14;
        const rotation = isVertical ? Math.PI / 2 : 0;

        // Apply offset to align checkpoint with bus stopping position
        // Horizontal: Bus moves +X, so add to X
        // Vertical: Bus moves +Z, so add to Z
        const offset = isVertical ? [0, 0, 10] : [10, 0, 0];

        // Logic to open barrier:
        // 1. Determine the "Next Cell" after this checkpoint
        let nextCell = [pos[0], pos[1]];
        if (isVertical) {
          nextCell = [pos[0], pos[1] - 1]; // Moving Down (Y decreases)
        } else {
          nextCell = [pos[0] + 1, pos[1]]; // Moving Right (X increases)
        }

        // 2. Check if bus is AT the checkpoint or AT the next cell
        const isAtCheckpoint = busPos[0] === pos[0] && busPos[1] === pos[1];
        const isAtNextCell = busPos[0] === nextCell[0] && busPos[1] === nextCell[1];

        // 3. Open if:
        //    - Bus is at Next Cell (driving through/past barrier)
        //    - OR Bus is at Checkpoint AND Action is STOP (inspection in progress)
        //    Note: We do NOT open for MOVE/SPEED_UP at the checkpoint itself, 
        //    because that represents "Arriving" at the closed barrier.
        const isOpen = isAtNextCell || (isAtCheckpoint && action === RLAction.STOP);

        return (
          <PoliceCheckpoint 
            key={`police-${index}`} 
            position={[worldPos[0] + offset[0], worldPos[1] + offset[1], worldPos[2] + offset[2]]} 
            rotation={rotation}
            isOpen={isOpen}
          />
        );
      })}
    </group>
  );
};
