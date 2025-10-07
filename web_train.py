"""
Web-Based PPO Training for Space Invaders
Trains directly on jordancota.site for perfect compatibility
"""
import os
import time
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv
from web_env import WebSpaceInvadersEnv
from get_high_score import get_current_high_score, get_high_score_info

class WebTrainingCallback(BaseCallback):
    """Callback to monitor training progress on web game"""
    
    def __init__(self, check_freq=1000, save_freq=5000, verbose=1):
        super(WebTrainingCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.save_freq = save_freq
        self.best_score = 0
        self.episode_scores = []
        
        # Get dynamic high score target
        print("🎯 Fetching current high score target...")
        self.target_score = get_current_high_score()
        print(f"🏆 Target to beat: {self.target_score:,} points")
    
    def _on_step(self) -> bool:
        # Check progress periodically
        if self.n_calls % self.check_freq == 0:
            # Get recent episode scores from environment info
            if hasattr(self.training_env, 'get_attr'):
                try:
                    infos = self.training_env.get_attr('episode_score')
                    if infos and infos[0] > 0:
                        current_score = infos[0]
                        
                        if current_score > self.best_score:
                            self.best_score = current_score
                            
                            # Save best model
                            model_path = f"models/web_best_{current_score}.zip"
                            self.model.save(model_path)
                            print(f"🏆 NEW BEST! Score: {current_score} - Saved: {model_path}")
                            
                            # Check if we beat the high score
                            if current_score > self.target_score:
                                print(f"🎉 HIGH SCORE BEATEN! {current_score} > {self.target_score}")
                                print("Training complete! Ready to submit score.")
                                return False  # Stop training
                        
                        progress = (current_score / self.target_score) * 100
                        print(f"📊 Step {self.n_calls}: Score={current_score}, Best={self.best_score}, Progress={progress:.2f}%")
                
                except Exception as e:
                    if self.verbose > 0:
                        print(f"Monitoring error: {e}")
        
        # Save model periodically
        if self.n_calls % self.save_freq == 0:
            checkpoint_path = f"models/web_checkpoint_{self.n_calls}.zip"
            self.model.save(checkpoint_path)
            print(f"💾 Checkpoint saved: {checkpoint_path}")
        
        return True

def create_web_env():
    """Create web-based environment"""
    return WebSpaceInvadersEnv(headless=True)  # Headless for faster training

def train_web_model(total_timesteps=100000):
    """Train PPO model directly on web game"""
    
    print("💻 WEB-BASED SPACE INVADERS TRAINING")
    print("=" * 50)
    
    # Get current leaderboard info
    high_score_info = get_high_score_info()
    target_score = high_score_info['score']
    
    print(f"� Current Leader: {high_score_info['name']} - {target_score:,} points (Level {high_score_info['level']})")
    print(f"�🎯 AI Target: Beat {target_score:,} points")
    print(f"⏱️  Training Steps: {total_timesteps:,}")
    print()
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Create environment
    print("🌐 Creating web environment...")
    env = DummyVecEnv([create_web_env])
    
    # Create PPO model optimized for visual input
    print("🤖 Creating PPO model...")
    model = PPO(
        "CnnPolicy",  # CNN policy for image observations
        env,
        verbose=1,
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01
    )
    
    # Create callback for monitoring
    callback = WebTrainingCallback(
        check_freq=1000,
        save_freq=5000,
        verbose=1
    )
    
    # Start training
    print("🚀 Starting web-based training...")
    print("This will train directly on jordancota.site for perfect compatibility!")
    print()
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=callback,
            progress_bar=False  # Disable progress bar to avoid dependency issues
        )
        
        # Save final model
        final_model_path = "models/web_final_model.zip"
        model.save(final_model_path)
        print(f"✅ Training complete! Final model saved: {final_model_path}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Training interrupted by user")
        interrupt_model_path = "models/web_interrupted_model.zip"
        model.save(interrupt_model_path)
        print(f"💾 Model saved: {interrupt_model_path}")
    
    except Exception as e:
        print(f"❌ Training error: {e}")
        error_model_path = "models/web_error_model.zip"
        model.save(error_model_path)
        print(f"💾 Error model saved: {error_model_path}")
    
    finally:
        env.close()

def evaluate_web_model(model_path, episodes=3):
    """Evaluate trained model on web game"""
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return
    
    print(f"🎮 Evaluating Web Model: {model_path}")
    print("=" * 40)
    
    # Load model
    model = PPO.load(model_path)
    
    # Create environment (visible for evaluation)
    env = WebSpaceInvadersEnv(headless=False)
    
    episode_scores = []
    
    try:
        for episode in range(episodes):
            print(f"\n🎬 Episode {episode + 1}/{episodes}")
            
            obs, _ = env.reset()
            episode_score = 0
            steps = 0
            
            while True:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, done, _, info = env.step(action)
                
                episode_score = info['score']
                steps += 1
                
                if steps % 100 == 0:
                    print(f"  Step {steps}: Score = {episode_score}")
                
                if done:
                    break
            
            episode_scores.append(episode_score)
            print(f"✅ Episode {episode + 1} Score: {episode_score}")
            
            # Short break between episodes
            time.sleep(2)
        
        # Results
        best_score = max(episode_scores)
        avg_score = sum(episode_scores) / len(episode_scores)
        
        print(f"\n📊 EVALUATION RESULTS:")
        print(f"Best Score: {best_score}")
        print(f"Average Score: {avg_score:.1f}")
        print(f"Target Score: 25,940")
        print(f"Progress: {(best_score / 25940) * 100:.2f}%")
        
        if best_score > 25940:
            print("🎉 HIGH SCORE BEATEN! Ready to submit!")
        
    except Exception as e:
        print(f"❌ Evaluation error: {e}")
    finally:
        env.close()

def main():
    print("🕹️  WEB-BASED SPACE INVADERS ML TRAINING")
    print("Trains directly on jordancota.site for perfect compatibility")
    print()
    
    while True:
        print("Choose an option:")
        print("1. Start Training (100K steps)")
        print("2. Extended Training (500K steps)")
        print("3. Evaluate Existing Model")
        print("4. Test Environment")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            train_web_model(100000)
        elif choice == '2':
            train_web_model(500000)
        elif choice == '3':
            # Find available models
            model_dir = 'models'
            if os.path.exists(model_dir):
                models = [f for f in os.listdir(model_dir) if f.endswith('.zip')]
                if models:
                    print("\nAvailable models:")
                    for i, model in enumerate(models):
                        print(f"{i+1}. {model}")
                    
                    try:
                        model_idx = int(input("Choose model: ")) - 1
                        if 0 <= model_idx < len(models):
                            model_path = os.path.join(model_dir, models[model_idx])
                            evaluate_web_model(model_path)
                        else:
                            print("Invalid selection")
                    except ValueError:
                        print("Invalid input")
                else:
                    print("No trained models found")
            else:
                print("No models directory found")
        elif choice == '4':
            env = WebSpaceInvadersEnv(headless=False)
            try:
                obs, _ = env.reset()
                print("Environment test - taking 5 random actions...")
                for i in range(5):
                    action = env.action_space.sample()
                    obs, reward, done, _, info = env.step(action)
                    print(f"Action: {action}, Score: {info['score']}, Done: {done}")
                    if done:
                        break
            finally:
                env.close()
        elif choice == '5':
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()