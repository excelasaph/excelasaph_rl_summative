import { useRef, useState, useEffect, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGameStore, RLAction } from '@/store/gameStore';
import { gridToWorld } from '@/lib/gridToWorld';
import * as THREE from 'three';

// --- Types ---
type PassengerState = 'waiting' | 'boarding' | 'alighting' | 'walking_away';

interface PassengerData {
  id: string;
  position: THREE.Vector3;
  target: THREE.Vector3;
  state: PassengerState;
  color: string;
  speed: number;
  delay: number; // Delay before starting to move
}

// --- Individual Passenger Mesh ---
const Passenger = ({ data }: { data: PassengerData }) => {
  const groupRef = useRef<THREE.Group>(null);
  const [opacity, setOpacity] = useState(1);

  useFrame((state, delta) => {
    if (!groupRef.current) return;

    // 1. Movement Logic
    if (data.state === 'boarding' || data.state === 'alighting' || data.state === 'walking_away') {
      if (data.delay > 0) {
        data.delay -= delta;
        return;
      }

      const dist = groupRef.current.position.distanceTo(data.target);
      
      if (dist > 0.5) {
        // Move towards target
        const dir = new THREE.Vector3().subVectors(data.target, groupRef.current.position).normalize();
        groupRef.current.position.add(dir.multiplyScalar(data.speed * delta));
        
        // Face target
        groupRef.current.lookAt(data.target.x, groupRef.current.position.y, data.target.z);
      } else {
        // Reached target
        if (data.state === 'boarding') {
          // Disappear into bus
          setOpacity(Math.max(0, opacity - delta * 5));
        } else if (data.state === 'walking_away') {
           // Fade out
           setOpacity(Math.max(0, opacity - delta * 2));
        }
      }
    }

    // 2. Animation (Bobbing)
    const bobFreq = data.state === 'waiting' ? 2 : 10; // Walk faster than idle
    const bobAmp = data.state === 'waiting' ? 0.05 : 0.1;
    groupRef.current.position.y = data.position.y + Math.sin(state.clock.elapsedTime * bobFreq + parseInt(data.id)) * bobAmp;
    
    // Update scale for disappearance
    if (opacity < 1) {
        groupRef.current.scale.setScalar(opacity);
    }
  });

  return (
    <group ref={groupRef} position={data.position}>
      {/* Head */}
      <mesh position={[0, 1.6, 0]} castShadow>
        <sphereGeometry args={[0.15, 8, 8]} />
        <meshStandardMaterial color="#8d5524" />
      </mesh>
      
      {/* Body */}
      <mesh position={[0, 1.1, 0]} castShadow>
        <cylinderGeometry args={[0.15, 0.2, 0.8, 8]} />
        <meshStandardMaterial color={data.color} />
      </mesh>
      
      {/* Legs (Simple block) */}
      <mesh position={[0, 0.4, 0]} castShadow>
        <cylinderGeometry args={[0.12, 0.12, 0.8, 8]} />
        <meshStandardMaterial color="#111111" />
      </mesh>
    </group>
  );
};

