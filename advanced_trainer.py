"""
Advanced Trainer - Optimized for Winning
Uses curriculum learning and advanced PPO parameters
"""
import os
import time
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback, CallbackList
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import plot_results
import matplotlib.pyplot as plt
from stable_web_env import StableWebSpaceInvadersEnv
from get_high_score import get_current_high_score
import torch
import torch.nn as nn

class WinningCallback(BaseCallback):
    """Callback to detect when we beat the high score"""

    def __init__(self, target_score=25940, check_freq=1000, verbose=1):
        super(WinningCallback, self).__init__(verbose)
        self.target_score = target_score
        self.check_freq = check_freq
        self.best_score = 0
        self.episode_scores = []
        self.episode_count = 0
        self.start_time = time.time()

    def _on_step(self) -> bool:
        # Check every check_freq steps
        if self.n_calls % self.check_freq == 0:
            # Get current high score
            current_high = get_current_high_score()
            if current_high > self.target_score:
                self.target_score = current_high
                print(f"Updated target score to {self.target_score}")

            # Check if we have any episode scores
            if len(self.episode_scores) > 0:
                recent_avg = np.mean(self.episode_scores[-10:])  # Last 10 episodes
                self.best_score = max(self.best_score, max(self.episode_scores))

                elapsed = time.time() - self.start_time
                hours = elapsed / 3600

                print(f"Training Progress:")
                print(f"   Episodes: {self.episode_count}")
                print(f"   Best Score: {self.best_score}")
                print(f"   Recent Avg: {recent_avg:.1f}")
                print(f"   Target: {self.target_score}")
                print(f"   Training Time: {hours:.1f} hours")
                print(f"   Progress: {min(100, (self.best_score / self.target_score) * 100):.1f}%")

                # Check for victory
                if self.best_score >= self.target_score:
                    print(f"VICTORY! Beat high score {self.target_score} with {self.best_score}")
                    return False  # Stop training

        return True

    def _on_rollout_end(self) -> None:
        # Extract episode score from info
        if hasattr(self.locals, 'infos') and self.locals['infos']:
            for info in self.locals['infos']:
                if isinstance(info, dict) and 'episode_score' in info:
                    score = info['episode_score']
                    self.episode_scores.append(score)
                    self.episode_count += 1
                    break

class CurriculumLearning:
    """Curriculum learning to gradually increase difficulty"""

    def __init__(self, max_steps=1500):
        self.max_steps = max_steps
        self.current_max_steps = 500  # Start with shorter episodes
        self.increase_threshold = 1000  # Increase after this many episodes
        self.episode_count = 0

    def get_max_steps(self):
        """Get current max steps based on progress"""
        self.episode_count += 1

        if self.episode_count % self.increase_threshold == 0:
            self.current_max_steps = min(self.max_steps, self.current_max_steps + 200)
            print(f"Curriculum: Increased max steps to {self.current_max_steps}")

        return self.current_max_steps

def create_optimized_env(headless=True):
    """Create environment with optimized settings"""
    def make_env():
        env = StableWebSpaceInvadersEnv(headless=headless)
        env.max_steps = 500  # Will be updated by curriculum
        return Monitor(env)

    return DummyVecEnv([make_env])

def create_optimized_ppo(env):
    """Create PPO with optimized hyperparameters for Space Invaders"""

    # Custom CNN policy optimized for Space Invaders
    policy_kwargs = dict(
        features_extractor_class=CustomCNN,
        features_extractor_kwargs=dict(features_dim=512),
        net_arch=dict(pi=[256, 128], vf=[256, 128]),
        activation_fn=nn.ReLU,
    )

    model = PPO(
        "CnnPolicy",
        env,
        policy_kwargs=policy_kwargs,
        learning_rate=3e-4,  # Lower learning rate for stability
        n_steps=2048,        # Larger batch size
        batch_size=64,       # Smaller mini-batch
        n_epochs=10,         # More epochs per update
        gamma=0.99,          # High discount factor for long-term rewards
        gae_lambda=0.95,     # GAE parameter
        clip_range=0.2,      # PPO clip range
        clip_range_vf=None,  # No value clipping
        normalize_advantage=True,
        ent_coef=0.01,       # Small entropy bonus
        vf_coef=0.5,         # Value function coefficient
        max_grad_norm=0.5,   # Gradient clipping
        use_sde=False,       # No state-dependent exploration
        sde_sample_freq=-1,
        target_kl=None,      # No target KL
        tensorboard_log="./tensorboard/",
        verbose=1
    )

    return model

