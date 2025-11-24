import { useEffect, useMemo } from 'react';
import * as THREE from 'three';
import { useGameStore } from '@/store/gameStore';
import { gridToWorld } from '@/lib/gridToWorld';
import { useGLTF } from '@react-three/drei';

const BusStopModel = ({ position, rotation }: { position: [number, number, number], rotation: number }) => {
  const { scene } = useGLTF('/busstops/scene.gltf');
  
  // Clone the scene so we can reuse it multiple times
  // Memoize to prevent re-cloning on every render which causes flickering
  const clonedScene = useMemo(() => scene.clone(), [scene]);

  // Fix materials for the imported GLTF
  useEffect(() => {
    clonedScene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        const originalMat = Array.isArray(mesh.material) ? mesh.material[0] : mesh.material;
        const matName = originalMat.name || '';

        // Create a new Standard material to ensure proper lighting
        const newMat = new THREE.MeshStandardMaterial({
          roughness: 0.6,
          metalness: 0.2,
        });

        // Map colors based on material names from the GLTF
        if (matName.includes('Material.012')) {
          newMat.color.setHex(0xFFA500); // Orange/Yellow
        } else if (matName.includes('Ceramic_Tiles')) {
          // If texture exists on original, try to keep it, otherwise grey
          if ((originalMat as any).map) {
            newMat.map = (originalMat as any).map;
          } else {
            newMat.color.setHex(0x888888);
          }
        } else if (matName.includes('Material.018') || matName.includes('Material.050') || matName.includes('Material.052')) {
          newMat.color.setHex(0x111111); // Dark/Black
        } else if (matName.includes('Material.047')) {
          newMat.color.setHex(0xCCCCCC); // Light Grey
        } else if (matName.includes('Material.011')) {
          newMat.color.setHex(0x444444); // Grey
        } else if (matName.includes('Material.049') || matName.includes('Material.051')) {
          newMat.color.setHex(0x2F4F4F); // Dark Slate Grey
        } else if (matName.includes('CLEAR_GLASS')) {
          newMat.color.setHex(0x88CCFF);
          newMat.transparent = true;
          newMat.opacity = 0.3;
          newMat.roughness = 0.1;
          newMat.metalness = 0.9;
        } else if (matName.includes('Text')) {
          newMat.color.setHex(0xFFFFFF); // White text
          newMat.emissive.setHex(0xAAAAAA);
        } else {
           // Fallback: try to copy color if it exists
           if ((originalMat as any).color) {
             newMat.color.copy((originalMat as any).color);
           } else {
             newMat.color.setHex(0xDDDDDD);
           }
        }

        mesh.material = newMat;
      }
    });
  }, [clonedScene]);

  return (
    <primitive 
      object={clonedScene} 
      position={position} 
      scale={[1.2, 1.2, 1.2]} // Adjust scale as needed
      rotation={[0, rotation, 0]} // Rotate to face the road
    />
  );
};

export const BusStops = () => {
  // Use selector to avoid re-rendering on every store update (like position changes)
  const high_demand_stops = useGameStore((state) => state.high_demand_stops);

  return (
    <group>
      {high_demand_stops.map((pos, index) => {
        const worldPos = gridToWorld(pos[0], pos[1]);
        
        // Determine rotation and offset based on road segment
        // Route goes Right (x increases) then Up (z decreases/increases depending on coord system)
        // If y=14 (bottom row), we are moving right. Stops should be on the side (e.g. z offset)
        // If x=14 (right column), we are moving up. Stops should be on the side (e.g. x offset)
        
        let offset: [number, number, number] = [0, 0, 0];
        let rotation = 0;

        if (pos[1] === 14) {
          // Horizontal segment (moving right along X axis)
          // Road is at Z = -70. Place stop "above" (North) the road at Z = -76 -> Moved to -82 to avoid clipping
          // Offset X by 5 units to align with bus stopping position (forward)
          offset = [5, 0, -12]; 
          rotation = 0; // Face +Z (towards road)
        } else {
          // Vertical segment (moving "up" along Z axis)
          // Road is at X = 70. Place stop to the right (East) at X = 76 -> Moved to 82 to avoid clipping
          // Offset Z by 5 units to align with bus stopping position (forward)
          offset = [12, 0, 5];
          rotation = -Math.PI / 2; // Face -X (towards road)
        }

        return (
          <BusStopModel 
            key={`stop-${index}`} 
            position={[worldPos[0] + offset[0], worldPos[1], worldPos[2] + offset[2]]} 
            rotation={rotation}
          />
        );
      })}
    </group>
  );
};

