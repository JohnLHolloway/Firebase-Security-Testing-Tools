"""
Fixed Training Script - Start Fresh with Working Environment
"""
import os
import time
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_web_env import StableWebSpaceInvadersEnv
from get_high_score import get_current_high_score
import sys
import io

# Fix console encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class DetailedCallback(BaseCallback):
    """Monitor training progress with detailed logging"""

    def __init__(self, target_score=25940, check_freq=500, save_freq=5000, verbose=1):
        super(DetailedCallback, self).__init__(verbose)
        self.target_score = target_score
        self.check_freq = check_freq
        self.save_freq = save_freq
        self.best_score = 0
        self.episode_scores = []
        self.episode_count = 0
        self.start_time = time.time()
        self.last_save_step = 0

    def _on_step(self) -> bool:
        # Periodic progress report (more frequent for short runs)
        if self.n_calls % self.check_freq == 0 and self.n_calls > 0:
            elapsed = time.time() - self.start_time
            minutes = elapsed / 60

            if len(self.episode_scores) > 0:
                recent_scores = self.episode_scores[-10:]  # Last 10 episodes
                recent_avg = np.mean(recent_scores)
                self.best_score = max(self.best_score, max(self.episode_scores))

                print(f"\n{'='*60}")
                print(f"[UPDATE] Step {self.n_calls}")
                print(f"{'='*60}")
                print(f"Episodes: {self.episode_count} | Time: {minutes:.1f} min")
                print(f"Best Score: {self.best_score}")
                print(f"Avg (last 10): {recent_avg:.1f}")
                print(f"Recent scores: {recent_scores[-5:]}")  # Show last 5
                print(f"Target: {self.target_score} ({min(100, (self.best_score / self.target_score) * 100):.1f}%)")
                print(f"{'='*60}\n")

                # Check for victory
                if self.best_score >= self.target_score:
                    print(f"\n*** VICTORY! Beat target score {self.target_score} with {self.best_score} ***\n")
                    return False  # Stop training

        # Periodic model saving
        if self.n_calls - self.last_save_step >= self.save_freq:
            save_path = f"models/checkpoint_{self.n_calls}.zip"
            self.model.save(save_path)
            print(f"[CHECKPOINT] Saved model to {save_path}")
            self.last_save_step = self.n_calls

        return True

    def _on_rollout_end(self) -> None:
        # Extract episode info
        if hasattr(self.locals, 'infos') and self.locals['infos']:
            for info in self.locals['infos']:
                if isinstance(info, dict) and 'episode_score' in info:
                    score = info['episode_score']
                    if score > 0:  # Only count real episodes
                        self.episode_scores.append(score)
                        self.episode_count += 1
                        print(f"Episode {self.episode_count} completed - Score: {score}")
                    break

def create_training_env(headless=True):
    """Create vectorized environment for training"""
    def make_env():
        env = StableWebSpaceInvadersEnv(headless=headless)
        return Monitor(env)

    return DummyVecEnv([make_env])

def train_model(total_timesteps=500000, headless=True):
    """Train the model with fixed environment"""

    print("\n" + "="*60)
    print("STARTING TRAINING - FIXED ENVIRONMENT")
    print("="*60)

    target_score = get_current_high_score()
    print(f"Target High Score: {target_score}")
    print(f"Total Training Steps: {total_timesteps:,}")
    print(f"Headless Mode: {headless}")
    print("="*60 + "\n")

    # Create models directory
    os.makedirs("models", exist_ok=True)

    # Create environment
    print("Creating training environment...")
    env = create_training_env(headless=headless)
    print("Environment created successfully!\n")

    # Create model with simpler but effective parameters
    print("Creating PPO model...")
    model = PPO(
        "CnnPolicy",
        env,
        learning_rate=2.5e-4,      # Standard Atari learning rate
        n_steps=128,                # Smaller for faster updates
        batch_size=32,              # Smaller batch
        n_epochs=4,                 # Fewer epochs per update
        gamma=0.99,                 # Standard discount
        gae_lambda=0.95,
        clip_range=0.1,             # Standard PPO clip
        ent_coef=0.01,              # Encourage exploration
        vf_coef=0.5,
        max_grad_norm=0.5,
        tensorboard_log="./tensorboard/",
        verbose=1
    )
    print("Model created!\n")

    # Setup callback with frequent updates
    callback = DetailedCallback(
        target_score=target_score,
        check_freq=500,  # Update every 500 steps
        save_freq=5000   # Save every 5K steps
    )

    # Train
    print("Starting training loop...\n")
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=callback,
            tb_log_name="fixed_training"
        )
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
    except Exception as e:
        print(f"\n\nTraining stopped due to error: {e}")
        import traceback
        traceback.print_exc()

    # Save final model
    final_path = "models/trained_model_final.zip"
    model.save(final_path)
    print(f"\n[SAVED] Final model: {final_path}")

    # Cleanup
    env.close()
    print("\nTraining complete!")

    return model

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Train Space Invaders AI')
    parser.add_argument('--timesteps', type=int, default=500000,
                       help='Total training timesteps')
    parser.add_argument('--visible', action='store_true',
                       help='Show browser (not headless)')

    args = parser.parse_args()

    train_model(
        total_timesteps=args.timesteps,
        headless=not args.visible
    )
