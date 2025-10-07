"""
Winning Model Trainer - Robust Web Training for High Scores
Handles browser issues and focuses on beating 25,940 points
"""
import os
import time
import traceback
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from web_env import WebSpaceInvadersEnv
from get_high_score import get_current_high_score, get_high_score_info

class WinningCallback(BaseCallback):
    """Callback focused on winning performance"""
    
    def __init__(self, check_freq=2000, save_freq=10000):
        super().__init__()
        self.check_freq = check_freq
        self.save_freq = save_freq
        self.best_score = 0
        self.target_score = 25940
        self.episodes_completed = 0
        self.last_check = 0
        
        print("🎯 WINNING MODEL TRAINER")
        print("=" * 40)
        print(f"Target to beat: {self.target_score:,} points")
        print(f"Current record holder: John H")
        print()
    
    def _on_step(self) -> bool:
        # Check progress less frequently to avoid overhead
        if self.n_calls - self.last_check >= self.check_freq:
            self.last_check = self.n_calls
            
            try:
                # Get episode info from environment
                if hasattr(self.training_env, 'get_attr'):
                    episode_scores = self.training_env.get_attr('episode_score')
                    if episode_scores and episode_scores[0] > 0:
                        current_score = episode_scores[0]
                        
                        if current_score > self.best_score:
                            self.best_score = current_score
                            
                            # Save every improvement
                            model_path = f"models/winning_score_{current_score}.zip"
                            os.makedirs('models', exist_ok=True)
                            self.model.save(model_path)
                            
                            progress = (current_score / self.target_score) * 100
                            print(f"🏆 NEW RECORD! Score: {current_score:,} ({progress:.1f}% to target)")
                            
                            # Check if we won!
                            if current_score > self.target_score:
                                print(f"🎉 VICTORY! {current_score:,} > {self.target_score:,}")
                                print("HIGH SCORE BEATEN! Training complete!")
                                return False  # Stop training
                        
                        self.episodes_completed += 1
                        if self.episodes_completed % 10 == 0:
                            elapsed = time.time() - self.training_env.start_time if hasattr(self.training_env, 'start_time') else 0
                            print(f"📊 Episode {self.episodes_completed} | Best: {self.best_score:,} | Steps: {self.n_calls:,} | Time: {elapsed/60:.1f}m")
            
            except Exception as e:
                print(f"Callback error: {e}")
        
        # Regular saves
        if self.n_calls % self.save_freq == 0:
            checkpoint_path = f"models/winning_checkpoint_{self.n_calls}.zip"
            os.makedirs('models', exist_ok=True)
            self.model.save(checkpoint_path)
            print(f"💾 Checkpoint: {checkpoint_path}")
        
        return True

def train_winning_model():
    """Train a model focused on winning"""
    
    print("🚀 WINNING MODEL TRAINING")
    print("Starting intensive training to beat 25,940 points...")
    print()
    
    # Ensure models directory exists
    os.makedirs('models', exist_ok=True)
    
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            print(f"🌐 Attempt {retry_count + 1}/{max_retries}: Setting up environment...")
            
            # Create environment with retries
            env = WebSpaceInvadersEnv(headless=True)
            env.start_time = time.time()
            
            print("🤖 Creating optimized PPO model...")
            
            # Optimized hyperparameters for game performance
            model = PPO(
                "CnnPolicy",
                env,
                verbose=1,
                learning_rate=0.0003,
                n_steps=4096,        # Larger buffer for better learning
                batch_size=128,      # Larger batches
                n_epochs=10,         # More epochs per update
                gamma=0.995,         # Slightly higher discount for long-term rewards
                gae_lambda=0.95,
                clip_range=0.2,
                ent_coef=0.01,       # Encourage exploration
                vf_coef=0.5,
                max_grad_norm=0.5,
                target_kl=0.01
            )
            
            # Create winning callback
            callback = WinningCallback(check_freq=2000, save_freq=10000)
            
            print("🎮 Starting intensive training...")
            print("Training until we beat 25,940 points!")
            print()
            
            # Train with high timesteps
            total_timesteps = 1000000  # 1 million steps
            
            start_time = time.time()
            
            model.learn(
                total_timesteps=total_timesteps,
                callback=callback,
                progress_bar=False
            )
            
            elapsed = time.time() - start_time
            
            # Save final model
            final_path = "models/winning_final.zip"
            model.save(final_path)
            
            print(f"\n✅ TRAINING COMPLETE!")
            print(f"Time elapsed: {elapsed/3600:.1f} hours")
            print(f"Final model: {final_path}")
            print(f"Best score achieved: {callback.best_score:,}")
            
            if callback.best_score > 25940:
                print("🏆 HIGH SCORE BEATEN! Ready for submission!")
            else:
                print(f"📈 Progress: {(callback.best_score/25940)*100:.1f}% to target")
            
            env.close()
            return callback.best_score
            
        except KeyboardInterrupt:
            print("\n⏹️  Training interrupted by user")
            try:
                interrupt_path = f"models/winning_interrupted_{int(time.time())}.zip"
                model.save(interrupt_path)
                print(f"💾 Model saved: {interrupt_path}")
                env.close()
            except:
                pass
            return 0
            
        except Exception as e:
            retry_count += 1
            print(f"❌ Training error (attempt {retry_count}): {e}")
            print(f"Traceback: {traceback.format_exc()}")
            
            try:
                error_path = f"models/winning_error_{retry_count}.zip"
                if 'model' in locals():
                    model.save(error_path)
                    print(f"💾 Error model saved: {error_path}")
            except:
                pass
            
            try:
                if 'env' in locals():
                    env.close()
            except:
                pass
            
            if retry_count < max_retries:
                print(f"🔄 Retrying in 10 seconds...")
                time.sleep(10)
            else:
                print("❌ Max retries exceeded")
                return 0
    
    return 0

