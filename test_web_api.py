"""
Quick test script to verify Flask API and web frontend are working
Run this AFTER starting the Flask server with: python flask_api.py
"""

import requests
import json
import time

API_URL = 'http://localhost:5000/api'

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print('='*80)

def test_health():
    """Test 1: Server health check"""
    print_section("Test 1: Health Check")
    try:
        response = requests.get(f'{API_URL}/health', timeout=5)
        print(f"✅ Server responding (Status: {response.status_code})")
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Model Loaded: {data.get('model_loaded')}")
        print(f"   Environment Ready: {data.get('environment_ready')}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("   Make sure Flask server is running: python flask_api.py")
        return False

def test_models_list():
    """Test 2: List available models"""
    print_section("Test 2: List Available Models")
    try:
        response = requests.get(f'{API_URL}/models', timeout=5)
        print(f"✅ Models endpoint responding")
        data = response.json()
        print(f"   Available models:")
        for model_name, exists in data.items():
            status = "✅" if exists else "❌"
            print(f"     {status} {model_name}")
        return True
    except Exception as e:
        print(f"❌ Models list failed: {e}")
        return False

def test_load_model(algorithm='DQN'):
    """Test 3: Load a model"""
    print_section(f"Test 3: Load {algorithm} Model")
    try:
        payload = {'algorithm': algorithm}
        response = requests.post(f'{API_URL}/load-model', json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model loaded successfully")
            print(f"   Algorithm: {data.get('algorithm')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            error = response.json()
            print(f"❌ Failed to load model: {error.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def test_environment_info():
    """Test 4: Get environment information"""
    print_section("Test 4: Environment Information")
    try:
        response = requests.get(f'{API_URL}/environment-info', timeout=5)
        data = response.json()
        print(f"✅ Environment info retrieved")
        print(f"   Grid Size: {data.get('grid_size')} × {data.get('grid_size')}")
        print(f"   Number of Stops: {len(data.get('stops', []))}")
        print(f"   High Demand Stops: {len(data.get('high_demand_stops', []))}")
        print(f"   Action Space: {len(data.get('actions', []))} actions")
        print(f"   Observation Space: {len(data.get('observation_space', []))} dimensions")
        return True
    except Exception as e:
        print(f"❌ Environment info failed: {e}")
        return False

def test_reset_episode():
    """Test 5: Reset episode"""
    print_section("Test 5: Reset Episode")
    try:
        response = requests.post(f'{API_URL}/reset', timeout=5)
        data = response.json()
        print(f"✅ Episode reset successfully")
        if 'state' in data:
            state = data['state']
            print(f"   Agent Position: ({state.get('x')}, {state.get('y')})")
            print(f"   Passengers: {state.get('passengers')}")
            print(f"   Speed: {state.get('speed')}")
            print(f"   Hazards on map: {len(state.get('hazards', []))}")
        return True
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        return False

def test_step_episode():
    """Test 6: Execute one step"""
    print_section("Test 6: Execute One Step")
    try:
        payload = {'use_model': True}
        response = requests.post(f'{API_URL}/step', json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Step executed successfully")
            print(f"   Action Taken: {data.get('action')}")
            print(f"   Reward: {data.get('reward'):.2f}")
            if 'state' in data:
                state = data['state']
                print(f"   New Position: ({state.get('x')}, {state.get('y')})")
            return True
        else:
            error = response.json()
            print(f"⚠️  Step response: {error.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Step failed: {e}")
        return False

def test_current_state():
    """Test 7: Get current state"""
    print_section("Test 7: Get Current State")
    try:
        response = requests.get(f'{API_URL}/current-state', timeout=5)
        data = response.json()
        print(f"✅ Current state retrieved")
        if 'state' in data:
            state = data['state']
            print(f"   Episode: {data.get('episode', 'N/A')}")
            print(f"   Step: {data.get('step', 'N/A')}")
            print(f"   Total Reward: {data.get('total_reward', 0):.2f}")
            print(f"   Position: ({state.get('x')}, {state.get('y')})")
            print(f"   Passengers: {state.get('passengers')}/{state.get('capacity')}")
        return True
    except Exception as e:
        print(f"❌ Current state failed: {e}")
        return False

def test_web_ui():
    """Test 8: Web UI access"""
    print_section("Test 8: Web UI Access")
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            if 'Daladala' in response.text and 'canvas' in response.text:
                print(f"✅ Web UI is accessible")
                print(f"   URL: http://localhost:5000")
                print(f"   File size: {len(response.text)} bytes")
                print(f"   Contains canvas element: Yes")
                return True
            else:
                print(f"⚠️  Web UI loaded but may be incomplete")
                return False
        else:
            print(f"❌ Web UI returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web UI access failed: {e}")
        print("   Make sure Flask server is running")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*80)
    print("  DALADALA RL VISUALIZER - QUICK TEST SUITE")
    print("="*80)
    print("\nMake sure Flask server is running: python flask_api.py")
    print("This script will test all API endpoints and web UI\n")
    
    time.sleep(1)
    
    results = []
    
    # Test sequence
    results.append(("Health Check", test_health()))
    
    if not results[-1][1]:
        print("\n⚠️  Cannot continue without server response. Please start Flask server.")
        print("   Run: python flask_api.py")
        return results
    
    results.append(("List Models", test_models_list()))
    results.append(("Web UI Access", test_web_ui()))
    
    # Try to load DQN
    if test_load_model('DQN'):
        results.append(("Load DQN", True))
        results.append(("Environment Info", test_environment_info()))
        results.append(("Reset Episode", test_reset_episode()))
        results.append(("Execute Step", test_step_episode()))
        results.append(("Current State", test_current_state()))
    else:
        print("⚠️  Could not load DQN model. Check that models/dqn/best_dqn.zip exists")
        results.append(("Load DQN", False))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n✅ Passed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready to use web visualization.")
        print("   Open browser: http://localhost:5000")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
    
    return results

if __name__ == '__main__':
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
