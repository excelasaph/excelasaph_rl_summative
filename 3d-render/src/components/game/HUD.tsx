import { useGameStore, ACTION_NAMES, ACTION_COLORS, getActionColor } from '@/store/gameStore';
import { Button } from '@/components/ui/button';
import { useState, useEffect } from 'react';
import { useRLConnection } from '@/hooks/useRLConnection';
import { Minimap } from './Minimap';
import { 
  Trophy, 
  Users, 
  Wallet, 
  MapPin, 
  Gauge, 
  Play, 
  Pause, 
  RotateCcw, 
  Settings2, 
  ChevronUp, 
  ChevronDown,
  ChevronRight,
  Siren,
  AlertOctagon,
  Ban,
  Ticket,
  Zap,
  Activity,
  Volume2
} from 'lucide-react';

export const HUD = () => {
  const {
    passengers,
    money,
    reward,
    total_reward,
    action,
    light_red,
    police_here,
    must_stop,
    fined,
    speed,
    position,
    step,
    episode,
    isConnected,
    terminated,
    setHasStarted,
    isMuted,
    toggleMute
  } = useGameStore();

  // Get socket from connection hook
  const { socket, startEpisode, step: stepAction, reset, getState } = useRLConnection();
  
  // Local state for UI controls
  const [selectedModel, setSelectedModel] = useState<string>('PPO');
  const [loadedModel, setLoadedModel] = useState<string | null>(null);
  const [isAutoRunning, setIsAutoRunning] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [controlsOpen, setControlsOpen] = useState(false);
  
  // Load model from Flask API
  const loadModel = async (algorithm: string) => {
    try {
      const response = await fetch('http://localhost:5000/api/load-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ algorithm }),
      });
      const data = await response.json();
      if (response.ok) {
        setLoadedModel(algorithm);
        setSelectedModel(algorithm);
        console.log(`✓ Model loaded: ${algorithm}`);
      } else {
        console.error('Failed to load model:', data.error);
      }
    } catch (error) {
      console.error('Error loading model:', error);
    }
  };
  
  // Auto-run episode logic
  const toggleAutoRun = () => {
    setIsAutoRunning(!isAutoRunning);
  };
  
  // Effect to handle auto-run loop with variable delays
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    if (terminated) {
      if (isAutoRunning) {
        setIsAutoRunning(false);
        setShowSummary(true);
      }
      return;
    }

    if (isAutoRunning && isConnected) {
      // Determine delay based on LAST action
      // 1=Pickup, 2=Dropoff, 3=Stop -> 5 seconds delay
      // Others -> 0.5 seconds delay
      const isPauseAction = action === 1 || action === 2 || action === 3;
      const delay = isPauseAction ? 5000 : 500;

      timeoutId = setTimeout(() => {
        stepAction();
      }, delay);
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [isAutoRunning, step, terminated, isConnected, action, stepAction]);

  const actionInfo = ACTION_NAMES[action as keyof typeof ACTION_NAMES] || { en: 'Unknown', sw: 'Haijulikani' };
  const actionColor = getActionColor(action);
  const isOverloaded = passengers > 33;

  // Common glass panel style
  const glassPanel = "bg-black/40 backdrop-blur-md border border-white/10 shadow-xl rounded-xl";

  return (
    <div className="fixed inset-0 pointer-events-none z-50 p-4 font-sans select-none">
      
      {/* --- TOP LEFT: STATUS --- */}
      <div className="absolute top-4 left-4 pointer-events-auto">
        <div className={`flex gap-2 ${glassPanel} p-2`}>
          <div className="flex items-center gap-3 px-2 border-r border-white/10">
            <div className={`w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(0,255,0,0.6)] ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
            <div>
              <p className="text-[10px] uppercase tracking-wider text-white/50 font-bold">Episode</p>
              <p className="text-lg font-bold text-white leading-none">{episode}</p>
            </div>
          </div>
          
          <div className="px-2 border-r border-white/10">
            <p className="text-[10px] uppercase tracking-wider text-white/50 font-bold">Step</p>
            <p className="text-lg font-bold text-white leading-none">{step}</p>
          </div>

          <div className="px-2 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-blue-400" />
            <div>
              <p className="text-[10px] uppercase tracking-wider text-white/50 font-bold">Location</p>
              <p className="text-sm font-bold text-white leading-none font-mono">
                {position[0]}, {position[1]}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* --- TOP CENTER: ACTION PILL --- */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 pointer-events-auto">
        <div className={`transform transition-all duration-300 ${glassPanel} px-6 py-2 flex flex-col items-center min-w-[180px]`}
             style={{ borderColor: `${actionColor}40`, boxShadow: `0 0 20px ${actionColor}20` }}>
          <p className="text-[10px] uppercase tracking-[0.2em] font-bold mb-1" style={{ color: actionColor }}>
            Current Action
          </p>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4" style={{ color: actionColor }} />
            <span className="text-xl font-black tracking-wide text-white">
              {actionInfo.en.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {/* --- TOP RIGHT: RESOURCES & MINIMAP --- */}
      <div className="absolute top-4 right-4 flex flex-col items-end gap-4 pointer-events-auto">
        
        {/* Resources Panel */}
        <div className={`flex gap-3 ${glassPanel} p-2`}>
            {/* Passengers */}
            <div className="flex items-center gap-3 px-3 border-r border-white/10">
              <Users className={`w-5 h-5 ${isOverloaded ? 'text-red-500 animate-pulse' : 'text-blue-400'}`} />
              <div>
                <p className="text-[10px] uppercase tracking-wider text-white/50 font-bold">Passengers</p>
                <div className="flex items-baseline gap-1">
                  <span className={`text-lg font-bold leading-none ${isOverloaded ? 'text-red-400' : 'text-white'}`}>
                    {passengers}
                  </span>
                  <span className="text-xs text-white/40">/ 50</span>
                </div>
              </div>
            </div>

            {/* Money */}
            <div className="flex items-center gap-3 px-3">
              <Wallet className="w-5 h-5 text-emerald-400" />
              <div>
                <p className="text-[10px] uppercase tracking-wider text-white/50 font-bold">Earnings</p>
                <p className="text-lg font-bold text-emerald-400 leading-none">
                  TSh {Math.round(money).toLocaleString()}
                </p>
              </div>
            </div>
          </div>

        {/* Minimap */}
        <Minimap />
      </div>

      {/* --- CENTER ALERTS --- */}
      <div className="absolute top-32 left-1/2 -translate-x-1/2 flex flex-col gap-2 items-center pointer-events-none">
        {light_red === 1 && (
          <div className="bg-red-500/90 backdrop-blur-md px-6 py-2 rounded-full shadow-[0_0_30px_rgba(239,68,68,0.6)] flex items-center gap-3 animate-pulse">
            <AlertOctagon className="w-6 h-6 text-white" />
            <span className="text-white font-bold uppercase tracking-widest">Red Light</span>
          </div>
        )}
        {police_here === 1 && (
          <div className="bg-blue-600/90 backdrop-blur-md px-6 py-2 rounded-full shadow-[0_0_30px_rgba(37,99,235,0.6)] flex items-center gap-3 animate-pulse">
            <Siren className="w-6 h-6 text-white" />
            <span className="text-white font-bold uppercase tracking-widest">Police Checkpoint</span>
          </div>
        )}
        {fined === 1 && (
          <div className="bg-amber-500/90 backdrop-blur-md px-6 py-2 rounded-full shadow-[0_0_30px_rgba(245,158,11,0.6)] flex items-center gap-3 animate-bounce">
            <Ticket className="w-6 h-6 text-white" />
            <span className="text-white font-bold uppercase tracking-widest">Fined!</span>
          </div>
        )}
      </div>

      {/* --- BOTTOM LEFT: CONTROLS --- */}
      <div className="absolute bottom-6 left-6 pointer-events-auto flex flex-col gap-2 items-start">
        {/* Collapsible Control Panel */}
        {controlsOpen && (
          <div className={`${glassPanel} p-4 w-64 mb-2 animate-in slide-in-from-bottom-4 fade-in duration-200`}>
            <div className="flex items-center justify-between mb-4 border-b border-white/10 pb-2">
              <span className="text-xs font-bold text-white/70 uppercase tracking-wider">Debug Controls</span>
              <Settings2 className="w-4 h-4 text-white/40" />
            </div>

            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-[10px] text-white/50 uppercase font-bold">Model</label>
                <div className="flex gap-2">
                  <select 
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="flex-1 bg-black/50 border border-white/20 rounded text-xs text-white px-2 py-1.5 outline-none focus:border-blue-500"
                  >
                    <option value="DQN">DQN</option>
                    <option value="PPO">PPO</option>
                    <option value="A2C">A2C</option>
                    <option value="REINFORCE">REINFORCE</option>
                  </select>
                  <Button 
                    size="sm" 
                    variant={selectedModel === loadedModel ? "secondary" : "default"}
                    className="h-auto py-1 text-xs"
                    onClick={() => loadModel(selectedModel)}
                  >
                    {selectedModel === loadedModel ? 'Loaded' : 'Load'}
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="bg-white/5 border-white/10 hover:bg-white/10 text-white h-8 text-xs"
                  onClick={() => {
                    startEpisode();
                    setHasStarted(true);
                  }}
                  disabled={!loadedModel || isAutoRunning}
                >
                  <Play className="w-3 h-3 mr-1" /> Start
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="bg-white/5 border-white/10 hover:bg-white/10 text-white h-8 text-xs"
                  onClick={() => reset()}
                >
                  <RotateCcw className="w-3 h-3 mr-1" /> Reset
                </Button>
              </div>

              <Button 
                variant="outline" 
                size="sm" 
                className="w-full bg-white/5 border-white/10 hover:bg-white/10 text-white h-8 text-xs"
                onClick={() => stepAction()}
                disabled={!loadedModel || isAutoRunning}
              >
                <ChevronRight className="w-3 h-3 mr-1" /> Single Step
              </Button>

              <Button 
                className={`w-full h-9 text-xs font-bold tracking-wide ${isAutoRunning ? 'bg-red-500 hover:bg-red-600' : 'bg-emerald-500 hover:bg-emerald-600'}`}
                onClick={toggleAutoRun}
                disabled={!loadedModel}
              >
                {isAutoRunning ? (
                  <><Pause className="w-3 h-3 mr-2" /> PAUSE SIMULATION</>
                ) : (
                  <><Play className="w-3 h-3 mr-2" /> AUTO RUN</>
                )}
              </Button>

              {/* Camera Controls Help */}
              <div className="mt-3 pt-3 border-t border-white/10">
                <p className="text-[10px] text-white/50 uppercase font-bold mb-2">Camera Views</p>
                <div className="grid grid-cols-2 gap-1 text-[10px] text-white/70">
                  <div className="flex items-center gap-2"><kbd className="bg-white/10 px-1.5 rounded">1</kbd> Chase</div>
                  <div className="flex items-center gap-2"><kbd className="bg-white/10 px-1.5 rounded">2</kbd> Driver</div>
                  <div className="flex items-center gap-2"><kbd className="bg-white/10 px-1.5 rounded">3</kbd> Top</div>
                  <div className="flex items-center gap-2"><kbd className="bg-white/10 px-1.5 rounded">4</kbd> Cine</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Toggle Button */}
        <button 
          onClick={() => setControlsOpen(!controlsOpen)}
          className={`${glassPanel} p-3 hover:bg-white/10 transition-colors group`}
        >
          <Settings2 className={`w-5 h-5 text-white transition-transform duration-300 ${controlsOpen ? 'rotate-180' : ''}`} />
        </button>
      </div>

      {/* --- BOTTOM RIGHT: SPEED & REWARD --- */}
      <div className="absolute bottom-6 right-6 flex flex-col items-end gap-2 pointer-events-auto">
        
        {/* Sound Toggle */}
        <button 
          onClick={toggleMute}
          className={`${glassPanel} p-2 hover:bg-white/10 transition-colors group flex items-center justify-center w-10 h-10 relative`}
          title={isMuted ? "Unmute Sound" : "Mute Sound"}
        >
          <Volume2 className={`w-5 h-5 transition-colors ${isMuted ? 'text-white/40' : 'text-white group-hover:text-blue-400'}`} />
          {isMuted && (
            <div className="absolute w-6 h-0.5 bg-white -rotate-45 shadow-[0_1px_2px_rgba(0,0,0,0.5)]" />
          )}
        </button>

        <div className="flex items-end gap-4">
          {/* Reward Popup */}
        <div className={`${glassPanel} px-4 py-2 flex flex-col items-end min-w-[120px]`}>
          <span className="text-[10px] uppercase tracking-wider text-white/50 font-bold">Reward</span>
          <div className={`text-2xl font-black ${reward >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {reward > 0 ? '+' : ''}{reward.toFixed(1)}
          </div>
          <div className="w-full h-1 bg-white/10 rounded-full mt-1 overflow-hidden">
            <div 
              className={`h-full transition-all duration-500 ${total_reward >= 0 ? 'bg-emerald-500' : 'bg-red-500'}`}
              style={{ width: `${Math.min(Math.abs(total_reward) / 2, 100)}%` }}
            />
          </div>
          <span className="text-[10px] text-white/40 mt-1">Total: {total_reward.toFixed(1)}</span>
        </div>

        {/* Speedometer */}
        <div className={`${glassPanel} px-4 py-2 flex flex-col items-end min-w-[120px]`}>
          <span className="text-[10px] uppercase tracking-wider text-white/50 font-bold">Speed</span>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-black text-white italic tracking-tighter">
              {Math.round(speed)}
            </span>
            <span className="text-[10px] font-bold text-white/50 uppercase">km/h</span>
          </div>
          <div className="w-full h-1 bg-white/10 rounded-full mt-1 overflow-hidden">
            <div 
              className="h-full bg-blue-500 transition-all duration-300 ease-out"
              style={{ width: `${Math.min(speed, 100)}%` }}
            />
          </div>
          <div className="flex items-center gap-1 mt-1">
             <Gauge className="w-3 h-3 text-blue-400" />
             <span className="text-[10px] text-white/40">Live</span>
          </div>
        </div>
        </div>
      </div>

      {/* --- EPISODE SUMMARY MODAL --- */}
      {showSummary && terminated && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[100] pointer-events-auto animate-in fade-in duration-300">
          <div className={`${glassPanel} p-8 max-w-md w-full border-white/20 shadow-2xl transform scale-100`}>
            <div className="flex flex-col items-center mb-6">
              <Trophy className="w-12 h-12 text-yellow-400 mb-2" />
              <h2 className="text-3xl font-black text-white uppercase tracking-tight">Episode Complete</h2>
              <p className="text-white/50 font-medium">{selectedModel} Agent</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-8">
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <p className="text-xs text-white/40 uppercase font-bold">Total Reward</p>
                <p className={`text-2xl font-bold ${total_reward >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {total_reward.toFixed(1)}
                </p>
              </div>
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <p className="text-xs text-white/40 uppercase font-bold">Passengers</p>
                <p className="text-2xl font-bold text-white">
                  {passengers} <span className="text-sm text-white/40">/ 50</span>
                </p>
              </div>
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <p className="text-xs text-white/40 uppercase font-bold">Earnings</p>
                <p className="text-xl font-bold text-emerald-400">
                  TSh {Math.round(money).toLocaleString()}
                </p>
              </div>
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <p className="text-xs text-white/40 uppercase font-bold">Steps</p>
                <p className="text-xl font-bold text-white">{step}</p>
              </div>
            </div>
            
            <div className="flex gap-3">
              <Button
                onClick={() => {
                  setShowSummary(false);
                  startEpisode();
                }}
                className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-bold h-12"
              >
                REPLAY
              </Button>
              <Button
                onClick={() => setShowSummary(false)}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-bold h-12 border border-white/10"
              >
                CLOSE
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
