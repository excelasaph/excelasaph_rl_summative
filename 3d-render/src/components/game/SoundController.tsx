import { useEffect, useRef } from 'react';
import { useGameStore, RLAction } from '@/store/gameStore';
import { useSoundManager } from '@/hooks/useSoundManager';
import { Howler } from 'howler';

export const SoundController = () => {
  const { 
    action, 
    speed, 
    police_here, 
    light_red, 
    fined, 
    terminated,
    hasStarted,
    isMuted
  } = useGameStore();
  
  const { play, stop, fade, setRate } = useSoundManager();
  const prevAction = useRef<number>(0);
  const prevSpeed = useRef<number>(0);
  const prevPolice = useRef<number>(0);
  const prevFined = useRef<number>(0);

  // Handle Mute
  useEffect(() => {
    Howler.mute(isMuted);
  }, [isMuted]);

  // Start Ambient Sounds
  useEffect(() => {
    if (hasStarted) {
      play('city_ambient');
      play('engine_idle');
      fade('city_ambient', 0, 0.3, 2000);
      fade('engine_idle', 0, 0.4, 1000);
    }
    return () => {
      stop('city_ambient');
      stop('engine_idle');
    };
  }, [hasStarted]);

  // Engine Pitch based on Speed
  useEffect(() => {
    // Map speed (0-100) to rate (0.8 - 2.0)
    const rate = 0.8 + (speed / 100) * 1.2;
    setRate('engine_idle', rate);
    
    // Play rev sound if accelerating significantly
    if (speed > prevSpeed.current + 10) {
      play('engine_rev');
    }
    prevSpeed.current = speed;
  }, [speed]);

  // Action Sounds
  useEffect(() => {
    if (action === prevAction.current) return;

    switch (action) {
      case RLAction.MOVE:
        // Engine sound handles this mostly, but maybe a gear shift?
        break;
      case RLAction.STOP:
        play('brakes');
        break;
      case RLAction.PICKUP:
        play('brakes');
        setTimeout(() => play('door_open'), 500);
        setTimeout(() => play('pickup'), 1500);
        setTimeout(() => play('door_close'), 3500);
        break;
      case RLAction.DROPOFF:
        play('brakes');
        setTimeout(() => play('door_open'), 500);
        setTimeout(() => play('dropoff'), 1500);
        setTimeout(() => play('door_close'), 3500);
        break;
      case RLAction.SPEED_UP:
        play('engine_rev');
        break;
    }

    prevAction.current = action;
  }, [action]);

  // Hazard Sounds
  useEffect(() => {
    if (police_here === 1 && prevPolice.current === 0) {
      play('police_whistle');
    }
    prevPolice.current = police_here;
  }, [police_here]);

  // Fine Sounds
  useEffect(() => {
    if (fined === 1 && prevFined.current === 0) {
      play('fail');
      play('horn'); // Angry horn
    }
    prevFined.current = fined;
  }, [fined]);

  // Game Over
  useEffect(() => {
    if (terminated) {
      stop('engine_idle');
      play('success'); // Or fail depending on score, but generic end sound
    }
  }, [terminated]);

  return null; // Invisible component
};
