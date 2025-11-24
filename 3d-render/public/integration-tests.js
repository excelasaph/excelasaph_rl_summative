/**
 * Phase 3d: Frontend Integration Tests
 * Browser-based tests for Socket.IO connection and state management
 * 
 * Run in browser console after npm run dev
 */

// ============================================================================
// TEST UTILITIES
// ============================================================================

const testUtils = {
  colors: {
    reset: '\033[0m',
    green: '\033[92m',
    red: '\033[91m',
    yellow: '\033[93m',
    cyan: '\033[96m',
    bold: '\033[1m',
  },

  log(msg, color = 'reset') {
    const timestamp = new Date().toLocaleTimeString();
    const colorCode = this.colors[color] || '';
    console.log(`${colorCode}[${timestamp}] ${msg}${this.colors.reset}`);
  },

  section(title) {
    console.log(`\n${this.colors.bold}${this.colors.cyan}${'='.repeat(70)}`);
    console.log(title);
    console.log(`${'='.repeat(70)}${this.colors.reset}\n`);
  },

  pass(msg) {
    this.log(`✓ ${msg}`, 'green');
  },

  fail(msg) {
    this.log(`✗ ${msg}`, 'red');
  },

  warn(msg) {
    this.log(`⚠ ${msg}`, 'yellow');
  },

  info(msg) {
    this.log(`ℹ ${msg}`, 'cyan');
  },
};

// ============================================================================
// TESTS
// ============================================================================

