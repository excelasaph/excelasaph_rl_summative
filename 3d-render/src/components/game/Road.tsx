import * as THREE from 'three';

export const Road = () => {
  // Road Dimensions
  const ROAD_WIDTH = 8;
  const SEGMENT_LENGTH = 150; // Covers -70 to +70 plus margin
  
  // Segment 1: Horizontal (Along X-axis) at Z = -70
  // Center: (0, -70)
  const hPos: [number, number, number] = [0, 0.01, -70];
  
  // Segment 2: Vertical (Along Z-axis) at X = 70
  // Center: (70, 0)
  const vPos: [number, number, number] = [70, 0.01, 0];

  return (
    <group>
      {/* === HORIZONTAL SEGMENT (Grid Y=14) === */}
      <group position={hPos}>
        {/* Tarmac - Extended backwards by 10 units to accommodate bus at start */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-5, 0, 0]} receiveShadow>
          <planeGeometry args={[160, ROAD_WIDTH]} />
          <meshStandardMaterial color="#2a2a2a" roughness={0.9} />
        </mesh>
        
        {/* Markings */}
        {Array.from({ length: 15 }).map((_, i) => (
          <mesh key={`h-mark-${i}`} position={[-65 + i * 10, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[3, 0.2]} />
            <meshBasicMaterial color="#FFFFFF" />
          </mesh>
        ))}

        {/* Shoulders - Extended backwards */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-5, -0.01, 5]}>
           <planeGeometry args={[160, 2]} />
           <meshStandardMaterial color="#8B4513" roughness={1} />
        </mesh>
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-5, -0.01, -5]}>
           <planeGeometry args={[160, 2]} />
           <meshStandardMaterial color="#8B4513" roughness={1} />
        </mesh>
      </group>

      {/* === VERTICAL SEGMENT (Grid X=14) === */}
      <group position={vPos}>
        {/* Tarmac */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
          <planeGeometry args={[ROAD_WIDTH, SEGMENT_LENGTH]} />
          <meshStandardMaterial color="#2a2a2a" roughness={0.9} />
        </mesh>

        {/* Markings */}z
        {Array.from({ length: 15 }).map((_, i) => (
          <mesh key={`v-mark-${i}`} position={[0, 0.02, -65 + i * 10]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[0.2, 3]} />
            <meshBasicMaterial color="#FFFFFF" />
          </mesh>
        ))}

        {/* Shoulders */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[5, -0.01, 0]}>
           <planeGeometry args={[2, SEGMENT_LENGTH]} />
           <meshStandardMaterial color="#8B4513" roughness={1} />
        </mesh>
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-5, -0.01, 0]}>
           <planeGeometry args={[2, SEGMENT_LENGTH]} />
           <meshStandardMaterial color="#8B4513" roughness={1} />
        </mesh>
      </group>

      {/* === CORNER CONNECTION (X=70, Z=-70) === */}
      <mesh position={[70, 0.01, -70]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[ROAD_WIDTH, ROAD_WIDTH]} />
        <meshStandardMaterial color="#2a2a2a" roughness={0.9} />
      </mesh>

      {/* === TERRAIN === */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[35, -0.1, 0]} receiveShadow>
        <planeGeometry args={[300, 300]} />
        <meshStandardMaterial color="#A0785A" roughness={0.95} />
      </mesh>
    </group>
  );
};
