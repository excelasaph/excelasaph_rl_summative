# run_pipeline.py
"""
Complete Pipeline Runner
Executes all steps: training, demo, comparison, report generation, and testing.
Run this to do everything in one go (takes ~3 hours).
"""
import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and report status."""
    print("\n" + "="*80)
    print(f"{description}")
    print("="*80)
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=isinstance(cmd, str), check=True)
        print(f"\n✓ {description} COMPLETED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} FAILED (exit code {e.returncode})")
        return False
    except Exception as e:
        print(f"\n✗ {description} FAILED: {e}")
        return False

def main():
    print("\n" + "="*80)
    print("DALADALA AGENT - COMPLETE PIPELINE")
    print("="*80)
    print("\nThis script will execute:")
    print("  1. Validation tests")
    print("  2. DQN training (12 configs)")
    print("  3. PPO training (12 configs)")
    print("  4. A2C training (12 configs)")
    print("  5. REINFORCE training (12 configs)")
    print("  6. Random demo generation")
    print("  7. Model comparison evaluation")
    print("  8. Report generation")
    print("\nEstimated time: 2.5-3.5 hours on CPU")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    start_time = time.time()
    results = {}
    
    # 1. Validation
    results["Validation"] = run_command(
        [sys.executable, "test_setup.py"],
        "STEP 1/8: Running validation tests"
    )
    
    # 2. DQN Training
    results["DQN Training"] = run_command(
        [sys.executable, "training/dqn_training.py"],
        "STEP 2/8: Training DQN (12 configurations)"
    )
    
    # 3. PPO Training
    results["PPO Training"] = run_command(
        [sys.executable, "training/ppo_training.py"],
        "STEP 3/8: Training PPO (12 configurations)"
    )
    
    # 4. A2C Training
    results["A2C Training"] = run_command(
        [sys.executable, "training/a2c_training.py"],
        "STEP 4/8: Training A2C (12 configurations)"
    )
    
    # 5. REINFORCE Training
    results["REINFORCE Training"] = run_command(
        [sys.executable, "training/reinforce_training.py"],
        "STEP 5/8: Training REINFORCE (12 configurations)"
    )
    
    # 6. Random Demo
    results["Random Demo"] = run_command(
        [sys.executable, "random_demo.py"],
        "STEP 6/8: Generating random demo GIF"
    )
    
    # 7. Model Comparison
    results["Model Comparison"] = run_command(
        [sys.executable, "comparison_eval.py"],
        "STEP 7/8: Comparing all models (100 episodes each)"
    )
    
    # 8. Report Generation
    results["Report Generation"] = run_command(
        [sys.executable, "generate_report.py"],
        "STEP 8/8: Generating analysis report"
    )
    
    # Summary
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    
    print("\n" + "="*80)
    print("PIPELINE EXECUTION SUMMARY")
    print("="*80)
    
    for step, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{step:<30} {status}")
    
    print("\n" + "-"*80)
    print(f"Total time: {hours}h {minutes}m")
    print("-"*80)
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ PIPELINE COMPLETED SUCCESSFULLY!")
        print("\nNext steps:")
        print("  1. Review results/comparison_results.json")
        print("  2. Check results/*.png graphs")
        print("  3. Run 'python main.py' to see best agent in action")
        print("  4. Create PDF report from graphs + analysis_report.txt")
        print("  5. Submit to Canvas")
    else:
        print("\n✗ PIPELINE HAD FAILURES")
        print("\nFailed steps:")
        for step, success in results.items():
            if not success:
                print(f"  - {step}")
        print("\nRun individual scripts to debug:")
        print("  - python test_setup.py")
        print("  - python training/[algorithm]_training.py")
        print("  - python comparison_eval.py")
        print("  - python generate_report.py")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
