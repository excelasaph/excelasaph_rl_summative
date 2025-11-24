import { useMemo } from 'react';
import * as THREE from 'three';
import { useGameStore } from '@/store/gameStore';
import { gridToWorld } from '@/lib/gridToWorld';
import { useGLTF } from '@react-three/drei';

// Palm tree component
const PalmTree = ({ position }: { position: [number, number, number] }) => {
  const { scene } = useGLTF('/palm_tree/scene.gltf');
  const clone = useMemo(() => scene.clone(), [scene]);
  
  // Memoize rotation to prevent re-randomization on re-renders
  const rotation = useMemo(() => [0, Math.random() * Math.PI, 0] as [number, number, number], []);

  return (
    <primitive 
      object={clone} 
      position={position} 
      scale={[1.815, 1.815, 1.815]} 
      rotation={rotation} 
    />
  );
};

// Simple building
const Building = ({ 
  position, 
  color = '#F4A460' 
}: { 
  position: [number, number, number];
  color?: string;
}) => (
  <group position={position}>
    <mesh castShadow>
      <boxGeometry args={[4, 8, 4]} />
      <meshStandardMaterial color={color} roughness={0.8} />
    </mesh>
    {/* Roof */}
    <mesh position={[0, 4.5, 0]} castShadow>
      <boxGeometry args={[4.2, 0.5, 4.2]} />
      <meshStandardMaterial color="#8B4513" />
    </mesh>
    {/* Windows */}
    {Array.from({ length: 3 }).map((_, floor) => 
      Array.from({ length: 2 }).map((_, side) => (
        <mesh
          key={`${floor}-${side}`}
          position={[side === 0 ? 1.5 : -1.5, -2 + floor * 2.5, 2.1]}
        >
          <planeGeometry args={[0.8, 1.2]} />
          <meshBasicMaterial color="#87CEEB" />
        </mesh>
      ))
    )}
  </group>
);

// Bus stop
export const BusStop = ({ position }: { position: [number, number, number] }) => (
  <group position={position}>
    {/* Shelter */}
    <mesh position={[0, 2, 0]} castShadow>
      <boxGeometry args={[3, 0.1, 2]} />
      <meshStandardMaterial color="#DC143C" metalness={0.5} />
    </mesh>
    {/* Support poles */}
    <mesh position={[-1.3, 1, 0]} castShadow>
      <cylinderGeometry args={[0.08, 0.08, 2, 8]} />
      <meshStandardMaterial color="#808080" metalness={0.7} />
    </mesh>
    <mesh position={[1.3, 1, 0]} castShadow>
      <cylinderGeometry args={[0.08, 0.08, 2, 8]} />
      <meshStandardMaterial color="#808080" metalness={0.7} />
    </mesh>
    {/* Bench */}
    <mesh position={[0, 0.5, 0.5]} castShadow>
      <boxGeometry args={[2.5, 0.1, 0.6]} />
      <meshStandardMaterial color="#8B4513" />
    </mesh>
    {/* Sign */}
    <mesh position={[0, 2.5, -0.8]}>
      <planeGeometry args={[2, 0.8]} />
      <meshStandardMaterial color="#FFFFFF" />
    </mesh>
  </group>
);

// Signboard
const SignBoard = ({ 
  position, 
  text = 'POSTA',
  color = '#FF0000'
}: { 
  position: [number, number, number];
  text?: string;
  color?: string;
}) => (
  <group position={position}>
    {/* Pole */}
    <mesh position={[0, 2, 0]} castShadow>
      <cylinderGeometry args={[0.1, 0.1, 4, 8]} />
      <meshStandardMaterial color="#808080" metalness={0.7} />
    </mesh>
    {/* Sign */}
    <mesh position={[0, 4.5, 0]} castShadow>
      <boxGeometry args={[2.5, 1, 0.1]} />
      <meshStandardMaterial color={color} />
    </mesh>
    {/* Text area (white) */}
    <mesh position={[0, 4.5, 0.06]}>
      <planeGeometry args={[2.2, 0.7]} />
      <meshBasicMaterial color="#FFFFFF" />
    </mesh>
  </group>
);

