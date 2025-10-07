"""
Training Monitor - Check training progress in real-time
"""
import os
import time
from datetime import datetime

def monitor_training():
    """Monitor training progress by checking model files and logs"""
    
    print("📊 TRAINING MONITOR")
    print("=" * 25)
    print("Monitoring training progress...\n")
    
    models_dir = "models"
    last_model_count = 0
    start_time = time.time()
    
    while True:
        try:
            # Check for new models
            if os.path.exists(models_dir):
                models = [f for f in os.listdir(models_dir) if f.endswith('.zip')]
                model_count = len(models)
                
                if model_count > last_model_count:
                    print(f"🆕 New model detected! Total models: {model_count}")
                    for model in models[-3:]:  # Show last 3 models
                        model_path = os.path.join(models_dir, model)
                        mod_time = os.path.getmtime(model_path)
                        mod_time_str = datetime.fromtimestamp(mod_time).strftime("%H:%M:%S")
                        print(f"   📁 {model} (created: {mod_time_str})")
                    print()
                    last_model_count = model_count
                
                # Show current status
                elapsed = time.time() - start_time
                elapsed_str = f"{elapsed/60:.1f} minutes"
                
                print(f"\r⏱️  Training time: {elapsed_str} | Models: {model_count}", end="", flush=True)
            
            time.sleep(5)  # Check every 5 seconds
            
        except KeyboardInterrupt:
            print("\n\n📊 TRAINING SUMMARY:")
            if os.path.exists(models_dir):
                models = [f for f in os.listdir(models_dir) if f.endswith('.zip')]
                print(f"Total models created: {len(models)}")
                for model in models:
                    print(f"  📁 {model}")
            break
        except Exception as e:
            print(f"\nMonitor error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_training()