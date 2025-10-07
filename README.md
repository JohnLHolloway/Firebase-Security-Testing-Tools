# Space-Invaders-ML-Model

# 🌐 Web-Based Space Invaders ML

**Train an AI directly on https://jordancota.site/ for perfect compatibility**

## 🎯 Mission

Beat the current high score of **25,940 points** and submit as **"John H"**

## 🚀 Fresh Start - Web-First Approach

This is a completely rebuilt system that trains directly on the actual website, eliminating compatibility issues.

## 🎮 Quick Start

```bash
# 1. Install dependencies
py -m pip install -r requirements.txt

# 2. Start web training
py web_train.py

# 3. Submit high scores
py web_submit.py
```

## 📁 Clean Architecture

### Core System
- **`web_env.py`** - 🌐 Direct web game environment (jordancota.site)
- **`web_train.py`** - 🤖 PPO training on actual website
- **`web_submit.py`** - 🏆 High score submission with "John H"

### Legacy (Reference Only)
- `main.py` - Original evaluation script

## ✨ Why Web-First Works Better

1. **� Perfect Compatibility** - Trains on the actual game, not a replica
2. **🌐 Real Environment** - No translation between local and web
3. **📊 Direct Feedback** - Immediate score and game over detection
4. **🏆 Seamless Submission** - Automatic high score submission

## 🎮 Training Process

1. **Browser Automation** - Opens jordancota.site automatically
2. **Game Detection** - Finds canvas and start button
3. **Visual Learning** - CNN processes game screenshots (84x84 RGB)
4. **Action Execution** - Arrow keys + spacebar controls
5. **Score Monitoring** - Real-time score tracking and progress

## 🤖 Model Details

- **Algorithm**: PPO (Proximal Policy Optimization)
- **Policy**: CNN for visual input processing
- **Actions**: Left, Right, Shoot, No-op
- **Observations**: 84x84x3 RGB game screenshots
- **Reward**: Score increases + survival bonus

## 🏆 High Score System

When the AI achieves > 25,940 points:
1. ✅ **Automatic detection** of high score
2. 🎯 **Auto-submission** with name "John H"  
3. 🏆 **Leaderboard update** on jordancota.site
4. 🎉 **Mission accomplished!**

## 📊 Training Options

- **Quick Training**: 100K steps (~2-3 hours)
- **Extended Training**: 500K steps (~10-12 hours)
- **Custom Training**: Set your own timesteps

## 🔧 Usage

### Start Training
```bash
py web_train.py
# Choose option 1 for quick training
# Choose option 2 for extended training
```

### Test Environment
```bash
py web_train.py
# Choose option 4 to test web connection
```

### Submit High Score
```bash
py web_submit.py
# Automatically plays and submits if high score achieved
```

## 🎯 Goal

Train until AI consistently beats 25,940 points, then automatically submit "John H" to the leaderboard!

---

**🌐 Pure web training = Perfect compatibility = High score success!**

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