// --- Main System ---
export const PassengerSystem = () => {
  const { action, position, high_demand_stops } = useGameStore();
  const [passengers, setPassengers] = useState<PassengerData[]>([]);
  const prevAction = useRef<number>(0);

  // Initialize waiting passengers at stops
  useEffect(() => {
    const initialPassengers: PassengerData[] = [];
    
    high_demand_stops.forEach((stopPos, idx) => {
      const worldPos = gridToWorld(stopPos[0], stopPos[1]);
      
      // Calculate stop offset (same logic as BusStops.tsx)
      let offset = [0, 0, 0];
      if (stopPos[1] === 14) offset = [5, 0, -12]; // Horizontal
      else offset = [12, 0, 5]; // Vertical

      const stopCenter = new THREE.Vector3(
        worldPos[0] + offset[0], 
        0, 
        worldPos[2] + offset[2]
      );

      // Create 3-5 waiting passengers per stop
      const count = 3 + Math.floor(Math.random() * 3);
      for (let i = 0; i < count; i++) {
        // Random position around stop
        const angle = Math.random() * Math.PI * 2;
        const radius = 1 + Math.random() * 2;
        const pos = new THREE.Vector3(
          stopCenter.x + Math.cos(angle) * radius,
          0,
          stopCenter.z + Math.sin(angle) * radius
        );

        initialPassengers.push({
          id: `waiting-${idx}-${i}`,
          position: pos,
          target: pos, // Waiting, so target is self
          state: 'waiting',
          color: `hsl(${Math.random() * 360}, 70%, 50%)`,
          speed: 0,
          delay: 0
        });
      }
    });

    setPassengers(initialPassengers);
  }, [high_demand_stops]);

  // Handle Actions (Pickup/Dropoff)
  useEffect(() => {
    if (action === prevAction.current) return;

    const busWorldPos = gridToWorld(position[0], position[1]);
    const busVec = new THREE.Vector3(busWorldPos[0], 0, busWorldPos[2]);
    
    // Bus "Door" is roughly where the bus is
    // We can add a slight offset to make it look like the side
    // Horizontal (y=14): Bus moves +X. Door is on -Z side (Right side of road).
    // Vertical (x=14): Bus moves +Z. Door is on +X side.
    let doorOffset = new THREE.Vector3(0, 0, 2); // Default
    if (position[1] === 14) doorOffset = new THREE.Vector3(0, 0, 2);
    else doorOffset = new THREE.Vector3(-2, 0, 0);
    
    const doorPos = busVec.clone().add(doorOffset);

    if (action === RLAction.PICKUP) {
      // Find nearest waiting passengers
      setPassengers(prev => {
        return prev.map(p => {
          if (p.state === 'waiting') {
            const dist = p.position.distanceTo(busVec);
            if (dist < 15) { // If close to bus (within 15 units)
              return {
                ...p,
                state: 'boarding',
                target: doorPos,
                speed: 4 + Math.random() * 2, // Random walk speed
                delay: Math.random() * 1.0 // Random start delay
              };
            }
          }
          return p;
        });
      });
    } 
    else if (action === RLAction.DROPOFF) {
      // Spawn new passengers alighting
      const newPassengers: PassengerData[] = [];
      const count = 2 + Math.floor(Math.random() * 3);
      
      for (let i = 0; i < count; i++) {
        // Target: Random point on sidewalk (away from road)
        // Simple logic: Move 5-8 units away from door
        const angle = Math.random() * Math.PI * 2;
        const target = doorPos.clone().add(new THREE.Vector3(
            Math.cos(angle) * 8, 
            0, 
            Math.sin(angle) * 8
        ));

        newPassengers.push({
          id: `alighting-${Date.now()}-${i}`,
          position: doorPos.clone(), // Start at door
          target: target,
          state: 'walking_away',
          color: `hsl(${Math.random() * 360}, 70%, 50%)`,
          speed: 3 + Math.random() * 2,
          delay: i * 0.5 // Staggered exit
        });
      }
      
      setPassengers(prev => [...prev, ...newPassengers]);
    }

    prevAction.current = action;
  }, [action, position]);

  // Cleanup finished passengers
  useFrame(() => {
    // Ideally we'd filter out passengers who are done (opacity 0)
    // But for simplicity in this loop we just let them stay invisible or handle it periodically
    // To avoid performance issues with thousands of objects, we should clean up
    if (Math.random() < 0.01) { // Occasional cleanup
       setPassengers(prev => prev.filter(p => {
           // Keep if waiting
           if (p.state === 'waiting') return true;
           // Keep if moving (distance to target > 0.5)
           if (p.position.distanceTo(p.target) > 0.6) return true;
           // Remove if finished boarding/walking away
           return false;
       }));
    }
  });

  return (
    <group>
      {passengers.map(p => (
        <Passenger key={p.id} data={p} />
      ))}
    </group>
  );
};