export const SceneProps = () => {
  const high_demand_stops = useGameStore((state) => state.high_demand_stops);

  // Generate props for the L-shaped road
  const props = useMemo(() => {
    const trees: [number, number, number][] = [];
    const buildings: { pos: [number, number, number]; color: string }[] = [];
    
    // Calculate forbidden zones based on bus stops
    // We replicate the logic from BusStops.tsx to know where they are
    const forbiddenZones: THREE.Vector3[] = high_demand_stops.map(stop => {
        const [gx, gy] = stop;
        const worldPos = gridToWorld(gx, gy);
        // Apply same offsets as BusStops.tsx
        if (gy === 14) {
            // Horizontal segment stop
            return new THREE.Vector3(worldPos[0], worldPos[1], worldPos[2] - 12);
        } else {
            // Vertical segment stop
            return new THREE.Vector3(worldPos[0] + 12, worldPos[1], worldPos[2]);
        }
    });

    // Check if a position is too close to any bus stop
    const isBlocked = (x: number, z: number) => {
        return forbiddenZones.some(zone => {
            const dx = zone.x - x;
            const dz = zone.z - z;
            // 8 unit radius to be safe (trees are big)
            return (dx * dx + dz * dz) < 64; 
        });
    };

    const colors = ['#F4A460', '#DEB887', '#CD853F', '#D2691E'];

    // 1. Horizontal Segment (Road at Z = -70, X from -70 to 60)
    // We place props at Z = -85 (North) and Z = -55 (South)
    for (let x = -60; x <= 50; x += 15) {
      // Trees - North Side (Z = -85)
      if (!isBlocked(x, -85)) {
        trees.push([x, 0, -85]); 
      }
      // Trees - South Side (Z = -55)
      if (!isBlocked(x, -55)) {
        trees.push([x, 0, -55]); 
      }

      // Buildings (sparser)
      if (x % 30 === 0) {
        // Deterministic placement
        const isNorth = (x % 60 === 0);
        // Remove Left (North) buildings, keep Right (South)
        if (!isNorth) {
            const zPos = -50;
            if (!isBlocked(x, zPos)) {
                buildings.push({
                    pos: [x, 0, zPos],
                    color: colors[Math.abs(x) % colors.length]
                });
            }
        }
      }
    }

    // 2. Vertical Segment (Road at X = 70, Z from -70 to 70)
    // We place props at X = 55 (West) and X = 85 (East)
    for (let z = -60; z <= 60; z += 15) {
      // Trees - West Side (X = 55)
      if (!isBlocked(55, z)) {
        trees.push([55, 0, z]); 
      }
      // Trees - East Side (X = 85)
      if (!isBlocked(85, z)) {
        trees.push([85, 0, z]); 
      }

      // Buildings
      if (z % 30 === 0) {
        const isWest = (z % 60 === 0);
        // Remove Left (East) buildings, keep Right (West)
        if (isWest) {
            const xPos = 50;
            if (!isBlocked(xPos, z)) {
                buildings.push({
                    pos: [xPos, 0, z],
                    color: colors[Math.abs(z) % colors.length]
                });
            }
        }
      }
    }

    return { trees, buildings };
  }, [high_demand_stops]);

  return (
    <group>
      {/* Palm trees */}
      {props.trees.map((pos, i) => (
        <PalmTree key={`tree-${i}`} position={pos} />
      ))}

      {/* Buildings */}
      {props.buildings.map((building, i) => (
        <Building key={`building-${i}`} position={building.pos} color={building.color} />
      ))}

      {/* Signs - Updated positions for L-shape */}
      <SignBoard position={[-60, 0, -80]} text="UBUNGO" color="#0000FF" />
      <SignBoard position={[60, 0, -80]} text="CORNER" color="#FF0000" />
      <SignBoard position={[80, 0, 60]} text="POSTA" color="#00AA00" />
    </group>
  );
};
