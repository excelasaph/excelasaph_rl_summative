import { Scene } from '@/components/game/Scene';
import { HUD } from '@/components/game/HUD';
import { useGameStore } from '@/store/gameStore';

const Index = () => {
  const hasStarted = useGameStore((state) => state.hasStarted);

  return (
    <div className="relative w-full h-screen overflow-hidden">
      <Scene />
      <HUD />
      
      {/* Loading/Welcome overlay */}
      <div className={`fixed inset-0 pointer-events-none transition-opacity duration-1000 ${hasStarted ? 'opacity-0' : 'opacity-100'}`}>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center animate-fade-in">
          <h1 className="text-4xl md:text-6xl font-bold text-primary mb-2 drop-shadow-lg">
            Daladala
          </h1>
          <p className="text-xl md:text-2xl text-foreground drop-shadow-md italic">
            Autonomous Urban Transit
          </p>
          <p className="text-sm text-muted-foreground mt-4 drop-shadow">
            Press 1-4 to change camera • Simulated RL Agent Active
          </p>
        </div>
      </div>
    </div>
  );
};

export default Index;