class CustomCNN(nn.Module):
    """Custom CNN optimized for Space Invaders"""

    def __init__(self, observation_space, features_dim=512):
        super(CustomCNN, self).__init__()
        n_input_channels = observation_space.shape[0]

        self.cnn = nn.Sequential(
            nn.Conv2d(n_input_channels, 32, kernel_size=8, stride=4, padding=0),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=0),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=0),
            nn.ReLU(),
            nn.Flatten(),
        )

        # Compute shape by doing one forward pass
        with torch.no_grad():
            n_flatten = self.cnn(
                torch.as_tensor(observation_space.sample()[None]).float()
            ).shape[1]

        self.linear = nn.Sequential(nn.Linear(n_flatten, features_dim), nn.ReLU())

        # Set features_dim attribute for Stable Baselines
        self.features_dim = features_dim

    def forward(self, observations):
        return self.linear(self.cnn(observations))

def train_advanced_model(total_timesteps=5000000, save_freq=50000):
    """Train model with advanced techniques"""

    print("Starting Advanced Training for Space Invaders")
    print(f"Target: Beat high score of {get_current_high_score()}")

    # Create environment
    env = create_optimized_env(headless=True)

    # Create model
    model = create_optimized_ppo(env)

    # Setup callbacks
    target_score = get_current_high_score()
    winning_callback = WinningCallback(target_score=target_score, check_freq=5000)
    curriculum = CurriculumLearning()

    # Custom callback to update curriculum
    class CurriculumCallback(BaseCallback):
        def _on_step(self):
            # Update max steps for all environments
            new_max_steps = curriculum.get_max_steps()
            for env_idx in range(env.num_envs):
                env.envs[env_idx].env.max_steps = new_max_steps
            return True

    curriculum_callback = CurriculumCallback()

    callbacks = CallbackList([winning_callback, curriculum_callback])

    # Training loop with periodic saving
    try:
        for i in range(0, total_timesteps, save_freq):
            remaining = min(save_freq, total_timesteps - i)

            print(f"Training segment {i//save_freq + 1}, steps: {remaining}")

            # Train for this segment
            model.learn(
                total_timesteps=remaining,
                callback=callbacks,
                reset_num_timesteps=False,
                tb_log_name="advanced_space_invaders"
            )

            # Save checkpoint
            checkpoint_path = f"models/advanced_checkpoint_{i+remaining}.zip"
            model.save(checkpoint_path)
            print(f"Saved checkpoint: {checkpoint_path}")

            # Check if we won
            if winning_callback.best_score >= target_score:
                print("Training completed - VICTORY ACHIEVED!")
                break

    except KeyboardInterrupt:
        print("Training interrupted by user")

    # Save final model
    final_path = "models/advanced_final.zip"
    model.save(final_path)
    print(f"Saved final model: {final_path}")

    # Cleanup
    env.close()

    return model

def evaluate_model(model_path, num_episodes=10):
    """Evaluate trained model"""
    print(f"Evaluating model: {model_path}")

    env = create_optimized_env(headless=False)  # Show browser for evaluation
    model = PPO.load(model_path)

    scores = []
    for episode in range(num_episodes):
        obs = env.reset()
        done = False
        episode_score = 0
        steps = 0

        while not done and steps < 2000:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            episode_score = max(episode_score, info[0].get('episode_score', 0))
            steps += 1

        scores.append(episode_score)
        print(f"Episode {episode + 1}: {episode_score} points")

    env.close()

    avg_score = np.mean(scores)
    max_score = max(scores)
    print(f"Evaluation Results:")
    print(f"   Average Score: {avg_score:.1f}")
    print(f"   Max Score: {max_score}")
    print(f"   Target: {get_current_high_score()}")

    return avg_score, max_score

def main():
    """Main training function"""
    import argparse

    parser = argparse.ArgumentParser(description='Advanced Space Invaders Training')
    parser.add_argument('--mode', choices=['train', 'evaluate'], default='train',
                       help='Training mode')
    parser.add_argument('--model', type=str, default='models/advanced_final.zip',
                       help='Model path for evaluation')
    parser.add_argument('--timesteps', type=int, default=2000000,
                       help='Total training timesteps')

    args = parser.parse_args()

    if args.mode == 'train':
        train_advanced_model(total_timesteps=args.timesteps)
    elif args.mode == 'evaluate':
        evaluate_model(args.model)

if __name__ == "__main__":
    main()