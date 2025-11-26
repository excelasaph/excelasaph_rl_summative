import { useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { useGameStore } from '@/store/gameStore';

interface RLStateUpdate {
  type: string;
  data: any;
  timestamp: number;
}

// Use environment variable for API URL, fallback to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const useRLConnection = (wsUrl: string = API_URL) => {
  const socketRef = useRef<Socket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const { updateFromRL } = useGameStore();

  const connect = useCallback(() => {
    try {
      const socket = io(wsUrl, {
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5,
      });

      socket.on('connect', () => {
        console.log('✓ Connected to Flask WebSocket (Socket.IO)');
        useGameStore.setState({ isConnected: true });
      });

      socket.on('rl-update', (data: RLStateUpdate) => {
        console.log('📊 RL State Update:', data.data);
        updateFromRL(data);
      });

      socket.on('episode-complete', (data: any) => {
        console.log('✓ Episode Complete:', data);
        // Could emit custom event here if needed
      });

      socket.on('connection-status', (data: any) => {
        console.log('ℹ Connection Status:', data);
      });

      socket.on('error', (error: any) => {
        console.error('❌ Socket.IO Error:', error);
      });

      socket.on('disconnect', (reason) => {
        console.log('✗ Disconnected from Flask:', reason);
        useGameStore.setState({ isConnected: false });
      });

      socketRef.current = socket;
    } catch (err) {
      console.error('Failed to create Socket.IO connection:', err);
    }
  }, [wsUrl, updateFromRL]);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
  }, []);

  const startEpisode = useCallback(() => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('start-episode');
      console.log('▶ Episode started');
    }
  }, []);

  const step = useCallback((action?: number) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('step', { action });
      console.log(`→ Step executed (action: ${action})`);
    }
  }, []);

  const reset = useCallback(() => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('reset');
      console.log('🔄 Environment reset');
    }
  }, []);

  const getState = useCallback(() => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('get-state');
      console.log('? Requested current state');
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    isConnected: socketRef.current?.connected ?? false,
    startEpisode,
    step,
    reset,
    getState,
    disconnect,
    reconnect: connect,
    socket: socketRef.current,
  };
};