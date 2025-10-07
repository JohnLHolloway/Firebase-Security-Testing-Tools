import os
import time
import numpy as np
import torch
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.vec_env import DummyVecEnv
import gymnasium as gym
from gymnasium import spaces
from typing import Dict, List, Optional, Tuple, Type, Union
import cv2

class SpaceInvadersEnv(gym.Env):
    """Custom Environment for Space Invaders game based on Gymnasium."""
    
    metadata = {'render_modes': ['human']}
    
    def __init__(self, game_controller, vision_system):
        """Initialize the environment with game controller and vision system."""
        super().__init__()
        
        # Game interaction components
        self.controller = game_controller
        self.vision = vision_system
        
        # Define action and observation spaces
        # Actions: 0 = do nothing, 1 = move left, 2 = move right, 3 = shoot
        self.action_space = spaces.Discrete(4)
        
        # Observation space: processed game state
        # We'll use a simplified representation with key game elements
        self.observation_space = spaces.Box(
            low=0, high=255, 
            shape=(84, 84, 1),  # Downsampled grayscale image
            dtype=np.uint8
        )
        
        # Environment state
        self.current_score = 0
        self.current_lives = 3
        self.prev_enemies_count = 0
        self.steps_since_last_shot = 0
        self.last_action = 0
        self.consecutive_same_actions = 0
        self.steps_without_score = 0
        self.total_steps = 0
        
        # For rendering
        self.current_frame = None
    
    def _get_observation(self):
        """Process the game state into the observation for the agent."""
        # Get screenshot and process it
        screenshot = self.controller.get_screenshot()
        if screenshot is None:
            return np.zeros((84, 84, 1), dtype=np.uint8)
        
        game_state = self.vision.process_screenshot(screenshot)
        self.current_frame = game_state['raw_image']
        
        # Convert the image to grayscale and resize to 84x84
        gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (84, 84))
        
        return np.expand_dims(resized, axis=2)  # Shape: (84, 84, 1)
    
    def step(self, action):
        """Execute the action and return new state, reward, done flag, and info."""
        # Track if same action is repeated
        if action == self.last_action:
            self.consecutive_same_actions += 1
        else:
            self.consecutive_same_actions = 0
            self.last_action = action
        
        # Execute the selected action
        if action == 0:  # Do nothing
            pass
        elif action == 1:  # Move left
            self.controller.move_left()
        elif action == 2:  # Move right
            self.controller.move_right()
        elif action == 3:  # Shoot
            self.controller.shoot()
            self.steps_since_last_shot = 0
        
        # Wait a short time for action to take effect
        time.sleep(0.05)
        
        # Get the new state
        observation = self._get_observation()
        
        # Check game status
        prev_score = self.current_score
        prev_lives = self.current_lives
        
        self.current_score = self.controller.get_current_score()
        self.current_lives = self.controller.get_lives()
        done = self.controller.check_game_over()
        
        # Calculate rewards
        reward = 0
        
        # Reward for scoring points
        score_reward = (self.current_score - prev_score) * 0.1
        reward += score_reward
        
        if score_reward > 0:
            self.steps_without_score = 0
        else:
            self.steps_without_score += 1
        
        # Penalty for losing lives
        if self.current_lives < prev_lives:
            reward -= 10
        
        # Penalty for game over
        if done:
            reward -= 20
        
        # Encourage shooting but not too frequently
        self.steps_since_last_shot += 1
        if action == 3 and self.steps_since_last_shot > 5:
            reward += 0.1
        
        # Small penalty for doing nothing to encourage action
        if action == 0:
            reward -= 0.01
        
        # Penalty for excessive repetition of the same action
        if self.consecutive_same_actions > 10:
            reward -= 0.05 * (self.consecutive_same_actions - 10)
        
        # Penalty for not scoring for a long time
        if self.steps_without_score > 100:
            reward -= 0.01 * (self.steps_without_score - 100) / 100
        
        # Update step counter
        self.total_steps += 1
        
        # Info dictionary for logging
        info = {
            'score': self.current_score,
            'lives': self.current_lives,
            'steps': self.total_steps
        }
        
        return observation, reward, done, False, info
    
    def reset(self, seed=None, options=None):
        """Reset the environment to start a new episode."""
        super().reset(seed=seed)
        
        # If game is over, restart it
        if not self.controller.game_active:
            self.controller.restart_game()
            time.sleep(1)  # Wait for game to initialize
        
        # Reset environment state
        self.current_score = 0
        self.current_lives = 3
        self.prev_enemies_count = 0
        self.steps_since_last_shot = 0
        self.last_action = 0
        self.consecutive_same_actions = 0
        self.steps_without_score = 0
        self.total_steps = 0
        
        # Get initial observation
        observation = self._get_observation()
        
        return observation, {}
    
    def render(self, mode='human'):
        """Render the current game state."""
        if self.current_frame is not None and mode == 'human':
            cv2.imshow('Space Invaders', self.current_frame)
            cv2.waitKey(1)
    
    def close(self):
        """Clean up resources."""
        cv2.destroyAllWindows()


