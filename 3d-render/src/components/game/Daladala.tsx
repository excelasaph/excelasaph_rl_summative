import { useRef, useState, useEffect, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF } from '@react-three/drei';
import { RigidBody, RapierRigidBody } from '@react-three/rapier';
import { useGameStore } from '@/store/gameStore';
import { gridToWorld } from '@/lib/gridToWorld';
import * as THREE from 'three';

export const Daladala = ({ busRef }: { busRef?: React.RefObject<THREE.Group> }) => {
  const rbRef = useRef<RapierRigidBody>(null);
  const localBusRef = useRef<THREE.Group>(null);
  const daladalaRef = busRef || localBusRef;
  
  const { passengers, speed, position, terminated } = useGameStore();
  const isOverloaded = passengers > 40;

  // Define the route path for smooth movement
  const routePath = useRef<THREE.CurvePath<THREE.Vector3>>(new THREE.CurvePath());
  
  useEffect(() => {
    if (routePath.current.curves.length === 0) {
      // Segment 1: Start to near corner (-70, -70) to (60, -70)
      const start = new THREE.Vector3(-70, 0.5, -70);
      const cornerEntry = new THREE.Vector3(60, 0.5, -70);
      routePath.current.add(new THREE.LineCurve3(start, cornerEntry));
      
      // Corner: Bezier curve (60, -70) -> Control(70, -70) -> (70, -60)
      const cornerControl = new THREE.Vector3(70, 0.5, -70);
      const cornerExit = new THREE.Vector3(70, 0.5, -60);
      routePath.current.add(new THREE.QuadraticBezierCurve3(cornerEntry, cornerControl, cornerExit));
      
      // Segment 2: Corner exit to End (70, -60) to (70, 70)
      const end = new THREE.Vector3(70, 0.5, 70);
      routePath.current.add(new THREE.LineCurve3(cornerExit, end));
    }
  }, []);
  
  // Load the bus model
  const { scene } = useGLTF('/bus/scene.gltf');

  // Fix materials and shadows for the imported GLTF
  useEffect(() => {
    scene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        const originalMat = Array.isArray(mesh.material) ? mesh.material[0] : mesh.material;
        const matName = originalMat.name || '';
        
        const newMat = new THREE.MeshStandardMaterial({
          roughness: 0.5,
          metalness: 0.1,
        });

        if (matName.includes('yellow')) {
          newMat.color.setHex(0xFFD700);
        } else if (matName.includes('rubber') || matName.includes('black')) {
          newMat.color.setHex(0x222222);
        } else if (matName.includes('metal')) {
          newMat.color.setHex(0xAAAAAA);
          newMat.metalness = 0.8;
          newMat.roughness = 0.2;
        } else if (matName.includes('red_lamp')) {
          newMat.color.setHex(0xFF0000);
          newMat.emissive.setHex(0x550000);
        } else if (matName.includes('glass')) {
          newMat.color.setHex(0x88CCFF);
          newMat.transparent = true;
          newMat.opacity = 0.3;
          newMat.roughness = 0.0;
          newMat.metalness = 0.9;
          newMat.side = THREE.DoubleSide;
        } else if (matName.includes('Box170__0')) {
          newMat.color.setHex(0xFFFFFF);
        } else {
          if ((originalMat as any).color) {
             newMat.color.copy((originalMat as any).color);
          } else {
             newMat.color.setHex(0xDDDDDD);
          }
        }
        mesh.material = newMat;
      }
    });
  }, [scene]);
  
  // Initialize state for the RigidBody position
  // We ONLY want to set this on mount or hard reset, NOT on every step update
  // otherwise the RigidBody prop update will conflict with our manual physics updates
  const [rbPosition, setRbPosition] = useState(() => gridToWorld(position[0], position[1]));

  // Track smooth progress along the path
  const currentProgress = useRef(0);

  // Initialize progress on mount based on current position
  useEffect(() => {
    // Calculate initial progress based on start position
    const totalLen = 275.7;
    let startProgress = 0;
    if (position[1] === 14) {
      if (position[0] < 14) startProgress = (position[0] * 10) / totalLen;
      else startProgress = (130 + 7.85) / totalLen;
    } else {
      const stepsFromCorner = 14 - position[1];
      startProgress = (145.7 + ((stepsFromCorner - 1) * 10)) / totalLen;
    }
    currentProgress.current = startProgress;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run once on mount

  // Handle Reset: When position goes back to start [0, 14], reset physics state
  useEffect(() => {
    if (position[0] === 0 && position[1] === 14 && rbRef.current) {
      const [x, y, z] = gridToWorld(0, 14);
      
      // Reset translation
      rbRef.current.setTranslation({ x, y, z }, true);
      
      // Reset rotation to face East (PI/2)
      const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(0, Math.PI / 2, 0));
      rbRef.current.setRotation(q, true);
      
      // Reset velocities
      rbRef.current.setLinvel({ x: 0, y: 0, z: 0 }, true);
      rbRef.current.setAngvel({ x: 0, y: 0, z: 0 }, true);
      
      // Reset progress
      currentProgress.current = 0;
      
      // Update internal state just to be safe, though RB handles it
      setRbPosition([x, y, z]);
    }
  }, [position[0], position[1]]);

  // Physics-based movement logic
  useFrame((state, delta) => {
    if (!rbRef.current) return;

    // Calculate target progress based on RL grid position
    // Total Grid Steps = 14 (Horizontal) + 14 (Vertical) = 28 steps
    // Curve Lengths: Seg1=130, Corner=~15.7, Seg2=130. Total ~275.7
    const totalLen = 275.7;
    let targetProgress = 0;

    if (position[1] === 14) {
      // Horizontal Segment (0 to 14)
      if (position[0] < 14) {
        // Linear mapping 0-130
        targetProgress = (position[0] * 10) / totalLen;
      } else {
        // Corner (Grid 14, 14) - Map to center of corner
        targetProgress = (130 + 7.85) / totalLen;
      }
    } else {
      // Vertical Segment (14 to 0)
      // Start after corner (130 + 15.7 = 145.7)
      const stepsFromCorner = 14 - position[1];
      targetProgress = (145.7 + ((stepsFromCorner - 1) * 10)) / totalLen;
    }
    
    // Clamp target
    if (targetProgress > 1.0) targetProgress = 1.0;

    // Smoothly interpolate currentProgress towards targetProgress
    // We use the RL 'speed' to determine how fast we interpolate
    // Base speed 15 + (speed * 5) world units per second
    // Clamp delta to prevent huge jumps (e.g. tab switching)
    const safeDelta = Math.min(delta, 0.1);
    const moveSpeed = (15 + speed * 5) * safeDelta; 
    const progressSpeed = moveSpeed / totalLen;

    // Handle Reset case (large jump backwards)
    if (currentProgress.current - targetProgress > 0.2) {
      currentProgress.current = targetProgress;
    } else {
      // Move towards target - STRICTLY FORWARD ONLY
      // We prevent backward movement to avoid "wobble" or jitter when stopping
      // Add epsilon to prevent micro-adjustments when stopped
      if (currentProgress.current < targetProgress - 0.00001) {
        currentProgress.current += progressSpeed;
        if (currentProgress.current > targetProgress) currentProgress.current = targetProgress;
      } 
      // If current > target (overshoot), we just wait. We do NOT move back.
    }

    // Get exact position and tangent from the curve
    // This ensures the bus stays perfectly on the line
    const point = routePath.current.getPointAt(currentProgress.current);
    const tangent = routePath.current.getTangentAt(currentProgress.current).normalize();
    
    // Set Physics Position (Direct Translation)
    // We use setTranslation instead of setNextKinematicTranslation to avoid
    // physics engine interpolation jitter. We want exact frame-by-frame control.
    rbRef.current.setTranslation({ x: point.x, y: 0.5, z: point.z }, true);

    // Set Physics Rotation (Direct Rotation)
    // Calculate angle from tangent vector
    // atan2(x, z) gives the angle relative to North (Z-axis)
    const angle = Math.atan2(tangent.x, tangent.z);
    const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(0, angle, 0));
    rbRef.current.setRotation(q, true);

    // Visual effects (Bobbing/Tilt) on the inner mesh
    if (daladalaRef.current) {
      const bobAmount = 0.08 + (speed * 0.05);
      // Raised base height from -1.5 to -0.5 to show tires
      daladalaRef.current.position.y = -0.5 + Math.sin(state.clock.elapsedTime * (2 + speed)) * bobAmount;
      
      if (isOverloaded) {
        daladalaRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 3) * 0.05 + 0.02;
      } else {
        daladalaRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 1.5) * 0.01;
      }
    }
  });

  return (
    <RigidBody 
      ref={rbRef} 
      type="kinematicPosition" 
      position={rbPosition} 
      rotation={[0, Math.PI / 2, 0]} // Initialize facing East (along the first road segment)
      colliders="hull"
      lockRotations // We control rotation manually
    >
      <group ref={daladalaRef}>
        <primitive 
          object={scene} 
          scale={[0.40, 0.40, 0.40]} 
          rotation={[0, Math.PI, 0]} 
          position={[0, 0, -4.0]} // Shift forward to align visually with grid position
        />

        {/* Overload indicator */}
        {isOverloaded && (
          <>
            <mesh position={[0.3, 2.1, 0.5]} castShadow>
              <boxGeometry args={[0.5, 0.3, 0.6]} />
              <meshStandardMaterial color="#654321" roughness={0.8} />
            </mesh>
            <mesh position={[-0.4, 2.1, -0.2]} castShadow>
              <boxGeometry args={[0.4, 0.25, 0.5]} />
              <meshStandardMaterial color="#8b4513" roughness={0.8} />
            </mesh>
          </>
        )}
      </group>
    </RigidBody>
  );
};
