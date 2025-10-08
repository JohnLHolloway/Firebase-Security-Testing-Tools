# Space Invaders ML Training

Train a reinforcement learning model to beat the high score on [jordancota.site](https://jordancota.site) Space Invaders.

**Goal:** Beat 25,940 points and submit as "John H" to the leaderboard.

## Quick Start

```bash
# Install dependencies
pip install stable-baselines3 selenium opencv-python pillow numpy beautifulsoup4 gymnasium

# Start training (10 million timesteps = ~24-48 hours)
python train_fixed.py --timesteps 10000000
```

## Files

- **[train_fixed.py](train_fixed.py)** - Main training script
- **[stable_web_env.py](stable_web_env.py)** - Gymnasium environment for the web game
- **[get_high_score.py](get_high_score.py)** - Scrapes current high score from website
- **[requirements.txt](requirements.txt)** - Python dependencies

## Training Options

```bash
# Short test run
python train_fixed.py --timesteps 100000

# Medium run (2-4 hours)
python train_fixed.py --timesteps 1000000

# Long run (24-48 hours) - Recommended
python train_fixed.py --timesteps 10000000

# Very long run (48-96 hours)
python train_fixed.py --timesteps 50000000
```

## Monitoring Training

Training creates TensorBoard logs in `./tensorboard/`:

```bash
tensorboard --logdir=./tensorboard
```

Open http://localhost:6006 to see:
- Average reward per episode
- Episode length
- Training loss/metrics

## How It Works

1. **Environment** ([stable_web_env.py](stable_web_env.py)): Controls Chrome browser, takes screenshots, executes actions
2. **Model**: PPO (Proximal Policy Optimization) from Stable-Baselines3
3. **Observations**: 84x84 grayscale screenshots of game
4. **Actions**: 6 possible (idle, left, right, shoot, left+shoot, right+shoot)
5. **Reward**: Game score delta

## Progress

Trained models are saved to `./models/` every 50,000 steps with filenames like:
```
ppo_spaceinvaders_1000000_steps.zip
```

Load a trained model:
```python
from stable_baselines3 import PPO
model = PPO.load("models/ppo_spaceinvaders_1000000_steps.zip")
```

## Current Status

- Environment bug fixed (game detection now works correctly)
- Training confirmed working (scores improving: 70 → 85 → 101 → 133+)
- Target: 25,940 points
- Strategy: Single long training run on Windows PC

## Tips

- **Be patient** - Reaching 25,940 points will take millions of timesteps
- **Watch for plateaus** - If score stops improving after 5M+ steps, may need hyperparameter tuning
- **Check progress** - Look at `ep_rew_mean` in training output to see average scores
- **Let it run** - Best results come from uninterrupted 24-48 hour training sessions

## Troubleshooting

**"ModuleNotFoundError: No module named 'stable_baselines3'"**
```bash
pip install stable-baselines3
```

**Chrome crashes or hangs**
- Training runs in headless mode by default
- If issues persist, restart training (model checkpoints are saved)

**Scores not improving**
- Make sure you're training for at least 1M timesteps
- Early training (0-500k steps) shows high variance
- Real learning happens around 1M-5M steps

## Hardware

- **CPU**: Training works on CPU (current setup)
- **GPU**: Intel Arc GPU detected but PyTorch not configured for it (optional optimization)
- **RAM**: Recommended 8GB+
- **Disk**: ~500MB for models and tensorboard logs
