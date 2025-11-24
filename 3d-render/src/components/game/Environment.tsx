import { Environment, Sky, ContactShadows, Cloud } from '@react-three/drei';

export const DarEnvironment = () => {
  return (
    <>
      {/* African Sunset Sky */}
      <Sky
        distance={450000}
        sunPosition={[100, 10, 100]}
        inclination={0.3}
        azimuth={0.25}
        mieCoefficient={0.005}
        mieDirectionalG={0.8}
        rayleigh={0.5}
        turbidity={8}
      />

      {/* Clouds */}
      <Cloud
        opacity={0.3}
        speed={0.2}
        position={[10, 15, -20]}
      />
      <Cloud
        opacity={0.25}
        speed={0.15}
        position={[-15, 18, -25]}
      />

      {/* HDRI Environment for reflections */}
      <Environment preset="sunset" />

      {/* Ground shadow */}
      <ContactShadows
        position={[0, -0.01, 0]}
        opacity={0.5}
        scale={100}
        blur={2}
        far={10}
      />

      {/* Ambient lighting */}
      <ambientLight intensity={0.6} color="#FFE4B5" />

      {/* Main sun light */}
      <directionalLight
        position={[50, 30, 50]}
        intensity={1.5}
        color="#FFD700"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-far={200}
        shadow-camera-left={-50}
        shadow-camera-right={50}
        shadow-camera-top={50}
        shadow-camera-bottom={-50}
      />

      {/* Fill light (bounce from ground) */}
      <directionalLight
        position={[-20, 10, -30]}
        intensity={0.4}
        color="#FF8C00"
      />

      {/* Rim light for daladala */}
      <pointLight
        position={[0, 5, -10]}
        intensity={0.8}
        color="#FFA500"
        distance={30}
      />

      {/* Fog for depth and atmosphere */}
      <fog attach="fog" args={['#FFE4B5', 30, 150]} />
    </>
  );
};
