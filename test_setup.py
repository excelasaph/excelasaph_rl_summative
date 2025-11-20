# test_setup.py
"""
Validation script to verify environment, models, and all components work correctly.
Run this before final submission to ensure everything is functional.
"""
import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported."""
    print("\n" + "="*80)
    print("TESTING IMPORTS")
    print("="*80)
    
    packages = [
        ("gymnasium", "gymnasium"),
        ("numpy", "numpy"),
        ("pygame", "pygame"),
        ("torch", "torch"),
        ("imageio", "imageio"),
        ("stable_baselines3", "stable_baselines3"),
        ("matplotlib", "matplotlib"),
    ]
    
    all_ok = True
    for display_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"✓ {display_name}")
        except ImportError as e:
            print(f"✗ {display_name}: {e}")
            all_ok = False
    
    return all_ok

def test_environment():
    """Test that the custom environment works."""
    print("\n" + "="*80)
    print("TESTING ENVIRONMENT")
    print("="*80)
    
    try:
        from environment import DaladalaEnv
        print("✓ Environment import successful")
        
        env = DaladalaEnv()
        print("✓ Environment instantiation successful")
        
        obs, info = env.reset()
        print(f"✓ Environment reset successful (obs shape: {obs.shape})")
        
        for _ in range(10):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
        print("✓ Environment step successful (10 steps)")
        
        env.close()
        print("✓ Environment closed successfully")
        
        return True
    except Exception as e:
        print(f"✗ Environment test failed: {e}")
        traceback.print_exc()
        return False

def test_observation_space():
    """Verify observation space correctness."""
    print("\n" + "="*80)
    print("TESTING OBSERVATION SPACE")
    print("="*80)
    
    try:
        from environment import DaladalaEnv
        import numpy as np
        
        env = DaladalaEnv()
        obs, _ = env.reset()
        
        expected_shape = (15,)
        if obs.shape != expected_shape:
            print(f"✗ Observation shape mismatch: {obs.shape} vs {expected_shape}")
            return False
        print(f"✓ Observation shape correct: {obs.shape}")
        
        # Check all values in [-1, 1]
        if np.all(obs >= -1.0) and np.all(obs <= 1.0):
            print(f"✓ All observations in [-1, 1]")
        else:
            print(f"✗ Observations out of bounds: min={np.min(obs)}, max={np.max(obs)}")
            return False
        
        # Check for NaNs
        if np.isnan(obs).any():
            print(f"✗ NaN values in observation!")
            return False
        print(f"✓ No NaN values")
        
        env.close()
        return True
    except Exception as e:
        print(f"✗ Observation space test failed: {e}")
        traceback.print_exc()
        return False

def test_models():
    """Test that trained models can be loaded."""
    print("\n" + "="*80)
    print("TESTING TRAINED MODELS")
    print("="*80)
    
    all_ok = True
    
    # Test DQN
    try:
        from stable_baselines3 import DQN
        model = DQN.load("models/dqn/best_dqn")
        print("✓ DQN model loaded successfully")
    except Exception as e:
        print(f"✗ DQN model failed: {e}")
        all_ok = False
    
    # Test PPO
    try:
        from stable_baselines3 import PPO
        model = PPO.load("models/ppo/best_ppo")
        print("✓ PPO model loaded successfully")
    except Exception as e:
        print(f"✗ PPO model failed: {e}")
        all_ok = False
    
    # Test A2C
    try:
        from stable_baselines3 import A2C
        model = A2C.load("models/a2c/best_a2c")
        print("✓ A2C model loaded successfully")
    except Exception as e:
        print(f"✗ A2C model failed: {e}")
        all_ok = False
    
    # Test REINFORCE
    try:
        import torch
        from training.reinforce_training import Policy
        reinforce_model = Policy(hidden_size=256)
        reinforce_model.load_state_dict(torch.load("models/reinforce/best_reinforce.pth"))
        print("✓ REINFORCE model loaded successfully")
    except Exception as e:
        print(f"✗ REINFORCE model failed: {e}")
        all_ok = False
    
    return all_ok

def test_model_predictions():
    """Test that models can make predictions."""
    print("\n" + "="*80)
    print("TESTING MODEL PREDICTIONS")
    print("="*80)
    
    try:
        from environment import DaladalaEnv
        from stable_baselines3 import DQN, PPO, A2C
        import torch
        from training.reinforce_training import Policy
        
        env = DaladalaEnv()
        obs, _ = env.reset()
        
        # Test DQN
        try:
            dqn = DQN.load("models/dqn/best_dqn")
            action, _ = dqn.predict(obs, deterministic=True)
            print(f"✓ DQN prediction: action={action}")
        except Exception as e:
            print(f"✗ DQN prediction failed: {e}")
        
        # Test PPO
        try:
            ppo = PPO.load("models/ppo/best_ppo")
            action, _ = ppo.predict(obs, deterministic=True)
            print(f"✓ PPO prediction: action={action}")
        except Exception as e:
            print(f"✗ PPO prediction failed: {e}")
        
        # Test A2C
        try:
            a2c = A2C.load("models/a2c/best_a2c")
            action, _ = a2c.predict(obs, deterministic=True)
            print(f"✓ A2C prediction: action={action}")
        except Exception as e:
            print(f"✗ A2C prediction failed: {e}")
        
        # Test REINFORCE
        try:
            reinforce = Policy(hidden_size=256)
            reinforce.load_state_dict(torch.load("models/reinforce/best_reinforce.pth"))
            reinforce.eval()
            obs_tensor = torch.from_numpy(obs).float()
            probs = reinforce(obs_tensor)
            action = torch.argmax(probs).item()
            print(f"✓ REINFORCE prediction: action={action}")
        except Exception as e:
            print(f"✗ REINFORCE prediction failed: {e}")
        
        env.close()
        return True
    except Exception as e:
        print(f"✗ Model prediction test failed: {e}")
        traceback.print_exc()
        return False

def test_files_exist():
    """Verify all required files exist."""
    print("\n" + "="*80)
    print("TESTING FILE STRUCTURE")
    print("="*80)
    
    required_files = [
        "environment/daladala_env.py",
        "environment/rendering.py",
        "environment/__init__.py",
        "training/dqn_training.py",
        "training/ppo_training.py",
        "training/a2c_training.py",
        "training/reinforce_training.py",
        "models/dqn/best_dqn.zip",
        "models/ppo/best_ppo.zip",
        "models/a2c/best_a2c.zip",
        "models/reinforce/best_reinforce.pth",
        "main.py",
        "random_demo.py",
        "comparison_eval.py",
        "generate_report.py",
        "requirements.txt",
        "README.md",
    ]
    
    all_ok = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} NOT FOUND")
            all_ok = False
    
    return all_ok

def main():
    print("="*80)
    print("DALADALA PROJECT VALIDATION TEST SUITE")
    print("="*80)
    
    results = {
        "Imports": test_imports(),
        "Files": test_files_exist(),
        "Environment": test_environment(),
        "Observation Space": test_observation_space(),
        "Models": test_models(),
        "Model Predictions": test_model_predictions(),
    }
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:<30} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "="*80)
        print("✓ ALL TESTS PASSED - PROJECT READY FOR SUBMISSION")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("✗ SOME TESTS FAILED - FIX ISSUES BEFORE SUBMISSION")
        print("="*80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
