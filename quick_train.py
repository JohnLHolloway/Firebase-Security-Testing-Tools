"""
Quick Training Script with Frequent Updates
Simple training loop with detailed progress monitoring
"""
import os
import time
from stable_baselines3 import PPO
from web_env import WebSpaceInvadersEnv
from get_high_score import get_current_high_score, get_high_score_info

def quick_train():
    """Quick training with frequent progress updates"""
    
    print("🚀 QUICK WEB TRAINING")
    print("=" * 30)
    
    # Get target score
    target_info = get_high_score_info()
    target_score = target_info['score']
    
    print(f"🏆 Current Leader: {target_info['name']} - {target_score:,} points")
    print(f"🎯 AI Target: Beat {target_score:,} points")
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Create environment
    print("\n🌐 Setting up web environment...")
    env = WebSpaceInvadersEnv(headless=True)  # Headless for speed
    
    # Create simple PPO model
    print("🤖 Creating PPO model...")
    model = PPO(
        "CnnPolicy",
        env,
        verbose=1,
        learning_rate=0.0003,
        n_steps=1024,  # Smaller steps for faster feedback
        batch_size=32,
        n_epochs=5,
        gamma=0.99
    )
    
    print("🎮 Starting training...")
    print("Training will show updates every 1000 steps\n")
    
    best_score = 0
    
    try:
        # Train in smaller chunks for frequent updates
        total_steps = 50000  # Start with 50K steps
        chunk_size = 1000
        
        for step in range(0, total_steps, chunk_size):
            print(f"📈 Training steps {step} to {step + chunk_size}...")
            
            # Train for this chunk
            model.learn(total_timesteps=chunk_size, reset_num_timesteps=False)
            
            # Quick evaluation every 5000 steps
            if step % 5000 == 0 and step > 0:
                print(f"\n🧪 Quick evaluation at step {step}...")
                
                # Test for 1 episode
                obs, _ = env.reset()
                episode_score = 0
                steps_taken = 0
                
                while steps_taken < 500:  # Max 500 steps per test
                    action, _ = model.predict(obs, deterministic=True)
                    obs, reward, done, _, info = env.step(action)
                    episode_score = info['score']
                    steps_taken += 1
                    
                    if done:
                        break
                
                if episode_score > best_score:
                    best_score = episode_score
                    model_path = f"models/quick_best_{best_score}.zip"
                    model.save(model_path)
                    print(f"🏆 NEW BEST! Score: {best_score} - Saved: {model_path}")
                    
                    if best_score > target_score:
                        print(f"🎉 TARGET BEATEN! {best_score} > {target_score}")
                        print("Training complete!")
                        break
                else:
                    print(f"📊 Score: {episode_score}, Best: {best_score}")
                
                progress = (best_score / target_score) * 100
                print(f"Progress: {progress:.2f}% toward target\n")
        
        # Save final model
        final_path = "models/quick_final.zip"
        model.save(final_path)
        print(f"✅ Training complete! Final model: {final_path}")
        print(f"Best score achieved: {best_score}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Training stopped by user")
        interrupt_path = "models/quick_interrupted.zip"
        model.save(interrupt_path)
        print(f"💾 Model saved: {interrupt_path}")
    
    except Exception as e:
        print(f"\n❌ Training error: {e}")
        error_path = "models/quick_error.zip"
        model.save(error_path)
        print(f"💾 Error model saved: {error_path}")
    
    finally:
        env.close()

if __name__ == "__main__":
    quick_train()