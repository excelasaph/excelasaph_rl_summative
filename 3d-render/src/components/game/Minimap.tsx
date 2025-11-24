import { useGameStore } from '@/store/gameStore';
import { Siren, AlertOctagon, Zap, MapPin, Flag } from 'lucide-react';

export const Minimap = () => {
  const { 
    position, 
    police_checkpoints, 
    traffic_lights, 
    high_demand_stops,
  } = useGameStore();

  // Grid dimensions
  const GRID_SIZE = 14;

  // Convert grid coordinates to percentage for CSS positioning
  // x: 0..14 -> 15%..85%
  // y: 14..0 -> 15%..85% (Inverted: 14 is top, 0 is bottom)
  const getPos = (x: number, y: number) => ({
    left: `${15 + (x / GRID_SIZE) * 70}%`,
    top: `${15 + ((GRID_SIZE - y) / GRID_SIZE) * 70}%`
  });

  return (
    <div className="bg-black/40 backdrop-blur-md border border-white/10 shadow-xl rounded-xl w-56 h-56 relative overflow-hidden group transition-all hover:bg-black/50">
      {/* Header */}
      <div className="absolute top-3 left-3 z-10">
        <p className="text-[10px] uppercase tracking-wider text-white/50 font-bold flex items-center gap-1">
          <MapPin className="w-3 h-3" /> Live Tracker
        </p>
      </div>

      {/* Grid/Map Container */}
      <div className="absolute inset-0">
        {/* The L-Shaped Road Path */}
        <svg className="w-full h-full absolute inset-0 pointer-events-none opacity-40" viewBox="0 0 100 100" preserveAspectRatio="none">
          {/* Road Background */}
          <path 
            d="M 15 15 L 85 15 L 85 85"
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="16"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {/* Road Center Line */}
          <path 
            d="M 15 15 L 85 15 L 85 85"
            fill="none"
            stroke="rgba(255,255,255,0.3)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray="4 4"
          />
        </svg>

        {/* Start Point (Ubungo) */}
        <div className="absolute transform -translate-x-1/2 -translate-y-1/2" style={getPos(0, 14)}>
          <div className="w-2 h-2 bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
        </div>
        
        {/* End Point (Posta) */}
        <div className="absolute transform -translate-x-1/2 -translate-y-1/2" style={getPos(14, 0)}>
          <Flag className="w-3 h-3 text-red-500 fill-red-500" />
        </div>

        {/* Static Elements (Police, Lights, Stops) */}
        {police_checkpoints?.map((p, i) => (
           <div key={`police-${i}`} className="absolute text-blue-500 transform -translate-x-1/2 -translate-y-1/2 z-10" style={getPos(p[0], p[1])}>
             <Siren size={10} className="animate-pulse" />
           </div>
        ))}

        {traffic_lights?.map((p, i) => (
           <div key={`light-${i}`} className="absolute text-yellow-500 transform -translate-x-1/2 -translate-y-1/2 z-10" style={getPos(p[0], p[1])}>
             <AlertOctagon size={10} />
           </div>
        ))}
        
        {high_demand_stops?.map((p, i) => (
           <div key={`stop-${i}`} className="absolute text-purple-400 transform -translate-x-1/2 -translate-y-1/2 z-10" style={getPos(p[0], p[1])}>
             <Zap size={10} />
           </div>
        ))}

        {/* The Agent (Bus) */}
        <div 
          className="absolute w-4 h-4 bg-blue-500 border-2 border-white rounded-full shadow-[0_0_15px_rgba(59,130,246,1)] z-20 transition-all duration-500 ease-linear flex items-center justify-center"
          style={{ 
            ...getPos(position[0], position[1]),
            transform: 'translate(-50%, -50%)'
          }}
        >
          <div className="w-1 h-1 bg-white rounded-full animate-ping" />
        </div>
      </div>
      
      {/* Legend/Status at bottom */}
      <div className="absolute bottom-2 left-0 right-0 flex justify-center gap-3 text-[8px] text-white/40 uppercase font-bold">
         <span className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div> Bus</span>
         <span className="flex items-center gap-1"><Siren size={8} /> Police</span>
         <span className="flex items-center gap-1"><AlertOctagon size={8} /> Light</span>
      </div>
    </div>
  );
};
