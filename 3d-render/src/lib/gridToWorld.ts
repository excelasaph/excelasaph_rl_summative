/**
 * Grid to World coordinate conversion for DaladalaEnv
 * 
 * RL Environment: 15x15 grid (positions 0-14)
 * 3D World: Daladala positioned on road
 * 
 * Grid coordinates map to world positions:
 * - Grid (7, 7) = World center (0, 0) - Starting position
 * - X-axis: -3 to +3 world units (left/right across road)
 * - Z-axis: -70 to +70 world units (forward/backward along road)
 */

export const GRID_SIZE = 15;
export const WORLD_SCALE = 10; // 1 grid unit = 10 world units
export const ROAD_WIDTH = 8; 

/**
 * Convert grid position [x, y] to world position [x, y, z]
 * 
 * @param gridX - Grid X position (0-14)
 * @param gridY - Grid Y position (0-14)
 * @returns [worldX, worldY, worldZ] position in 3D space
 */
export function gridToWorld(gridX: number, gridY: number): [number, number, number] {
  // Map Grid (0,0) to World (0,0,0) for simplicity, or center it.
  // Let's map so that the corner (14,14) is at a logical anchor or keep (7,7) as center.
  // Keeping (7,7) as center (0,0) helps with camera centering.
  
  const normalizedX = gridX - 7; 
  const normalizedY = gridY - 7;

  // Direct mapping: Grid X -> World X, Grid Y -> World Z (inverted for standard 3D coords)
  // In 3D, -Z is usually "forward". 
  // RL Route: (0,14) -> (14,14) -> (14,0)
  // If we map X->X and Y->-Z:
  // Start (0,14) -> X=-70, Z=-70
  // Corner (14,14) -> X=70, Z=-70
  // End (14,0) -> X=70, Z=70
  
  const worldX = normalizedX * WORLD_SCALE;
  const worldZ = -normalizedY * WORLD_SCALE; // Invert Y so "Up" in grid is "Forward" (-Z) in 3D
  
  const worldY = 0.5; // Height

  return [worldX, worldY, worldZ];
}

/**
 * Convert world position back to grid (for debugging)
 * 
 * @param worldX - World X position
 * @param worldZ - World Z position
 * @returns [gridX, gridY] grid position
 */
export function worldToGrid(worldX: number, worldZ: number): [number, number] {
  const normalizedX = worldX / 0.4;
  const normalizedZ = worldZ / (WORLD_SCALE * 0.8);

  const gridX = Math.round(normalizedX + GRID_SIZE / 2);
  const gridY = Math.round(normalizedZ + GRID_SIZE / 2);

  return [
    Math.max(0, Math.min(GRID_SIZE - 1, gridX)),
    Math.max(0, Math.min(GRID_SIZE - 1, gridY)),
  ];
}

/**
 * Calculate distance between grid positions
 */
export function gridDistance(x1: number, y1: number, x2: number, y2: number): number {
  const dx = x2 - x1;
  const dy = y2 - y1;
  return Math.sqrt(dx * dx + dy * dy);
}

/**
 * Calculate rotation/heading from grid direction
 * Used to orient bus when moving
 * 
 * @param fromX - Starting grid X
 * @param fromY - Starting grid Y
 * @param toX - Ending grid X
 * @param toY - Ending grid Y
 * @returns Rotation in radians (0 = north, π/2 = east, π = south, 3π/2 = west)
 */
export function calculateHeading(
  fromX: number,
  fromY: number,
  toX: number,
  toY: number
): number {
  const dx = toX - fromX;
  const dy = toY - fromY;
  return Math.atan2(dx, dy); // atan2(x, z) for Three.js
}

/**
 * Smooth lerp between two positions for animation
 */
export function lerpPosition(
  current: [number, number, number],
  target: [number, number, number],
  t: number // 0 to 1
): [number, number, number] {
  return [
    current[0] + (target[0] - current[0]) * t,
    current[1] + (target[1] - current[1]) * t,
    current[2] + (target[2] - current[2]) * t,
  ];
}

/**
 * Get action description for logging
 */
export function getActionDescription(action: number): string {
  const actions: Record<number, string> = {
    0: 'Move',
    1: 'Pick Up',
    2: 'Drop Off',
    3: 'Stop',
    4: 'Speed Up',
  };
  return actions[action] || 'Unknown';
}

export default {
  gridToWorld,
  worldToGrid,
  gridDistance,
  calculateHeading,
  lerpPosition,
  getActionDescription,
};
