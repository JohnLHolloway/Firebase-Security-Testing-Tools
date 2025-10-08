#!/bin/bash
# Deploy security testing worker to Raspberry Pi

echo "========================================="
echo "Security Worker Deployment Script"
echo "========================================="
echo ""

# Configuration
RPI_USER="pi"
RPI_HOST="192.168.1.194"  # Change this to your RPi IP
REMOTE_DIR="/home/$RPI_USER/security-testing"

echo "Target: $RPI_USER@$RPI_HOST"
echo "Remote directory: $REMOTE_DIR"
echo ""

# Create remote directory
echo "Creating remote directory..."
ssh $RPI_USER@$RPI_HOST "mkdir -p $REMOTE_DIR"

# Copy security worker
echo "Copying security_worker.py..."
scp security_worker.py $RPI_USER@$RPI_HOST:$REMOTE_DIR/

# Create systemd service for auto-start
echo "Creating systemd service..."
ssh $RPI_USER@$RPI_HOST "cat > $REMOTE_DIR/security-worker.service << 'EOF'
[Unit]
Description=Security Testing Worker
After=network.target

[Service]
Type=simple
User=$RPI_USER
WorkingDirectory=$REMOTE_DIR
ExecStart=/usr/bin/python3 $REMOTE_DIR/security_worker.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF"

# Install and start service
echo "Installing service..."
ssh $RPI_USER@$RPI_HOST "sudo cp $REMOTE_DIR/security-worker.service /etc/systemd/system/ && \
    sudo systemctl daemon-reload && \
    sudo systemctl enable security-worker.service && \
    sudo systemctl start security-worker.service"

echo ""
echo "========================================="
echo "Deployment complete!"
echo "========================================="
echo ""
echo "To check status:"
echo "  ssh $RPI_USER@$RPI_HOST 'sudo systemctl status security-worker'"
echo ""
echo "To view logs:"
echo "  ssh $RPI_USER@$RPI_HOST 'sudo journalctl -u security-worker -f'"
echo ""
echo "To stop worker:"
echo "  ssh $RPI_USER@$RPI_HOST 'sudo systemctl stop security-worker'"
echo ""
