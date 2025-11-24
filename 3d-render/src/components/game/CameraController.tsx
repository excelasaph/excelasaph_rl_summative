import { useEffect, useRef, useState } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import { useGameStore } from '@/store/gameStore';
import * as THREE from 'three';

export const CameraController = ({ targetRef }: { targetRef: React.RefObject<THREE.Group> }) => {
  const { camera, gl } = useThree();
  const { cameraMode, setCameraMode } = useGameStore();
  const currentPosRef = useRef(new THREE.Vector3());
  const currentLookAtRef = useRef(new THREE.Vector3());
  const firstFrameRef = useRef(true);
  
  // GTA-style camera controls
  const [cameraDistance, setCameraDistance] = useState(12);
  const [cameraAngle, setCameraAngle] = useState(0);
  const [cameraPitch, setCameraPitch] = useState(0.3);
  const [isDragging, setIsDragging] = useState(false);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });

  // Set default camera mode
  useEffect(() => {
    setCameraMode('chase');
  }, []);

  // Handle keyboard shortcuts for camera modes
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      switch (e.key) {
        case '1':
          setCameraMode('chase');
          break;
        case '2':
          setCameraMode('driver');
          break;
        case '3':
          setCameraMode('topdown');
          break;
        case '4':
          setCameraMode('cinematic');
          break;
        case '5':
          setCameraMode('passenger');
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [setCameraMode]);

  // GTA-style mouse controls
  useEffect(() => {
    const canvas = gl.domElement;

    const handleMouseDown = (e: MouseEvent) => {
      if (e.button === 2 || e.button === 0) {
        setIsDragging(true);
        setLastMousePos({ x: e.clientX, y: e.clientY });
        canvas.style.cursor = 'grabbing';
      }
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging && cameraMode === 'chase') {
        const deltaX = e.clientX - lastMousePos.x;
        const deltaY = e.clientY - lastMousePos.y;

        setCameraAngle(prev => prev - deltaX * 0.005);
        setCameraPitch(prev => Math.max(-0.8, Math.min(1.2, prev + deltaY * 0.005)));

        setLastMousePos({ x: e.clientX, y: e.clientY });
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      canvas.style.cursor = 'default';
    };

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      if (cameraMode === 'chase') {
        setCameraDistance(prev => Math.max(5, Math.min(30, prev + e.deltaY * 0.01)));
      }
    };

    const handleContextMenu = (e: Event) => {
      e.preventDefault();
    };

    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('wheel', handleWheel, { passive: false });
    canvas.addEventListener('contextmenu', handleContextMenu);

    return () => {
      canvas.removeEventListener('mousedown', handleMouseDown);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseup', handleMouseUp);
      canvas.removeEventListener('wheel', handleWheel);
      canvas.removeEventListener('contextmenu', handleContextMenu);
    };
  }, [isDragging, lastMousePos, cameraMode, gl]);

  // Main camera frame loop
  useFrame((state) => {
    if (!targetRef.current) return;

    const target = targetRef.current;
    const targetPos = new THREE.Vector3();
    target.getWorldPosition(targetPos);

    // Get world rotation (needed because target is child of RigidBody)
    const targetQuat = new THREE.Quaternion();
    target.getWorldQuaternion(targetQuat);
    const targetEuler = new THREE.Euler().setFromQuaternion(targetQuat);
    const targetRotY = targetEuler.y;

    // Initialize camera on first frame when bus is at correct position
    if (firstFrameRef.current && targetPos.length() > 0.1) {
      firstFrameRef.current = false;
      
      console.log('📷 First frame! Bus at:', targetPos.toArray());
      
      // Set initial camera position behind the bus
      const initialAngle = targetRotY; // Use actual bus rotation
      const distance = 12;
      const height = 6;
      
      const initialCameraPos = new THREE.Vector3(
        targetPos.x - Math.sin(initialAngle) * distance,
        targetPos.y + height,
        targetPos.z - Math.cos(initialAngle) * distance
      );
      
      const initialLookAt = new THREE.Vector3(
        targetPos.x,
        targetPos.y + 0.5,
        targetPos.z
      );
      
      currentPosRef.current.copy(initialCameraPos);
      currentLookAtRef.current.copy(initialLookAt);
      camera.position.copy(initialCameraPos);
      camera.lookAt(initialLookAt);
      
      console.log('📷 Camera initialized at:', initialCameraPos.toArray());
    } else if (firstFrameRef.current) {
        // Fallback if targetPos is near zero (e.g. start of game)
        // Just snap to a reasonable default relative to target
        const initialAngle = targetRotY;
        const distance = 12;
        const height = 6;
        
        const initialCameraPos = new THREE.Vector3(
            targetPos.x - Math.sin(initialAngle) * distance,
            targetPos.y + height,
            targetPos.z - Math.cos(initialAngle) * distance
        );
        
        currentPosRef.current.lerp(initialCameraPos, 0.1);
        camera.position.copy(currentPosRef.current);
        camera.lookAt(targetPos);
    }

    let desiredPos = new THREE.Vector3();
    let desiredLookAt = new THREE.Vector3();

    switch (cameraMode) {
      case 'chase': {
        const vehicleAngle = targetRotY;
        const totalAngle = vehicleAngle + cameraAngle;
        const heightOffset = Math.sin(cameraPitch) * cameraDistance;
        const horizontalDistance = Math.cos(cameraPitch) * cameraDistance;
        
        desiredPos.set(
          targetPos.x - Math.sin(totalAngle) * horizontalDistance,
          targetPos.y + Math.max(4, heightOffset + 2.5), // Raised camera height for better view
          targetPos.z - Math.cos(totalAngle) * horizontalDistance
        );
        
        desiredLookAt.set(
          targetPos.x + Math.sin(vehicleAngle) * 2,
          targetPos.y + 0.5, // Look slightly lower to see more road ahead
          targetPos.z + Math.cos(vehicleAngle) * 2
        );
        break;
      }

      case 'driver': {
        desiredPos.set(
          targetPos.x - Math.sin(targetRotY) * 0.3, 
          targetPos.y + 1.5, 
          targetPos.z - Math.cos(targetRotY) * 0.3
        );
        desiredLookAt.set(
          targetPos.x + Math.sin(targetRotY) * 5, 
          targetPos.y + 1, 
          targetPos.z + Math.cos(targetRotY) * 10
        );
        break;
      }

      case 'topdown': {
        desiredPos.set(targetPos.x, targetPos.y + 25, targetPos.z);
        desiredLookAt.copy(targetPos);
        break;
      }

      case 'cinematic': {
        const radius = 18;
        const speed = 0.15;
        const orbitX = Math.cos(state.clock.elapsedTime * speed) * radius;
        const orbitZ = Math.sin(state.clock.elapsedTime * speed) * radius;
        
        desiredPos.set(
          targetPos.x + orbitX,
          targetPos.y + 10 + Math.sin(state.clock.elapsedTime * speed * 0.5) * 2,
          targetPos.z + orbitZ
        );
        desiredLookAt.set(
          targetPos.x,
          targetPos.y + 1,
          targetPos.z
        );
        break;
      }

      case 'passenger': {
        desiredPos.set(targetPos.x + 0.8, targetPos.y + 0.8, targetPos.z - 1);
        desiredLookAt.set(
          targetPos.x + Math.sin(targetRotY) * 3,
          targetPos.y + 0.5,
          targetPos.z + Math.cos(targetRotY) * 8
        );
        break;
      }
    }

    const lerpSpeed = cameraMode === 'chase' && isDragging ? 0.15 : 0.08;
    currentPosRef.current.lerp(desiredPos, lerpSpeed);
    currentLookAtRef.current.lerp(desiredLookAt, lerpSpeed);

    camera.position.copy(currentPosRef.current);
    camera.lookAt(currentLookAtRef.current);
  });

  return null;
};
