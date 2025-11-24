import { useEffect, useRef } from 'react';
import { Howl } from 'howler';

export const useSoundManager = () => {
  const sounds = useRef<Record<string, Howl>>({});

  useEffect(() => {
    // Initialize sounds
    sounds.current = {
      // Ambient
      city_ambient: new Howl({ src: ['/sounds/city_ambient.mp3'], loop: true, volume: 0.3 }),
      
      // Bus
      engine_idle: new Howl({ src: ['/sounds/engine_idle.mp3'], loop: true, volume: 0.4 }),
      engine_rev: new Howl({ src: ['/sounds/engine_rev.mp3'], volume: 0.6 }),
      brakes: new Howl({ src: ['/sounds/brakes.mp3'], volume: 0.5 }),
      door_open: new Howl({ src: ['/sounds/door_open.mp3'], volume: 0.7 }),
      door_close: new Howl({ src: ['/sounds/door_close.mp3'], volume: 0.7 }),
      
      // Actions
      pickup: new Howl({ src: ['/sounds/coin.mp3'], volume: 0.6 }), // Money sound
      dropoff: new Howl({ src: ['/sounds/shuffle.mp3'], volume: 0.6 }), // Passenger movement
      horn: new Howl({ src: ['/sounds/horn.mp3'], volume: 0.8 }),
      
      // Environment
      police_whistle: new Howl({ src: ['/sounds/whistle.mp3'], volume: 0.7 }),
      traffic_light: new Howl({ src: ['/sounds/beep.mp3'], volume: 0.4 }),
      
      // UI
      success: new Howl({ src: ['/sounds/success.mp3'], volume: 0.5 }),
      fail: new Howl({ src: ['/sounds/fail.mp3'], volume: 0.5 }),
      click: new Howl({ src: ['/sounds/click.mp3'], volume: 0.3 }),
    };

    return () => {
      // Cleanup
      Object.values(sounds.current).forEach(sound => sound.unload());
    };
  }, []);

  const play = (name: string) => {
    if (sounds.current[name]) {
      sounds.current[name].play();
    }
  };

  const stop = (name: string) => {
    if (sounds.current[name]) {
      sounds.current[name].stop();
    }
  };

  const fade = (name: string, from: number, to: number, duration: number) => {
    if (sounds.current[name]) {
      sounds.current[name].fade(from, to, duration);
    }
  };

  const setRate = (name: string, rate: number) => {
    if (sounds.current[name]) {
      sounds.current[name].rate(rate);
    }
  };

  return { play, stop, fade, setRate };
};
