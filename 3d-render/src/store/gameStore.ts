import { create } from 'zustand';

// Real 5-action system from DaladalaEnv
export enum RLAction {
  MOVE = 0,
  PICKUP = 1,
  DROPOFF = 2,
  STOP = 3,
  SPEED_UP = 4,
}

export interface RLState {
  // Normalized state observations (14 total)
  step: number;
  position: [number, number];           // Grid position (0-14, 0-14)
  passengers: number;                   // 0-50 (normalized)
  capacity: number;                     // Fixed at 50
  money: number;                        // Total earnings (normalized)
  speed: number;                        // Current speed (normalized)
  
  // Environmental hazards
  light_red: number;                    // 0 or 1 (red light)
  police_here: number;                  // 0 or 1 (police checkpoint)
  must_stop: number;                    // 0 or 1 (must stop flag)
  fined: number;                        // 0 or 1 (got fined)
  
  // Array observations
  hazards: Array<[number, number, string]>;        // [[x, y, type], ...]
  police_checkpoints: Array<[number, number]>;     // Police locations
  traffic_lights: Array<[number, number]>;         // Traffic light locations
  traffic_light_states: Record<string, number>;    // Map of "x,y" -> state (1=Red, 0=Green)
  high_demand_stops: Array<[number, number]>;      // High demand passenger stops
  light_cycle: number;                  // Traffic light cycle (0-10)
  
  // Episode tracking
  episode: number;
  action: number;                       // Last action taken (0-4)
  reward: number;                       // Reward from last step
  total_reward: number;                 // Cumulative reward
  terminated: boolean;                  // Episode ended
}

export interface GameState extends RLState {
  isConnected: boolean;
  hasStarted: boolean;
  isMuted: boolean;
  rotation: number;
  cameraMode: 'chase' | 'driver' | 'topdown' | 'cinematic' | 'passenger';
  updateFromRL: (data: any) => void;
  updatePosition: (pos: [number, number], rot: number) => void;
  setSpeed: (speed: number) => void;
  setCameraMode: (mode: GameState['cameraMode']) => void;
  setHasStarted: (started: boolean) => void;
  toggleMute: () => void;
  reset: () => void;
}

const initialState: RLState = {
  step: 0,
  position: [0, 14], // Start at route beginning: Ubungo (0, 14) - matches Python route
  passengers: 0,
  capacity: 50,
  money: 0,
  speed: 0,
  light_red: 0,
  police_here: 0,
  must_stop: 0,
  fined: 0,
  hazards: [],
  police_checkpoints: [],
  traffic_lights: [],
  traffic_light_states: {},
  high_demand_stops: [],
  light_cycle: 0,
  episode: 1,
  action: 0,
  reward: 0,
  total_reward: 0,
  terminated: false,
};

export const useGameStore = create<GameState>((set) => ({
  ...initialState,
  isConnected: false,
  hasStarted: false,
  isMuted: false,
  rotation: 0,
  cameraMode: 'chase' as const,
  
  updateFromRL: (data) => set((state) => {
    // Map Flask API fields to Zustand store
    // Flask sends: { data: { step, position, passengers, ... } }
    const flaskData = data.data || data;
    
    return {
      // Direct field mappings
      step: flaskData.step ?? state.step,
      position: flaskData.position ?? state.position,
      passengers: flaskData.passengers ?? state.passengers,
      capacity: flaskData.capacity ?? state.capacity,
      money: flaskData.money ?? state.money,
      speed: flaskData.speed ?? state.speed,
      light_red: flaskData.light_red ?? state.light_red,
      police_here: flaskData.police_here ?? state.police_here,
      must_stop: flaskData.must_stop ?? state.must_stop,
      fined: flaskData.fined ?? state.fined,
      hazards: flaskData.hazards ?? state.hazards,
      police_checkpoints: flaskData.police_checkpoints ?? state.police_checkpoints,
      traffic_lights: flaskData.traffic_lights ?? state.traffic_lights,
      traffic_light_states: flaskData.traffic_light_states ?? state.traffic_light_states,
      high_demand_stops: flaskData.high_demand_stops ?? state.high_demand_stops,
      light_cycle: flaskData.light_cycle ?? state.light_cycle,
      episode: flaskData.episode ?? state.episode,
      action: flaskData.action ?? state.action,
      reward: flaskData.reward ?? state.reward,
      total_reward: flaskData.total_reward ?? state.total_reward,
      terminated: flaskData.terminated ?? state.terminated,
      isConnected: true,
      hasStarted: true, // Auto-set to true when we receive data
    };
  }),
  
  updatePosition: (pos, rot) => set({ position: pos, rotation: rot }),
  
  setSpeed: (speed) => set({ speed }),
  
  setCameraMode: (mode) => set({ cameraMode: mode }),

  setHasStarted: (started) => set({ hasStarted: started }),

  toggleMute: () => set((state) => ({ isMuted: !state.isMuted })),
  
  reset: () => set((state) => ({
    ...initialState,
    episode: state.episode + 1,
    rotation: state.rotation,
    cameraMode: state.cameraMode,
    hasStarted: state.hasStarted, // Keep started state
  })),
}));

// Action names and metadata for 5-action system
export const ACTION_NAMES: Record<RLAction, { en: string; sw: string }> = {
  [RLAction.MOVE]: { en: 'Move', sw: 'Kusonga' },
  [RLAction.PICKUP]: { en: 'Pick Up', sw: 'Chukua Abiria' },
  [RLAction.DROPOFF]: { en: 'Drop Off', sw: 'Atua Abiria' },
  [RLAction.STOP]: { en: 'Stop', sw: 'Simama' },
  [RLAction.SPEED_UP]: { en: 'Speed Up', sw: 'Ongeza Kasi' },
};

// Color coding for actions
export const ACTION_COLORS: Record<RLAction, string> = {
  [RLAction.MOVE]: '#3b82f6',      // Blue
  [RLAction.PICKUP]: '#10b981',    // Green
  [RLAction.DROPOFF]: '#f59e0b',   // Amber
  [RLAction.STOP]: '#ef4444',      // Red
  [RLAction.SPEED_UP]: '#8b5cf6',  // Purple
};

// Environmental hazard types
export const HAZARD_TYPES = {
  POLICE: 'police',
  TRAFFIC_LIGHT: 'traffic_light',
  CONGESTION: 'congestion',
} as const;

// Helper function to map action number to action enum
export const getActionName = (actionNum: number) => {
  return ACTION_NAMES[actionNum as RLAction] || { en: 'Unknown', sw: 'Haijulikani' };
};

export const getActionColor = (actionNum: number) => {
  return ACTION_COLORS[actionNum as RLAction] || '#6b7280';
};
