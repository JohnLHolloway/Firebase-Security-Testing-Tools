#!/bin/bash
# Automated Raspberry Pi Worker Setup Script
# Run this on each RPi to setup worker daemon

set -e  # Exit on error

echo "======================================================================"
echo "🤖 Space Invaders ML - Worker Setup"
echo "======================================================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo "❌ Please don't run as root. Run as regular user (pi)."
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
sudo apt install -y \
    git \
    python3-pip \
    python3-venv \
    chromium-browser \
    chromium-chromedriver \
    python3-dev \
    libatlas-base-dev \
    libopenblas-dev \
    screen

# Create project directory
PROJECT_DIR="$HOME/ml-training"
echo "📁 Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python packages
echo "📦 Installing Python packages (this may take a while on RPi)..."
pip install flask requests

# Download worker daemon
echo "📥 Downloading worker daemon..."
# If you have GitHub repo:
# git clone https://github.com/yourusername/Space-Invaders-ML-Model.git .

# For now, assuming files will be copied manually or via SCP
echo "⚠️  Please copy these files to $PROJECT_DIR:"
echo "   - worker_daemon.py"
echo "   - stable_web_env.py"
echo "   - train_fixed.py"
echo "   - get_high_score.py"
echo "   - requirements.txt"

# Create systemd service for auto-start
echo "🔧 Creating systemd service..."
SERVICE_FILE="$HOME/.config/systemd/user/ml-worker.service"
mkdir -p "$HOME/.config/systemd/user"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=ML Training Worker
After=network.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/worker_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

# Enable user lingering (allows service to run without login)
sudo loginctl enable-linger $USER

# Reload systemd
systemctl --user daemon-reload

echo ""
echo "======================================================================"
echo "✅ Worker setup complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "1. Copy project files to: $PROJECT_DIR"
echo "2. Install additional Python packages:"
echo "   cd $PROJECT_DIR"
echo "   source venv/bin/activate"
echo "   pip install stable-baselines3 selenium opencv-python pillow numpy"
echo ""
echo "3. Start worker manually (for testing):"
echo "   cd $PROJECT_DIR"
echo "   source venv/bin/activate"
echo "   python worker_daemon.py"
echo ""
echo "4. Or enable auto-start service:"
echo "   systemctl --user enable ml-worker"
echo "   systemctl --user start ml-worker"
echo ""
echo "5. Check service status:"
echo "   systemctl --user status ml-worker"
echo ""
echo "======================================================================"