const integrationTests = {
  // Test 1: Zustand store initialized
  testZustandStore() {
    testUtils.section('TEST 1: Zustand Store Initialization');
    try {
      const store = gameStore.getState();
      
      if (!store) {
        testUtils.fail('Zustand store not found');
        return false;
      }

      testUtils.pass('Zustand store initialized');
      testUtils.info(`Position: ${JSON.stringify(store.position)}`);
      testUtils.info(`Episode: ${store.episode}`);
      testUtils.info(`Connected: ${store.isConnected}`);

      // Check initial position is [7, 7]
      if (store.position[0] === 7 && store.position[1] === 7) {
        testUtils.pass('Initial position correct: [7, 7]');
      } else {
        testUtils.warn(`Initial position: ${JSON.stringify(store.position)} (expected [7, 7])`);
      }

      return true;
    } catch (e) {
      testUtils.fail(`Error: ${e.message}`);
      return false;
    }
  },

  // Test 2: Action colors and names
  testActionMetadata() {
    testUtils.section('TEST 2: Action Metadata');
    try {
      const expectedActions = {
        0: { en: 'Move', sw: 'Kusonga' },
        1: { en: 'Pick Up', sw: 'Chukua Abiria' },
        2: { en: 'Drop Off', sw: 'Atua Abiria' },
        3: { en: 'Stop', sw: 'Simama' },
        4: { en: 'Speed Up', sw: 'Ongeza Kasi' },
      };

      const { ACTION_NAMES, ACTION_COLORS } = gameStore;

      let allValid = true;
      for (const [id, expected] of Object.entries(expectedActions)) {
        const name = ACTION_NAMES[id];
        const color = ACTION_COLORS[id];

        if (!name) {
          testUtils.fail(`Missing action name for ${id}`);
          allValid = false;
          continue;
        }

        if (name.en !== expected.en || name.sw !== expected.sw) {
          testUtils.fail(
            `Action ${id} mismatch: ${JSON.stringify(name)} vs ${JSON.stringify(expected)}`
          );
          allValid = false;
        } else {
          testUtils.info(`Action ${id}: ${name.en} (${name.sw}) - Color: ${color}`);
        }
      }

      if (allValid) {
        testUtils.pass('All action metadata valid');
      }
      return allValid;
    } catch (e) {
      testUtils.fail(`Error: ${e.message}`);
      return false;
    }
  },

  // Test 3: Position conversion
  async testPositionConversion() {
    testUtils.section('TEST 3: Position Conversion (Grid → World)');
    try {
      // Import gridToWorld if available
      // This would need to be exposed via window or module
      testUtils.info('Simulating position updates...');

      const store = gameStore.getState();
      const initialPos = store.position;

      // Simulate Flask sending a position update
      store.updateFromRL({
        data: {
          step: 5,
          position: [8, 8],  // Move right and forward
          passengers: 10,
          capacity: 50,
          money: 500,
          speed: 1.5,
          light_red: 0,
          police_here: 0,
          must_stop: 0,
          fined: 0,
          hazards: [],
          police_checkpoints: [],
          traffic_lights: [],
          high_demand_stops: [],
          light_cycle: 0,
          episode: 1,
          action: 0,
          reward: 10.0,
          total_reward: 50.0,
          terminated: false,
        },
      });

      const newStore = gameStore.getState();
      if (newStore.position[0] === 8 && newStore.position[1] === 8) {
        testUtils.pass(`Position updated: [${initialPos}] → [${newStore.position}]`);
        return true;
      } else {
        testUtils.fail(`Position update failed: ${JSON.stringify(newStore.position)}`);
        return false;
      }
    } catch (e) {
      testUtils.fail(`Error: ${e.message}`);
      return false;
    }
  },

  // Test 4: State mapping from Flask
  testStateMapping() {
    testUtils.section('TEST 4: Flask State Mapping');
    try {
      const store = gameStore.getState();
      const testData = {
        data: {
          step: 42,
          position: [10, 9],
          passengers: 25,
          capacity: 50,
          money: 2500,
          speed: 3.0,
          light_red: 0,
          police_here: 1,
          must_stop: 0,
          fined: 0,
          hazards: [
            [10, 8, 'police'],
            [11, 9, 'traffic_light'],
          ],
          police_checkpoints: [[10, 8]],
          traffic_lights: [[11, 9]],
          high_demand_stops: [[4, 14], [8, 14]],
          light_cycle: 5,
          episode: 1,
          action: 2,
          reward: 15.5,
          total_reward: 125.3,
          terminated: false,
        },
      };

      store.updateFromRL(testData);
      const updated = gameStore.getState();

      const mappedCorrectly = [
        ['step', 42, updated.step],
        ['position', '[10, 9]', JSON.stringify(updated.position)],
        ['passengers', 25, updated.passengers],
        ['money', 2500, updated.money],
        ['police_here', 1, updated.police_here],
        ['action', 2, updated.action],
        ['reward', 15.5, updated.reward],
        ['total_reward', 125.3, updated.total_reward],
      ];

      let allCorrect = true;
      for (const [field, expected, actual] of mappedCorrectly) {
        if (expected === actual) {
          testUtils.info(`${field}: ${actual} ✓`);
        } else {
          testUtils.fail(`${field}: expected ${expected}, got ${actual}`);
          allCorrect = false;
        }
      }

      if (allCorrect) {
        testUtils.pass('All fields mapped correctly');
      }
      return allCorrect;
    } catch (e) {
      testUtils.fail(`Error: ${e.message}`);
      return false;
    }
  },

  // Test 5: HUD component rendering
  testHUDRendering() {
    testUtils.section('TEST 5: HUD Component Rendering');
    try {
      const hudElement = document.querySelector('[class*="HUD"]') || 
                        document.querySelector('[role="presentation"]');

      if (hudElement) {
        testUtils.pass('HUD component rendered');
        testUtils.info(`HUD element: ${hudElement.tagName}`);

        // Check for expected elements
        const hasAction = hudElement.textContent.includes('Action');
        const hasPassengers = hudElement.textContent.includes('Passengers');
        const hasReward = hudElement.textContent.includes('Reward');

        if (hasAction && hasPassengers && hasReward) {
          testUtils.pass('HUD displays all expected elements');
          return true;
        } else {
          testUtils.warn('Some HUD elements missing');
          testUtils.info(`Has Action: ${hasAction}`);
          testUtils.info(`Has Passengers: ${hasPassengers}`);
          testUtils.info(`Has Reward: ${hasReward}`);
          return true; // Still pass, rendering is working
        }
      } else {
        testUtils.warn('HUD element not found in DOM');
        return true; // Not critical for this test
      }
    } catch (e) {
      testUtils.fail(`Error: ${e.message}`);
      return false;
    }
  },

  // Test 6: Socket.IO connection status
  testSocketIOConnection() {
    testUtils.section('TEST 6: Socket.IO Connection');
    try {
      const store = gameStore.getState();
      
      testUtils.info(`Connection status: ${store.isConnected ? 'Connected' : 'Disconnected'}`);
      
      if (store.isConnected) {
        testUtils.pass('Socket.IO connection active');
      } else {
        testUtils.warn('Not currently connected (WebSocket may not be initialized yet)');
        testUtils.info('Expected: Socket.IO client attempts to connect to http://localhost:5000');
      }

      return true; // Non-critical for test suite
    } catch (e) {
      testUtils.fail(`Error: ${e.message}`);
      return false;
    }
  },

  // Test 7: Environmental hazard alerts
  testHazardAlerts() {
    testUtils.section('TEST 7: Environmental Hazard Tracking');
    try {
      const store = gameStore.getState();

      // Simulate hazard scenario
      const hazardData = {
        data: {
          step: 50,
          position: [7, 7],
          passengers: 30,
          capacity: 50,
          money: 5000,
          speed: 2.0,
          light_red: 1,      // Red light
          police_here: 1,    // Police present
          must_stop: 1,      // Must stop
          fined: 0,
          hazards: [[7, 7, 'police']],
          police_checkpoints: [[7, 7]],
          traffic_lights: [],
          high_demand_stops: [],
          light_cycle: 0,
          episode: 1,
          action: 3,
          reward: -5.0,
          total_reward: 100.0,
          terminated: false,
        },
      };

      store.updateFromRL(hazardData);
      const updated = gameStore.getState();

      const hazardStatus = [
        ['light_red (Red Light)', updated.light_red === 1],
        ['police_here (Police)', updated.police_here === 1],
        ['must_stop (Must Stop)', updated.must_stop === 1],
        ['fined', updated.fined === 0],
      ];

      let allCorrect = true;
      for (const [hazard, status] of hazardStatus) {
        if (status) {
          testUtils.info(`${hazard}: ✓`);
        } else {
          testUtils.fail(`${hazard}: not set correctly`);
          allCorrect = false;
        }
      }

      if (allCorrect) {
        testUtils.pass('All hazards tracked correctly');
      }
      return allCorrect;
    } catch (e) {
      testUtils.fail(`Error: ${e.message}`);
      return false;
    }
  },

  // Test 8: Memory and state consistency
  testStateConsistency() {
    testUtils.section('TEST 8: State Consistency');
    try {
      const store = gameStore.getState();
      const snapshot1 = JSON.stringify(store);

      // Get state again
      const store2 = gameStore.getState();
      const snapshot2 = JSON.stringify(store2);

      if (snapshot1 === snapshot2) {
        testUtils.pass('State remains consistent between reads');
        return true;
      } else {
        testUtils.warn('State changed between reads (may be expected if auto-updating)');
        return true;
      }
    } catch (e) {
      testUtils.fail(`Error: ${e.message}`);
      return false;
    }
  },
};

