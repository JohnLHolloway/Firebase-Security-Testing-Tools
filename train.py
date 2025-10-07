from stable_baselines3 import PPO
from space_invaders_env import SpaceInvadersEnv
import os

# Create environment
env = SpaceInvadersEnv()

# Create model
model = PPO(
    "CnnPolicy", 
    env, 
    verbose=1,
    learning_rate=0.0003,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.01,
    vf_coef=0.5,
    max_grad_norm=0.5,
    tensorboard_log="./tensorboard/"
)

# Train the model
model.learn(total_timesteps=500000)  # Adjust as needed

# Save the model
model.save("ppo_space_invaders")
print("Model saved as ppo_space_invaders.zip")

env.close()