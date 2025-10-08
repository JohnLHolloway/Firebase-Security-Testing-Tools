# Space Invaders ML Model - Refined System

An advanced reinforcement learning system designed to beat the high score on [jordancota.site](https://jordancota.site/) Space Invaders game.

## 🎯 Objective

Beat the current high score of **25,940 points** and automatically submit "John H" as the player name.

## 🏗️ System Architecture

### Core Components

1. **`stable_web_env.py`** - Robust web environment with error handling
2. **`advanced_trainer.py`** - Optimized PPO training with curriculum learning
3. **`evaluation_system.py`** - Model evaluation and high score submission
4. **`master_trainer.py`** - Complete training pipeline orchestration

### Supporting Files

- **`get_high_score.py`** - Dynamic high score detection
- **`requirements.txt`** - Python dependencies
- **`models/`** - Trained model storage

## 🚀 Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run Complete Training Pipeline

```bash
python master_trainer.py
```

This will:
1. Check and install dependencies
2. Setup Python environment
3. Train initial model
4. Run iterative training cycles until victory
5. Evaluate and submit high score

## 🛠️ Manual Usage

### Train Model

```bash
# Basic training
python advanced_trainer.py --mode train --timesteps 1000000

# Advanced training with custom parameters
python advanced_trainer.py --mode train --timesteps 5000000
```

### Evaluate Model

```bash
# Evaluate specific model
python evaluation_system.py --model models/advanced_final.zip

# Find and evaluate best model
python evaluation_system.py --evaluate-only

# Full evaluation with submission
python evaluation_system.py
```

### Test Environment

```bash
python stable_web_env.py
```

## 🔧 Key Improvements

### Stability Enhancements

- **Robust Browser Handling**: Multiple fallback methods for Chrome setup
- **Error Recovery**: Automatic retry logic for failed operations
- **Stable Actions**: Improved action execution with error handling
- **Screenshot Reliability**: Multiple methods for capturing game state

### Training Optimizations

- **Curriculum Learning**: Gradually increase episode length
- **Advanced PPO**: Optimized hyperparameters for Space Invaders
- **Custom CNN**: Specialized neural network architecture
- **Victory Detection**: Automatic stopping when high score is beaten

### Evaluation Features

- **Comprehensive Testing**: Multiple episodes with statistical analysis
- **Automatic Submission**: High score submission when target is beaten
- **Model Comparison**: Find best performing model automatically

## 📊 Training Progress

The system provides detailed progress tracking:

```
📊 Training Progress:
   Episodes: 1250
   Best Score: 18450
   Recent Avg: 15230.5
   Target: 25940
   Training Time: 2.3 hours
   Progress: 71.1%
```

## 🎮 Game Integration

- **Web-Based Training**: Trains directly on the actual game for perfect compatibility
- **Dynamic High Score**: Automatically detects current leaderboard
- **Real-Time Submission**: Submits scores immediately upon victory

## 🏆 Success Criteria

The system is successful when:
- Model achieves score ≥ 25,940 points
- Score is automatically submitted as "John H"
- Victory is confirmed on the website leaderboard

## 🔍 Troubleshooting

### Common Issues

1. **Browser Setup Fails**
   - Ensure Chrome is installed
   - Try running with `--headless false` for debugging

2. **Training Not Progressing**
   - Check internet connection for web-based training
   - Verify game elements are detected correctly
   - Try shorter episode lengths initially

3. **Submission Fails**
   - Check website structure hasn't changed
   - Verify form elements are correctly identified

### Debug Mode

Run with visible browser for debugging:

```bash
python evaluation_system.py --headless false
```

## 📈 Performance Metrics

Track these key metrics:

- **Average Score**: Should increase steadily
- **Max Score**: Peak performance achieved
- **Win Rate**: Percentage of episodes beating target
- **Training Stability**: Consistent improvement over time

## 🎯 Advanced Configuration

### Custom Training Parameters

Edit `advanced_trainer.py` to modify:

```python
# PPO Hyperparameters
learning_rate=3e-4
n_steps=2048
batch_size=64
n_epochs=10
```

### Environment Settings

Modify `stable_web_env.py` for:

```python
# Browser options
headless=True
max_retries=3
max_steps=1500
```

## 🤝 Contributing

The system is designed to be modular. Key areas for improvement:

- Enhanced computer vision for better game state detection
- Multi-agent training approaches
- Advanced reward shaping techniques
- Neural architecture search for optimal policies

## 📝 License

This project is for educational and research purposes in reinforcement learning and game AI.