class CNNFeatureExtractor(nn.Module):
    """Custom CNN feature extractor for processing game screenshots."""
    
    def __init__(self, observation_space):
        super().__init__()
        
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.Flatten()
        )
        
        # Calculate feature dimensions
        with torch.no_grad():
            n_flatten = self.cnn(torch.zeros(1, 1, 84, 84)).shape[1]
        
        self.linear = nn.Sequential(
            nn.Linear(n_flatten, 512),
            nn.ReLU()
        )
    
    def forward(self, observations):
        # Permute dimensions from [B, H, W, C] to [B, C, H, W]
        x = observations.permute(0, 3, 1, 2)
        x = x.float() / 255.0  # Normalize
        x = self.cnn(x)
        x = self.linear(x)
        return x


class CustomActorCriticPolicy(ActorCriticPolicy):
    """Custom policy using CNN feature extractor."""
    
    def __init__(
        self,
        observation_space: spaces.Space,
        action_space: spaces.Space,
        lr_schedule,
        *args,
        **kwargs
    ):
        super().__init__(
            observation_space,
            action_space,
            lr_schedule,
            *args,
            **kwargs
        )
    
    def _build_mlp_extractor(self) -> None:
        self.mlp_extractor.features_extractor = CNNFeatureExtractor(self.observation_space)


class SpaceInvadersAgent:
    """Reinforcement learning agent for playing Space Invaders."""
    
    def __init__(self, env, model_path=None):
        """Initialize the agent with environment and model."""
        self.env = env
        self.model_path = model_path
        
        # Vectorize environment (required by Stable-Baselines)
        self.vec_env = DummyVecEnv([lambda: env])
        
        # Create or load model
        if model_path and os.path.exists(model_path):
            self.model = PPO.load(model_path, env=self.vec_env)
            print(f"Loaded model from {model_path}")
        else:
            # Create new model with custom policy
            policy_kwargs = dict(
                features_extractor_class=CNNFeatureExtractor,
                features_extractor_kwargs=dict(features_dim=512),
                net_arch=dict(pi=[256, 128], vf=[256, 128])
            )
            
            self.model = PPO(
                "CnnPolicy",
                self.vec_env,
                learning_rate=0.0001,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                verbose=1,
                tensorboard_log="./logs/",
                policy_kwargs=policy_kwargs
            )
            print("Created new model")
    
    def train(self, total_timesteps=100000, save_path="models/space_invaders_ppo"):
        """Train the agent."""
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Train the model
        self.model.learn(
            total_timesteps=total_timesteps,
            progress_bar=True,
            tb_log_name="space_invaders_training",
            callback=None  # Can add callbacks for saving checkpoints
        )
        
        # Save the trained model
        self.model.save(save_path)
        print(f"Model saved to {save_path}")
        
        return self.model
    
    def play(self, episodes=5, render=True):
        """Play the game using the trained model."""
        obs, _ = self.env.reset()
        done = False
        episode = 1
        total_reward = 0
        
        while episode <= episodes:
            # Get action from model
            action, _ = self.model.predict(np.array([obs]), deterministic=True)
            
            # Take action in environment
            obs, reward, done, _, info = self.env.step(action[0])
            total_reward += reward
            
            # Render if requested
            if render:
                self.env.render()
            
            # Check if episode is done
            if done:
                print(f"Episode {episode} done. Score: {info['score']}, Lives: {info['lives']}")
                episode += 1
                total_reward = 0
                obs, _ = self.env.reset()
        
        return True
