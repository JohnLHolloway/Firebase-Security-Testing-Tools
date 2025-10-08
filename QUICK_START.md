## Quick Start Guide: Distributed Training Cluster

### Prerequisites
- Windows PC (Master)
- 1+ Raspberry Pi 5 (Workers)
- All devices on same local network

---

## Step 1: Setup Master (Windows PC) - 5 minutes

```bash
# Install Flask
pip install flask

# Start master server
cd "c:\Users\jlhol\OneDrive\Desktop\Space-Invaders-ML-Model"
python master_server.py
```

**Master is now running!** Open browser: http://localhost:5000

---

## Step 2: Setup Workers (Raspberry Pi) - 10 minutes each

### Method A: Automated Setup (Recommended)

```bash
# On RPi, copy setup script and run:
chmod +x setup_worker.sh
./setup_worker.sh

# Then copy project files:
scp -r stable_web_env.py worker_daemon.py train_fixed.py get_high_score.py pi@raspberrypi.local:~/ml-training/

# Install ML packages:
cd ~/ml-training
source venv/bin/activate
pip install stable-baselines3 selenium opencv-python pillow numpy requests beautifulsoup4

# Start worker:
python worker_daemon.py
```

### Method B: Manual Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install deps
sudo apt install -y git python3-pip chromium-browser chromium-chromedriver

# Create project
mkdir -p ~/ml-training
cd ~/ml-training

# Copy files from Windows:
# (On Windows): scp -r *.py pi@192.168.1.xxx:~/ml-training/

# Install Python packages
pip3 install flask requests stable-baselines3 selenium opencv-python pillow numpy

# Run worker
python3 worker_daemon.py
```

---

## Step 3: Monitor Training

**Web Dashboard**: http://your-pc-ip:5000

You'll see:
- All connected workers
- Job queue
- Completed jobs with scores

---

## Usage Examples

### Start Master with Jobs

```python
# Edit master_server.py - create_jobs() function
# Add your custom training configurations
jobs = [
    {"job_id": "exp_lr_high", "config": {"learning_rate": 0.001, "timesteps": 100000}},
    {"job_id": "exp_lr_low", "config": {"learning_rate": 0.0001, "timesteps": 100000}},
]
```

### Add Jobs Dynamically

Visit: http://localhost:5000 and click "Create Test Jobs"

Or via API:
```bash
curl -X POST http://localhost:5000/create_test_jobs
```

### Check Status (CLI)

```bash
curl http://localhost:5000/status | python -m json.tool
```

---

## Troubleshooting

### Master can't find workers
```bash
# On RPi, specify master IP manually:
python worker_daemon.py --master 192.168.1.100
```

### Worker can't reach master
- Check firewall on Windows (allow port 5000)
- Verify both on same network
- Ping test: `ping master-ip-address`

### Training fails
- Check logs on worker
- Verify all Python packages installed
- Test train_fixed.py manually first

---

## File Transfer Between PC and RPi

### Copy TO RPi:
```bash
scp stable_web_env.py worker_daemon.py train_fixed.py pi@192.168.1.xxx:~/ml-training/
```

### Copy FROM RPi (trained models):
```bash
scp pi@192.168.1.xxx:~/ml-training/models/*.zip ./models/
```

---

## Architecture at a Glance

```
Windows PC (Master)
    ↓ (discovers workers)
    ├── RPi #1 → trains model A
    ├── RPi #2 → trains model B
    └── RPi #3 → trains model C
    ↑ (reports results)
Windows PC collects all models
```

---

## What Gets Trained?

Each worker trains with different hyperparameters:
- Different learning rates
- Different batch sizes
- Different network architectures

Master collects results and you pick the best model!

---

## Next Steps

1. Let workers train for 1-2 days
2. Check dashboard for best scores
3. Download best models
4. Evaluate on actual game
5. Submit high score!
