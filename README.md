# Space-Invaders-ML-Model

This project trains a reinforcement learning model to play the Space Invaders game on https://jordancota.site/. The model uses Proximal Policy Optimization (PPO) with a convolutional neural network to process game screenshots and make decisions.

## Features
- Optimizes for high score and survival (3 lives)
- Reads current high score from the site
- Prompts for name if high score is beaten
- Uses advanced RL techniques with Stable Baselines3 and PyTorch

## Setup
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Train the model:
   ```
   python train.py
   ```

3. Test the model:
   ```
   python test.py
   ```

## Notes
- The environment uses Selenium to interact with the web game.
- Element IDs (score, lives, etc.) may need adjustment based on the actual site structure.
- Training may take time; adjust timesteps as needed.
- For better performance, consider frame stacking or reward shaping.