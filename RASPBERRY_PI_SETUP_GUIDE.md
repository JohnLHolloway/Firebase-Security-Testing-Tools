# Raspberry Pi 5 Setup Guide for Space Invaders ML Training

## Why Raspberry Pi 5 is Perfect for This Project

✅ **Always-on training**: Run 24/7 without keeping your main PC on
✅ **Low power**: ~15W vs 300W+ for desktop
✅ **Sufficient performance**: 4-core ARM CPU is adequate for this task
✅ **Headless ready**: Built for background tasks
✅ **Cost effective**: Dedicated ML training machine

---

## Complete Setup Plan

### Phase 1: Hardware & OS Setup (30 minutes)

#### What You Need:
- Raspberry Pi 5 (4GB or 8GB RAM recommended)
- MicroSD card (32GB+ recommended, Class 10/U3)
- Power supply (27W official RPi 5 power supply)
- Ethernet cable (recommended for stability) or WiFi
- (Optional) Cooling case/fan for extended training

#### Step 1: Install Operating System
1. Download **Raspberry Pi Imager**: https://www.raspberrypi.com/software/
2. Insert SD card into your PC
3. Open Raspberry Pi Imager
4. Choose:
   - **OS**: "Raspberry Pi OS (64-bit)" - Desktop version recommended
   - **Storage**: Your SD card
5. Click gear icon (⚙️) for advanced options:
   - Set hostname: `spaceinvaders-ml`
   - Enable SSH (password or key authentication)
   - Set username: `pi` (or your choice)
   - Set password
   - Configure WiFi if not using ethernet
6. Write to SD card
7. Insert SD card into Pi and boot

#### Step 2: Initial Pi Setup
```bash
# SSH into Pi (from your Windows PC)
ssh pi@spaceinvaders-ml.local
# Or use IP address: ssh pi@192.168.1.xxx

# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git vim htop python3-pip python3-venv

# Reboot
sudo reboot
```

---

### Phase 2: Install Chrome & Dependencies (20 minutes)

```bash
# Install Chromium browser (optimized for ARM)
sudo apt install -y chromium-browser chromium-chromedriver

# Verify installation
chromium-browser --version
chromedriver --version

# Install system dependencies for ML libraries
sudo apt install -y \
    python3-dev \
    libatlas-base-dev \
    libopenblas-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    libqt5gui5 \
    libqt5widgets5 \
    libqt5test5 \
    libilmbase-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libwebp-dev \
    libopencv-dev

# Install screen (for persistent sessions)
sudo apt install -y screen
```

---

### Phase 3: Transfer & Setup Project (15 minutes)

#### Option A: Git Clone (Recommended if you have GitHub)
```bash
# Create project directory
mkdir -p ~/projects
cd ~/projects

# Clone your repository
git clone https://github.com/yourusername/Space-Invaders-ML-Model.git
cd Space-Invaders-ML-Model
```

#### Option B: SCP Transfer from Windows (If no GitHub)
```bash
# On Windows (PowerShell or CMD), from project directory:
scp -r "c:\Users\jlhol\OneDrive\Desktop\Space-Invaders-ML-Model" pi@spaceinvaders-ml.local:~/projects/

# Then SSH into Pi
ssh pi@spaceinvaders-ml.local
cd ~/projects/Space-Invaders-ML-Model
```

---

### Phase 4: Setup Python Environment (30 minutes)

```bash
cd ~/projects/Space-Invaders-ML-Model

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install PyTorch (ARM-optimized version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
pip install gymnasium stable-baselines3 selenium opencv-python pillow numpy requests beautifulsoup4

# Install webdriver manager
pip install webdriver-manager
```

**Note**: Installing on ARM can take 30-60 minutes due to compiling some packages.

---

### Phase 5: Configure Environment for RPi (10 minutes)

#### Create RPi-specific configuration file:

```bash
nano rpi_config.py
```

```python
"""
Raspberry Pi Specific Configuration
"""

# Use Chromium instead of Chrome
CHROME_BINARY = "/usr/bin/chromium-browser"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"

# Optimize for RPi
HEADLESS = True  # Always headless on Pi
MAX_STEPS_PER_EPISODE = 1000  # Reduce for faster iterations
TRAINING_BATCH_SIZE = 32  # Smaller batches for limited RAM
```

#### Update stable_web_env.py for RPi:

```bash
nano stable_web_env.py
```

Add at the beginning (after imports):
```python
import os
import platform

# Detect if running on Raspberry Pi
IS_RPI = platform.machine().startswith('arm') or platform.machine().startswith('aarch')

if IS_RPI:
    # Use Chromium on Raspberry Pi
    CHROME_BINARY = "/usr/bin/chromium-browser"
else:
    CHROME_BINARY = None  # Auto-detect on other systems
```

Then in the `setup_browser()` method, update the chrome paths section:
```python
# Around line 80-82, replace:
if IS_RPI:
    options.binary_location = CHROME_BINARY
else:
    # Try different Chrome paths (existing code)
    chrome_paths = [...]
```

---

### Phase 6: Test the Setup (10 minutes)

```bash
# Activate environment
cd ~/projects/Space-Invaders-ML-Model
source venv/bin/activate

# Test environment
python3 -c "
from stable_web_env import StableWebSpaceInvadersEnv
print('Creating environment...')
env = StableWebSpaceInvadersEnv(headless=True)
obs, _ = env.reset()
print(f'Success! Observation shape: {obs.shape}')
env.close()
"
```

---

### Phase 7: Start Training (Persistent Session)