def evaluate_winning_model():
    """Evaluate the best model we've trained"""
    
    print("🧪 EVALUATING WINNING MODELS")
    print("=" * 35)
    
    models_dir = "models"
    if not os.path.exists(models_dir):
        print("❌ No models found! Train a model first.")
        return
    
    # Find all models
    models = [f for f in os.listdir(models_dir) if f.endswith('.zip')]
    if not models:
        print("❌ No models found!")
        return
    
    # Sort by score if possible
    def get_score_from_name(name):
        try:
            if 'score_' in name:
                return int(name.split('score_')[1].split('.')[0])
        except:
            pass
        return 0
    
    models.sort(key=get_score_from_name, reverse=True)
    
    print("Available models:")
    for i, model in enumerate(models[:5]):  # Show top 5
        score = get_score_from_name(model)
        if score > 0:
            print(f"{i+1}. {model} (Score: {score:,})")
        else:
            print(f"{i+1}. {model}")
    
    # Test the best model
    best_model = models[0]
    model_path = os.path.join(models_dir, best_model)
    
    print(f"\n🎮 Testing best model: {best_model}")
    
    try:
        model = PPO.load(model_path)
        env = WebSpaceInvadersEnv(headless=False)  # Visible for evaluation
        
        episode_scores = []
        
        for episode in range(3):
            print(f"\n🎬 Episode {episode + 1}/3")
            
            obs, _ = env.reset()
            episode_score = 0
            steps = 0
            max_steps = 2000
            
            while steps < max_steps:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, done, _, info = env.step(action)
                
                episode_score = info['score']
                steps += 1
                
                if steps % 200 == 0:
                    print(f"  Step {steps}: Score = {episode_score:,}")
                
                if done:
                    break
            
            episode_scores.append(episode_score)
            print(f"✅ Episode {episode + 1} Final Score: {episode_score:,}")
        
        best_score = max(episode_scores)
        avg_score = sum(episode_scores) / len(episode_scores)
        
        print(f"\n📊 EVALUATION RESULTS:")
        print(f"Best Score: {best_score:,}")
        print(f"Average Score: {avg_score:,.0f}")
        print(f"Target: 25,940")
        print(f"Progress: {(best_score/25940)*100:.1f}%")
        
        if best_score > 25940:
            print("🎉 HIGH SCORE BEATEN! Ready to submit!")
        
        env.close()
        
    except Exception as e:
        print(f"❌ Evaluation error: {e}")

def main():
    """Main training interface"""
    
    print("🕹️  WINNING MODEL TRAINER")
    print("Beat the 25,940 point high score!")
    print()
    
    while True:
        print("Choose an option:")
        print("1. 🚀 Start Winning Training (1M steps)")
        print("2. 🧪 Evaluate Best Model")
        print("3. 🏆 Submit High Score")
        print("4. 📊 Check Current Leaderboard")
        print("5. ❌ Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            score = train_winning_model()
            if score > 25940:
                print("🎉 CONGRATULATIONS! You beat the high score!")
        
        elif choice == '2':
            evaluate_winning_model()
        
        elif choice == '3':
            from web_submit import main as submit_main
            submit_main()
        
        elif choice == '4':
            info = get_high_score_info()
            print(f"\n🏆 Current High Score: {info['score']:,} by {info['name']}")
        
        elif choice == '5':
            break
        
        else:
            print("Invalid choice!")
        
        print()

if __name__ == "__main__":
    main()