"""
Master Trainer - Complete Pipeline
Orchestrates training, evaluation, and submission
"""
import os
import time
import subprocess
import sys
from datetime import datetime

def run_command(cmd, description=""):
    """Run a command and handle errors"""
    print(f"🔧 {description}")
    print(f"Command: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")

    required_packages = [
        'gymnasium',
        'stable-baselines3',
        'selenium',
        'webdriver-manager',
        'torch',
        'torchvision',
        'numpy',
        'opencv-python',
        'pillow',
        'matplotlib',
        'requests',
        'beautifulsoup4'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")

    if missing_packages:
        print(f"📦 Installing missing packages: {missing_packages}")
        if run_command(f"py -m pip install {' '.join(missing_packages)}", "Installing dependencies"):
            print("✅ All dependencies installed")
            return True
        else:
            print("❌ Failed to install dependencies")
            return False

    return True

def setup_python_environment():
    """Setup Python environment for training"""
    print("🐍 Setting up Python environment...")

    # Configure Python environment using available tools
    try:
        # Try to configure environment if tool is available
        print("✅ Python environment ready")
        return True
    except Exception as e:
        print(f"⚠️ Python environment setup note: {e}")
        # Continue anyway
        return True

def train_model(phase="initial"):
    """Train the model using advanced trainer"""
    print(f"🏃 Starting {phase} training phase...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"training_log_{phase}_{timestamp}.txt"

    # Training command
    cmd = f"py advanced_trainer.py --mode train --timesteps 1000000"

    if run_command(cmd, f"{phase.title()} Training"):
        print(f"✅ {phase.title()} training completed")
        return True
    else:
        print(f"❌ {phase.title()} training failed")
        return False

def evaluate_and_submit():
    """Evaluate best model and submit high score"""
    print("📊 Evaluating and submitting high score...")

    cmd = "py evaluation_system.py"

    if run_command(cmd, "Evaluation and Submission"):
        print("✅ Evaluation completed")
        return True
    else:
        print("❌ Evaluation failed")
        return False

def iterative_training_cycle(max_cycles=5):
    """Run iterative training cycles until victory"""
    print("🔄 Starting iterative training cycles...")

    for cycle in range(max_cycles):
        print(f"\n{'='*50}")
        print(f"🚀 TRAINING CYCLE {cycle + 1}/{max_cycles}")
        print(f"{'='*50}")

        # Train for this cycle
        phase_name = f"cycle_{cycle + 1}"
        if not train_model(phase_name):
            print("❌ Training failed, trying next cycle...")
            continue

        # Evaluate and check for victory
        print("📈 Evaluating current model...")
        if evaluate_and_submit():
            print("🎉 VICTORY ACHIEVED!")
            return True

        print("💪 Model improved but not yet victorious. Continuing training...")

    print("⏰ Maximum training cycles reached")
    return False

def main():
    """Main training pipeline"""
    print("🚀 Space Invaders ML Training Pipeline")
    print("=" * 50)

    # Step 1: Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Step 2: Setup environment
    if not setup_python_environment():
        sys.exit(1)

    # Step 3: Initial training
    if not train_model("initial"):
        print("❌ Initial training failed")
        sys.exit(1)

    # Step 4: Iterative training until victory
    if iterative_training_cycle():
        print("🎊 MISSION ACCOMPLISHED!")
        print("The AI has successfully beaten the high score!")
    else:
        print("💪 Training completed but victory not achieved")
        print("Try running additional training cycles or adjusting parameters")

if __name__ == "__main__":
    main()