```bash
# Start a screen session (survives SSH disconnects)
screen -S training

# Activate environment
cd ~/projects/Space-Invaders-ML-Model
source venv/bin/activate

# Start training
python3 train_fixed.py --timesteps 500000

# Detach from screen: Press Ctrl+A, then D
# Reattach anytime: screen -r training
# Close SSH without stopping: Just exit
```

---

## Monitoring Training Remotely

### Option 1: SSH and Check Progress
```bash
# From Windows
ssh pi@spaceinvaders-ml.local

# Reattach to training session
screen -r training

# Or check saved models
ls -lh ~/projects/Space-Invaders-ML-Model/models/
```

### Option 2: TensorBoard (Advanced)
```bash
# On Pi, in a new screen session
screen -S tensorboard
cd ~/projects/Space-Invaders-ML-Model
source venv/bin/activate
tensorboard --logdir=./tensorboard/ --host=0.0.0.0 --port=6006

# Detach: Ctrl+A, D

# On Windows browser, visit:
# http://spaceinvaders-ml.local:6006
```

### Option 3: Auto-Status Reports (Recommended)

Create a monitoring script that emails/texts you progress:

```bash
nano monitor_and_report.py
```

```python
"""Monitor training and send status updates"""
import time
import os
from datetime import datetime

def check_progress():
    models_dir = "./models"
    if not os.path.exists(models_dir):
        return "No models yet"

    models = [f for f in os.listdir(models_dir) if f.endswith('.zip')]
    if not models:
        return "No models saved yet"

    latest = max(models, key=lambda f: os.path.getmtime(os.path.join(models_dir, f)))
    size = os.path.getsize(os.path.join(models_dir, latest))

    return f"Latest: {latest}, Size: {size/1024/1024:.1f}MB"

# Check every hour
while True:
    status = check_progress()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}")

    # Could add email/SMS here

    time.sleep(3600)  # 1 hour
```

Run in another screen:
```bash
screen -S monitor
python3 monitor_and_report.py
# Ctrl+A, D to detach
```

---

## Performance Expectations on RPi 5

### Training Speed:
- **RPi 5**: ~0.5-2 FPS (faster than Windows web automation!)
- **Reason**: Optimized Linux chromium + dedicated resources
- **100K steps**: ~14-56 hours
- **500K steps**: ~3-12 days

### Benefits vs Windows PC:
✅ Runs 24/7 without interruption
✅ Lower power consumption
✅ No impact on your main work computer
✅ More stable (Linux + dedicated hardware)
✅ Can run multiple experiments

---

## Optimization Tips for RPi

### 1. Enable Swap (for 4GB Pi)
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### 2. Overclock (Optional - adds ~10% speed)
```bash
sudo nano /boot/firmware/config.txt
# Add at end:
over_voltage=2
arm_freq=2400
```

### 3. Cooling
- Use a fan or heatsink case
- Monitor temp: `vcgencmd measure_temp`
- Should stay under 75°C during training

### 4. Use SSD instead of SD Card (Optional)
- Much faster I/O
- More reliable for 24/7 operation
- Connect via USB 3.0

---

## Transferring Trained Models Back to Windows

### Option 1: SCP
```bash
# On Windows
scp pi@spaceinvaders-ml.local:~/projects/Space-Invaders-ML-Model/models/*.zip ./models/
```

### Option 2: Git
```bash
# On Pi
cd ~/projects/Space-Invaders-ML-Model
git add models/
git commit -m "Trained model checkpoint"
git push

# On Windows
git pull
```

### Option 3: Shared Network Folder
- Setup Samba share on Pi
- Mount on Windows
- Direct access to files

---

## Troubleshooting

### Issue: Chrome/Chromium crashes
```bash
# Increase memory split
sudo raspi-config
# Advanced Options > Memory Split > Set to 256

# Or use lighter browser settings
export CHROMIUM_FLAGS="--disable-gpu --no-sandbox"
```

### Issue: Out of memory
```bash
# Check memory
free -h

# Reduce batch size in training
# Edit train_fixed.py: batch_size=16 (instead of 32)
```

### Issue: Training too slow
```bash
# Reduce observation size in stable_web_env.py
# Change from 84x84 to 64x64
```

### Issue: Can't connect to Pi
```bash
# Find Pi's IP
# On Pi: hostname -I
# On Windows: ping spaceinvaders-ml.local
```

---

## Complete Deployment Checklist

- [ ] Flash SD card with Raspberry Pi OS 64-bit
- [ ] Boot Pi and complete initial setup
- [ ] Update system packages
- [ ] Install Chromium and ChromeDriver
- [ ] Install system dependencies
- [ ] Transfer project files
- [ ] Create Python virtual environment
- [ ] Install Python packages
- [ ] Configure environment for RPi
- [ ] Test environment works
- [ ] Start training in screen session
- [ ] Setup monitoring
- [ ] Verify remote access works
- [ ] Let it run 24/7!

---

## Estimated Total Setup Time: 2-3 hours

(Plus training time: days to weeks depending on parameters)

---

## Next Steps After Training

1. Monitor progress daily via SSH or TensorBoard
2. When best score plateau is reached (~3-7 days):
   - Transfer model back to Windows
   - Run evaluation with visible browser
   - Submit high score if target beaten
3. Iterate with better hyperparameters if needed

---

## Cost Breakdown

- Raspberry Pi 5 (8GB): $80
- Power supply: $12
- SD card (64GB): $15
- Case with fan: $15
- **Total**: ~$122

**Electricity**: ~$0.05/day = ~$1.50/month for 24/7 operation

**vs Leaving Windows PC on**: ~300W = ~$20/month

**Savings**: ~$18/month + freedom to use your main PC!

---

## Questions?

This setup gives you a dedicated, always-on ML training rig for this and future projects!