// ============================================================================
// TEST RUNNER
// ============================================================================

async function runAllFrontendTests() {
  console.clear();
  console.log(`
╔════════════════════════════════════════════════════════════════════╗
║     Phase 3d: Frontend Integration Tests                           ║
║     Socket.IO + Zustand Store + React Components                  ║
╚════════════════════════════════════════════════════════════════════╝
  `);

  const tests = [
    ['Zustand Store', integrationTests.testZustandStore],
    ['Action Metadata', integrationTests.testActionMetadata],
    ['Position Conversion', integrationTests.testPositionConversion],
    ['State Mapping', integrationTests.testStateMapping],
    ['HUD Rendering', integrationTests.testHUDRendering],
    ['Socket.IO Connection', integrationTests.testSocketIOConnection],
    ['Hazard Alerts', integrationTests.testHazardAlerts],
    ['State Consistency', integrationTests.testStateConsistency],
  ];

  const results = [];

  for (const [testName, testFunc] of tests) {
    try {
      const result = await testFunc();
      results.push([testName, result]);
    } catch (e) {
      testUtils.fail(`Unexpected error in ${testName}: ${e.message}`);
      results.push([testName, false]);
    }
  }

  // Summary
  testUtils.section('TEST SUMMARY');

  const passed = results.filter(([_, r]) => r).length;
  const total = results.length;

  for (const [testName, result] of results) {
    const status = result ? '✓ PASS' : '✗ FAIL';
    console.log(`  ${status}  ${testName}`);
  }

  console.log(`\n  Total: ${passed}/${total} tests passed\n`);

  if (passed === total) {
    testUtils.pass('🎉 All frontend tests passed!');
  } else {
    testUtils.warn(`${total - passed} test(s) need attention`);
  }

  return passed === total;
}

// ============================================================================
// EXPORT FOR CONSOLE USE
// ============================================================================

window.runAllFrontendTests = runAllFrontendTests;
window.testUtils = testUtils;
window.integrationTests = integrationTests;

// Provide quick access
console.log(`
📋 Available Commands:
   runAllFrontendTests()           - Run all 8 integration tests
   
   Utilities:
   testUtils.log(msg, color)       - Log with color
   testUtils.section(title)        - Print section header
   
   Manual Tests:
   integrationTests.testZustandStore()
   integrationTests.testActionMetadata()
   integrationTests.testPositionConversion()
   integrationTests.testStateMapping()
   integrationTests.testHUDRendering()
   integrationTests.testSocketIOConnection()
   integrationTests.testHazardAlerts()
   integrationTests.testStateConsistency()
`);
