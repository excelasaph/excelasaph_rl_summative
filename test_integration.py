#!/usr/bin/env python3
"""
Phase 3d: Full Integration Test Suite
Tests Flask backend + 3D render frontend communication
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
FLASK_URL = "http://localhost:5000"
API_TIMEOUT = 10

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log(msg, color=Colors.END):
    """Print colored log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {msg}{Colors.END}")

def section(title):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print(f"{title}")
    print(f"{'='*70}{Colors.END}\n")

def test_flask_connection():
    """Test 1: Flask server is accessible"""
    section("TEST 1: Flask Connection")
    try:
        response = requests.get(f"{FLASK_URL}/api/health", timeout=API_TIMEOUT)
        if response.status_code == 200:
            log("✓ Flask server is running", Colors.GREEN)
            log(f"  Response: {response.json()}", Colors.GREEN)
            return True
        else:
            log(f"✗ Flask returned {response.status_code}", Colors.RED)
            return False
    except requests.exceptions.ConnectionError:
        log("✗ Cannot connect to Flask at localhost:5000", Colors.RED)
        log("  Start Flask with: python flask_api.py", Colors.YELLOW)
        return False
    except Exception as e:
        log(f"✗ Error: {e}", Colors.RED)
        return False

def test_load_model():
    """Test 2: Load DQN model via HTTP"""
    section("TEST 2: Load DQN Model")
    try:
        payload = {"algorithm": "DQN"}
        response = requests.post(
            f"{FLASK_URL}/api/load-model",
            json=payload,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            log(f"✓ Model loaded successfully", Colors.GREEN)
            log(f"  Algorithm: {data.get('algorithm')}", Colors.GREEN)
            log(f"  Message: {data.get('message')}", Colors.GREEN)
            return True
        else:
            log(f"✗ Model load failed: {response.status_code}", Colors.RED)
            log(f"  Response: {response.text}", Colors.RED)
            return False
    except Exception as e:
        log(f"✗ Error loading model: {e}", Colors.RED)
        return False

def test_environment_info():
    """Test 3: Get environment info"""
    section("TEST 3: Environment Information")
    try:
        response = requests.get(
            f"{FLASK_URL}/api/environment-info",
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            log("✓ Environment info retrieved", Colors.GREEN)
            
            env = data.get('environment', {})
            log(f"  Grid size: {env.get('grid_size')}x{env.get('grid_size')}", Colors.GREEN)
            log(f"  Actions: {env.get('num_actions')} (0-4)", Colors.GREEN)
            log(f"  Observations: {env.get('num_observations')} features", Colors.GREEN)
            
            obs_names = env.get('observation_names', [])
            log(f"  Observation fields:", Colors.CYAN)
            for i, name in enumerate(obs_names[:5]):  # Show first 5
                log(f"    {i+1}. {name}", Colors.CYAN)
            if len(obs_names) > 5:
                log(f"    ... and {len(obs_names) - 5} more", Colors.CYAN)
            
            return True
        else:
            log(f"✗ Failed: {response.status_code}", Colors.RED)
            return False
    except Exception as e:
        log(f"✗ Error: {e}", Colors.RED)
        return False

def test_reset_environment():
    """Test 4: Reset environment"""
    section("TEST 4: Reset Environment")
    try:
        response = requests.post(
            f"{FLASK_URL}/api/reset",
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            state = data.get('state', {})
            
            log("✓ Environment reset successfully", Colors.GREEN)
            log(f"  Episode: {state.get('episode')}", Colors.GREEN)
            log(f"  Step: {state.get('step')}", Colors.GREEN)
            log(f"  Position: {state.get('position')}", Colors.GREEN)
            log(f"  Passengers: {state.get('passengers')}", Colors.GREEN)
            log(f"  Money: {state.get('money')}", Colors.GREEN)
            
            # Verify position is [7, 7] (starting position)
            pos = state.get('position', [])
            if pos == [7, 7]:
                log(f"  ✓ Starting position correct: [7, 7]", Colors.GREEN)
            else:
                log(f"  ⚠ Starting position unexpected: {pos}", Colors.YELLOW)
            
            return True
        else:
            log(f"✗ Reset failed: {response.status_code}", Colors.RED)
            return False
    except Exception as e:
        log(f"✗ Error: {e}", Colors.RED)
        return False

def test_step_action():
    """Test 5: Execute single step"""
    section("TEST 5: Execute Step Action")
    try:
        # Action 0 = MOVE
        payload = {"action": 0}
        response = requests.post(
            f"{FLASK_URL}/api/step",
            json=payload,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            state = data.get('state', {})
            
            log("✓ Step executed successfully", Colors.GREEN)
            log(f"  Action: 0 (MOVE)", Colors.GREEN)
            log(f"  Step: {state.get('step')}", Colors.GREEN)
            log(f"  Position: {state.get('position')}", Colors.GREEN)
            log(f"  Reward: {state.get('reward')}", Colors.GREEN)
            log(f"  Total Reward: {state.get('total_reward')}", Colors.GREEN)
            log(f"  Terminated: {state.get('terminated')}", Colors.GREEN)
            
            # Verify state structure
            required_fields = [
                'step', 'position', 'passengers', 'money', 'speed',
                'light_red', 'police_here', 'must_stop', 'fined',
                'action', 'reward', 'total_reward', 'terminated'
            ]
            
            missing = [f for f in required_fields if f not in state]
            if missing:
                log(f"  ⚠ Missing fields: {missing}", Colors.YELLOW)
            else:
                log(f"  ✓ All required fields present", Colors.GREEN)
            
            return True
        else:
            log(f"✗ Step failed: {response.status_code}", Colors.RED)
            log(f"  Response: {response.text}", Colors.RED)
            return False
    except Exception as e:
        log(f"✗ Error: {e}", Colors.RED)
        return False

def test_multiple_steps():
    """Test 6: Execute multiple steps and verify state progression"""
    section("TEST 6: Multiple Steps & State Progression")
    try:
        log("Executing 5 steps with different actions...", Colors.CYAN)
        
        actions = [
            (0, "MOVE"),
            (1, "PICKUP"),
            (0, "MOVE"),
            (4, "SPEED_UP"),
            (3, "STOP"),
        ]
        
        previous_reward = 0
        total_reward = 0
        
        for action_id, action_name in actions:
            response = requests.post(
                f"{FLASK_URL}/api/step",
                json={"action": action_id},
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                state = data.get('state', {})
                step = state.get('step')
                pos = state.get('position')
                reward = state.get('reward', 0)
                total = state.get('total_reward', 0)
                
                log(f"  Step {step}: {action_name} → Pos {pos}, Reward {reward:+.1f}, Total {total:.1f}", Colors.CYAN)
                total_reward = total
            else:
                log(f"  ✗ Step failed: {response.status_code}", Colors.RED)
                return False
        
        if total_reward > 0:
            log(f"✓ Episode progressed successfully", Colors.GREEN)
            log(f"  Total reward accumulated: {total_reward:.1f}", Colors.GREEN)
        else:
            log(f"⚠ No positive reward yet (this is normal)", Colors.YELLOW)
        
        return True
    except Exception as e:
        log(f"✗ Error: {e}", Colors.RED)
        return False

def test_state_validation():
    """Test 7: Validate state structure matches Zustand expectations"""
    section("TEST 7: State Structure Validation")
    try:
        response = requests.post(f"{FLASK_URL}/api/reset", timeout=API_TIMEOUT)
        state = response.json()['state']
        
        # Expected fields for Zustand store
        expected_fields = {
            'step': int,
            'position': list,
            'passengers': (int, float),
            'capacity': int,
            'money': (int, float),
            'speed': (int, float),
            'light_red': int,
            'police_here': int,
            'must_stop': int,
            'fined': int,
            'hazards': list,
            'police_checkpoints': list,
            'traffic_lights': list,
            'high_demand_stops': list,
            'light_cycle': int,
            'episode': int,
            'action': int,
            'reward': (int, float),
            'total_reward': (int, float),
            'terminated': bool,
        }
        
        log("Validating state structure...", Colors.CYAN)
        
        all_valid = True
        for field, expected_type in expected_fields.items():
            if field not in state:
                log(f"  ✗ Missing field: {field}", Colors.RED)
                all_valid = False
            else:
                value = state[field]
                
                # Handle tuple of types
                if isinstance(expected_type, tuple):
                    is_valid = isinstance(value, expected_type)
                else:
                    is_valid = isinstance(value, expected_type)
                
                if is_valid:
                    log(f"  ✓ {field}: {type(value).__name__} = {repr(value)[:40]}", Colors.GREEN)
                else:
                    log(f"  ✗ {field}: expected {expected_type}, got {type(value).__name__}", Colors.RED)
                    all_valid = False
        
        if all_valid:
            log("✓ All state fields valid", Colors.GREEN)
        else:
            log("✗ Some fields invalid", Colors.RED)
        
        return all_valid
    except Exception as e:
        log(f"✗ Error: {e}", Colors.RED)
        return False

def test_grid_bounds():
    """Test 8: Verify position stays within grid bounds"""
    section("TEST 8: Grid Boundary Validation")
    try:
        log("Running 20 random steps to test boundary behavior...", Colors.CYAN)
        
        # Reset first
        requests.post(f"{FLASK_URL}/api/reset", timeout=API_TIMEOUT)
        
        min_x, max_x = 14, 0
        min_y, max_y = 14, 0
        out_of_bounds = False
        
        for i in range(20):
            action = i % 5  # Cycle through 5 actions
            response = requests.post(
                f"{FLASK_URL}/api/step",
                json={"action": action},
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                state = response.json()['state']
                pos = state['position']
                
                min_x = min(min_x, pos[0])
                max_x = max(max_x, pos[0])
                min_y = min(min_y, pos[1])
                max_y = max(max_y, pos[1])
                
                # Check bounds
                if not (0 <= pos[0] < 15 and 0 <= pos[1] < 15):
                    log(f"  ✗ Out of bounds at step {i}: {pos}", Colors.RED)
                    out_of_bounds = True
        
        log(f"  Position ranges explored:", Colors.CYAN)
        log(f"    X: [{min_x}, {max_x}]", Colors.CYAN)
        log(f"    Y: [{min_y}, {max_y}]", Colors.CYAN)
        
        if not out_of_bounds:
            log("✓ All positions within bounds [0-14, 0-14]", Colors.GREEN)
            return True
        else:
            log("✗ Out of bounds positions detected", Colors.RED)
            return False
    except Exception as e:
        log(f"✗ Error: {e}", Colors.RED)
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          Phase 3d: Full Integration Test Suite                     ║")
    print("║   Flask RL Backend + 3D Render Frontend Communication Test         ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    # List of tests
    tests = [
        ("Flask Connection", test_flask_connection),
        ("Load Model", test_load_model),
        ("Environment Info", test_environment_info),
        ("Reset Environment", test_reset_environment),
        ("Single Step", test_step_action),
        ("Multiple Steps", test_multiple_steps),
        ("State Validation", test_state_validation),
        ("Grid Bounds", test_grid_bounds),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            log("Tests interrupted by user", Colors.YELLOW)
            break
        except Exception as e:
            log(f"Unexpected error in {test_name}: {e}", Colors.RED)
            results.append((test_name, False))
        
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"  {status}  {test_name}")
    
    print(f"\n  {Colors.BOLD}Total: {passed}/{total} tests passed{Colors.END}\n")
    
    if passed == total:
        log("🎉 All tests passed! System is ready for 3D render integration.", Colors.GREEN)
        return 0
    else:
        log(f"⚠️  {total - passed} test(s) failed. Check output above.", Colors.YELLOW)
        return 1

if __name__ == "__main__":
    sys.exit(main())
