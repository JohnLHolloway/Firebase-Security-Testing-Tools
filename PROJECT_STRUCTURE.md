# Project Structure

## 📁 Directory Organization

```
Space-Invaders-ML-Model/
│
├─ Core Training Files (✅ Keep)
│  ├─ stable_web_env.py          # Gymnasium environment (FIXED)
│  ├─ train_fixed.py              # Training script
│  ├─ get_high_score.py           # Leaderboard scraper
│  └─ evaluation_system.py        # Model evaluation & submission
│
├─ Distributed System (✅ Keep)
│  ├─ master_server.py            # Master orchestrator
│  ├─ worker_daemon.py            # Worker node daemon
│  ├─ test_worker.py              # Test worker (local testing)
│  └─ setup_worker.sh             # Automated RPi setup
│
├─ Documentation (✅ Keep)
│  ├─ README.md                   # Main project readme
│  ├─ QUICK_START.md              # 15-min setup guide
│  ├─ DISTRIBUTED_TRAINING_ARCHITECTURE.md  # Full architecture
│  ├─ RASPBERRY_PI_SETUP_GUIDE.md          # Detailed RPi guide
│  └─ PROJECT_STRUCTURE.md        # This file
│
├─ Alternative Trainers (⚠️ Optional - can delete)
│  ├─ advanced_trainer.py         # Advanced PPO trainer
│  ├─ master_trainer.py           # Pipeline orchestrator
│  └─ monitor_progress.py         # Progress monitor
│
├─ Generated/Build (🚫 Ignore)
│  ├─ models/                     # Trained models
│  ├─ tensorboard/                # Training logs
│  ├─ __pycache__/                # Python cache
│  └─ *.pyc                       # Compiled Python
│
└─ Config
   ├─ .gitignore                  # Git ignore rules
   ├─ requirements.txt            # Python dependencies
   └─ .claude/                    # Claude Code settings
```

## 🎯 Essential Files (Must Keep)

### Core Training (5 files)
1. `stable_web_env.py` - Environment with fixes
2. `train_fixed.py` - Main training script
3. `get_high_score.py` - Scrapes target score
4. `evaluation_system.py` - Evaluates and submits
5. `requirements.txt` - Dependencies

### Distributed System (4 files)
6. `master_server.py` - Orchestrator
7. `worker_daemon.py` - Worker node
8. `setup_worker.sh` - Setup script
9. `test_worker.py` - Local testing

### Documentation (5 files)
10. `README.md`
11. `QUICK_START.md`
12. `DISTRIBUTED_TRAINING_ARCHITECTURE.md`
13. `RASPBERRY_PI_SETUP_GUIDE.md`
14. `PROJECT_STRUCTURE.md`

**Total: 14 essential files**

## 🗑️ Can Delete (Optional)

These are alternative/experimental files:
- `advanced_trainer.py` - Similar to train_fixed.py
- `master_trainer.py` - Pipeline wrapper
- `monitor_progress.py` - Basic monitor

**Keep them if you want alternatives, delete if you want minimal setup.**

## 🚫 Auto-Generated (Git Ignored)

- `models/*.zip` - Trained models (large files)
- `tensorboard/*` - Training logs
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python

## 🎯 Usage Patterns

### For Single PC Training:
```
stable_web_env.py
train_fixed.py
get_high_score.py
evaluation_system.py
```

### For Distributed Training:
```
master_server.py (Windows PC)
worker_daemon.py (Each RPi)
stable_web_env.py (On RPis)
train_fixed.py (On RPis)
```

### For Development:
```
test_worker.py (test locally)
monitor_progress.py (watch training)
```

## 📦 Dependencies

Install once:
```bash
pip install flask requests stable-baselines3 selenium opencv-python pillow numpy beautifulsoup4
```

## 🧹 Cleanup Commands

```bash
# Remove build artifacts
rm -rf __pycache__ tensorboard *.pyc

# Remove old models (keep best ones)
cd models && ls -t | tail -n +6 | xargs rm

# Remove optional trainers (if you want minimal setup)
rm advanced_trainer.py master_trainer.py monitor_progress.py
```

## ✨ Clean Minimal Setup

If you want the absolute minimum:

**Keep only:**
1. stable_web_env.py
2. train_fixed.py
3. get_high_score.py
4. evaluation_system.py
5. master_server.py
6. worker_daemon.py
7. requirements.txt
8. README.md
9. QUICK_START.md

**Delete everything else** (except .gitignore)

This gives you a clean, 9-file distributed training system!
