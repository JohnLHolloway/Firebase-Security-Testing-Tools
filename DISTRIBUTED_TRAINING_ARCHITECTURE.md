# Distributed ML Training Cluster Architecture

## Overview: Master-Worker Architecture

Instead of manually managing each Pi, create a **distributed training system** where:
- **Master (Windows PC)**: Orchestrates training, manages configs, collects results
- **Workers (RPis)**: Execute training jobs, report back results
- **Auto-discovery**: Automatically find and use available Pis on network
- **Parallel training**: Run multiple experiments simultaneously

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    WINDOWS PC (Master)                   │
│  ┌────────────────────────────────────────────────────┐ │
│  │  • Job Manager (distributes training jobs)         │ │
│  │  • Network Scanner (discovers Pis)                 │ │
│  │  • Results Aggregator (collects models/metrics)   │ │
│  │  │  GitHub/Git sync                               │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────┬───────────────────┬──────────────────┘
                   │                   │
      ┌────────────┴──────┬───────────┴──────┬
      │                   │                  │
┌─────▼──────┐   ┌───────▼────────┐  ┌─────▼──────┐
│   RPi #1   │   │    RPi #2      │  │  RPi #3    │
│  Worker    │   │   Worker       │  │  Worker    │
│            │   │                │  │            │
│ Training   │   │  Training      │  │ Training   │
│ Job A      │   │  Job B         │  │  Job C     │
│ LR=0.001   │   │  LR=0.0005     │  │ LR=0.0001  │
└────────────┘   └────────────────┘  └────────────┘
      │                   │                  │
      └────────────┬──────┴──────────────────┘
                   │
      ┌────────────▼─────────────┐
      │   GitHub Repository      │
      │   • Trained models       │
      │   • Training metrics     │
      │   • Logs                 │
      └──────────────────────────┘
```

---

## System Components

### 1. Master Node (Windows PC)

**Responsibilities:**
- Discover available RPi workers on local network
- Distribute training configurations
- Monitor worker health/progress
- Collect and aggregate results
- Manage Git synchronization

**Runs:**
- Job orchestration server
- Network scanner
- Web dashboard for monitoring

### 2. Worker Nodes (Raspberry Pis)

**Responsibilities:**
- Register with master on boot
- Pull training jobs from master
- Execute training
- Push results to Git/Master
- Report status/metrics

**Runs:**
- Lightweight worker daemon
- Training environment
- Auto-update from Git

---

## Implementation Plan

### Phase 1: Network Discovery & Communication

Create a simple REST API + auto-discovery system:

#### A. Master Server (`master_server.py`)

```python
"""
Master Training Orchestrator
Runs on Windows PC
"""
from flask import Flask, request, jsonify
import socket
import threading
import json
from datetime import datetime
import subprocess

app = Flask(__name__)

# Track available workers
workers = {}  # {ip: {hostname, last_seen, status, current_job}}
job_queue = []
completed_jobs = []

class WorkerDiscovery:
    """Auto-discover RPis on local network"""

    def __init__(self, port=5000):
        self.port = port

    def scan_network(self):
        """Scan local network for workers"""
        import ipaddress
        import concurrent.futures

        # Get local network range
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)

        print(f"Scanning network: {network}")
        active_workers = []

        def check_host(ip):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((str(ip), self.port))
                sock.close()
                if result == 0:
                    return str(ip)
            except:
                pass
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(check_host, network.hosts())
            active_workers = [ip for ip in results if ip]

        return active_workers

    def broadcast_discovery(self):
        """Alternative: Broadcast UDP to find workers"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)

        # Broadcast discovery message
        message = json.dumps({"type": "discover", "master": True}).encode()
        sock.sendto(message, ('<broadcast>', 5001))

        responses = []
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                response = json.loads(data.decode())
                if response.get("type") == "worker":
                    responses.append({
                        "ip": addr[0],
                        "hostname": response.get("hostname"),
                        "capabilities": response.get("capabilities")
                    })
        except socket.timeout:
            pass

        sock.close()
        return responses

@app.route('/register', methods=['POST'])
def register_worker():
    """Worker registration endpoint"""
    data = request.json
    worker_ip = request.remote_addr

    workers[worker_ip] = {
        "hostname": data.get("hostname"),
        "capabilities": data.get("capabilities"),
        "last_seen": datetime.now().isoformat(),
        "status": "idle",
        "current_job": None
    }

    print(f"✅ Worker registered: {data.get('hostname')} ({worker_ip})")
    return jsonify({"status": "registered", "worker_id": worker_ip})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """Worker heartbeat"""
    worker_ip = request.remote_addr
    if worker_ip in workers:
        workers[worker_ip]["last_seen"] = datetime.now().isoformat()
        workers[worker_ip]["status"] = request.json.get("status", "idle")
        return jsonify({"status": "ok"})
    return jsonify({"status": "unknown_worker"}), 404

@app.route('/get_job', methods=['GET'])
def get_job():
    """Assign job to requesting worker"""
    worker_ip = request.remote_addr

    if job_queue:
        job = job_queue.pop(0)
        workers[worker_ip]["current_job"] = job["job_id"]
        workers[worker_ip]["status"] = "training"

        print(f"📤 Assigned job {job['job_id']} to {worker_ip}")
        return jsonify(job)

    return jsonify({"status": "no_jobs"}), 204

@app.route('/report_result', methods=['POST'])
def report_result():
    """Worker reports training results"""
    data = request.json
    worker_ip = request.remote_addr

    completed_jobs.append({
        "worker": worker_ip,
        "job_id": data.get("job_id"),
        "metrics": data.get("metrics"),
        "model_path": data.get("model_path"),
        "timestamp": datetime.now().isoformat()
    })

    workers[worker_ip]["status"] = "idle"
    workers[worker_ip]["current_job"] = None

    print(f"✅ Job {data.get('job_id')} completed by {worker_ip}")
    print(f"   Best score: {data.get('metrics', {}).get('best_score', 'N/A')}")

    return jsonify({"status": "recorded"})

@app.route('/status', methods=['GET'])
def status():
    """Get cluster status"""
    return jsonify({
        "workers": workers,
        "jobs_pending": len(job_queue),
        "jobs_completed": len(completed_jobs)
    })

def create_jobs():
    """Create training jobs with different hyperparameters"""
    jobs = [
        {
            "job_id": "job_001",
            "config": {
                "learning_rate": 0.001,
                "batch_size": 32,
                "timesteps": 100000,
                "description": "High learning rate"
            }
        },
        {
            "job_id": "job_002",
            "config": {
                "learning_rate": 0.0005,
                "batch_size": 32,
                "timesteps": 100000,
                "description": "Medium learning rate"
            }
        },
        {
            "job_id": "job_003",
            "config": {
                "learning_rate": 0.0001,
                "batch_size": 64,
                "timesteps": 100000,
                "description": "Low learning rate, larger batch"
            }
        }
    ]
    return jobs

def start_master():
    """Start master server"""
    print("="*60)
    print("🎮 SPACE INVADERS ML - DISTRIBUTED TRAINING MASTER")
    print("="*60)

    # Discover workers
    print("\n🔍 Discovering workers on network...")
    discovery = WorkerDiscovery()

    # Try broadcast discovery first
    found_workers = discovery.broadcast_discovery()
    if found_workers:
        print(f"✅ Found {len(found_workers)} workers via broadcast:")
        for w in found_workers:
            print(f"   • {w['hostname']} ({w['ip']})")
    else:
        print("⚠️  No workers responded to broadcast")
        print("   Workers will register when they start")

    # Create job queue
    global job_queue
    job_queue = create_jobs()
    print(f"\n📋 Created {len(job_queue)} training jobs")

    # Start server
    print(f"\n🚀 Master server starting on port 5000")
    print(f"   Dashboard: http://localhost:5000/status")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    start_master()
```

#### B. Worker Daemon (`worker_daemon.py`)

```python
"""
Training Worker Daemon
Runs on Raspberry Pi
"""
import requests
import socket
import json
import time
import subprocess
import os
from datetime import datetime
import threading

class TrainingWorker:
    def __init__(self, master_ip=None):
        self.master_ip = master_ip or self.discover_master()
        self.hostname = socket.gethostname()
        self.worker_id = None
        self.running = True

    def discover_master(self):
        """Listen for master broadcast"""
        print("🔍 Looking for master node...")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 5001))
        sock.settimeout(5)

        try:
            while True:
                data, addr = sock.recvfrom(1024)
                message = json.loads(data.decode())

                if message.get("type") == "discover" and message.get("master"):
                    # Respond to master
                    response = json.dumps({
                        "type": "worker",
                        "hostname": self.hostname,
                        "capabilities": {
                            "cpu_cores": os.cpu_count(),
                            "platform": "rpi5"
                        }
                    }).encode()

                    sock.sendto(response, addr)
                    sock.close()

                    print(f"✅ Found master at {addr[0]}")
                    return addr[0]
        except socket.timeout:
            sock.close()
            print("❌ No master found. Please provide master IP manually.")
            return None

    def register(self):
        """Register with master"""
        if not self.master_ip:
            return False

        url = f"http://{self.master_ip}:5000/register"
        data = {
            "hostname": self.hostname,
            "capabilities": {
                "cpu_cores": os.cpu_count(),
                "ram": "8GB",  # Could detect this
                "platform": "rpi5"
            }
        }

        try:
            response = requests.post(url, json=data, timeout=5)
            if response.status_code == 200:
                self.worker_id = response.json().get("worker_id")
                print(f"✅ Registered with master as {self.worker_id}")
                return True
        except Exception as e:
            print(f"❌ Registration failed: {e}")

        return False

    def send_heartbeat(self):
        """Send periodic heartbeat"""
        while self.running:
            try:
                url = f"http://{self.master_ip}:5000/heartbeat"
                requests.post(url, json={"status": "idle"}, timeout=2)
            except:
                pass
            time.sleep(30)  # Every 30 seconds

    def get_job(self):
        """Request a training job"""
        try:
            url = f"http://{self.master_ip}:5000/get_job"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting job: {e}")

        return None

    def execute_job(self, job):
        """Execute training job"""
        job_id = job.get("job_id")
        config = job.get("config")

        print(f"\n{'='*60}")
        print(f"🎮 Starting job: {job_id}")
        print(f"   {config.get('description')}")
        print(f"   Learning rate: {config.get('learning_rate')}")
        print(f"   Batch size: {config.get('batch_size')}")
        print(f"   Timesteps: {config.get('timesteps')}")
        print(f"{'='*60}\n")

        # Execute training
        cmd = [
            "python3", "train_fixed.py",
            "--timesteps", str(config.get("timesteps")),
            "--learning-rate", str(config.get("learning_rate")),
            "--batch-size", str(config.get("batch_size"))
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Find best model
            models_dir = "./models"
            models = [f for f in os.listdir(models_dir) if f.endswith('.zip')]
            latest_model = max(models, key=lambda f: os.path.getmtime(os.path.join(models_dir, f)))

            return {
                "success": True,
                "model_path": os.path.join(models_dir, latest_model),
                "job_id": job_id
            }
        except Exception as e:
            print(f"❌ Job failed: {e}")
            return {"success": False, "error": str(e)}

    def report_result(self, job_id, result):
        """Report job completion to master"""
        try:
            url = f"http://{self.master_ip}:5000/report_result"
            data = {
                "job_id": job_id,
                "metrics": result.get("metrics", {}),
                "model_path": result.get("model_path"),
                "success": result.get("success")
            }

            requests.post(url, json=data, timeout=10)
            print(f"✅ Reported results for {job_id}")
        except Exception as e:
            print(f"❌ Failed to report results: {e}")

    def run(self):
        """Main worker loop"""
        print("="*60)
        print(f"🤖 TRAINING WORKER: {self.hostname}")
        print("="*60)

        # Register with master
        if not self.register():
            print("❌ Could not register with master. Exiting.")
            return

        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self.send_heartbeat, daemon=True)
        heartbeat_thread.start()

        print("\n✅ Worker ready. Waiting for jobs...\n")

        # Main job loop
        while self.running:
            job = self.get_job()

            if job:
                result = self.execute_job(job)
                self.report_result(job["job_id"], result)

                # TODO: Git push model
            else:
                # No jobs available, wait
                time.sleep(30)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=str, help="Master node IP address")
    args = parser.parse_args()

    worker = TrainingWorker(master_ip=args.master)
    worker.run()
```

---

### Phase 2: Simplified RPi Setup

With this architecture, RPi setup is MUCH simpler:

```bash
# 1. Flash OS (same as before)

# 2. Install minimal dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-pip chromium-browser chromium-chromedriver

# 3. Clone ONLY worker code (small repo)
git clone https://github.com/yourusername/ml-training-worker.git
cd ml-training-worker

# 4. Install minimal packages
pip3 install requests flask

# 5. Start worker daemon (runs forever)
python3 worker_daemon.py --master 192.168.1.100

# Or auto-discover:
python3 worker_daemon.py
```

**That's it!** The worker pulls everything else it needs from the master.

---

### Phase 3: Git Integration

Workers automatically push results:

```python
def push_model_to_git(model_path, job_id):
    """Push trained model to Git"""
    import subprocess

    # Commit and push
    commands = [
        f"git add {model_path}",
        f"git commit -m 'Model from {job_id} - {datetime.now()}'",
        "git push origin main"
    ]

    for cmd in commands:
        subprocess.run(cmd, shell=True)
```

---

## Advantages of This Architecture

### ✅ Scalability
- Add more RPis → automatically discovered and utilized
- No manual configuration per Pi
- True parallel training (3 Pis = 3x experiments simultaneously)

### ✅ Efficiency
- Hyperparameter sweep in parallel
- Try different learning rates, batch sizes, etc. at once
- Best model found faster

### ✅ Simplicity
- Master PC stays in control
- RPis are "dumb workers" (easy to setup/replace)
- Single source of truth (Git)

### ✅ Monitoring
- Centralized dashboard
- See all workers at once
- Track progress across experiments

### ✅ Fault Tolerance
- Worker crash? Master reassigns job
- Master sees which workers are alive via heartbeat
- Failed jobs can be retried

---

## Deployment Steps

### Step 1: Setup Master (Windows PC)

```bash
# Install Flask
pip install flask requests

# Run master server
python master_server.py
```

### Step 2: Setup Each Worker (RPi)

```bash
# Flash OS
# Boot Pi
# Run one-liner:
curl https://raw.githubusercontent.com/yourusername/repo/main/setup_worker.sh | bash

# Worker auto-discovers master and starts working!
```

### Step 3: Define Training Experiments

Edit `master_server.py` to create jobs:

```python
jobs = [
    {"job_id": "exp_001", "config": {"learning_rate": 0.001, ...}},
    {"job_id": "exp_002", "config": {"learning_rate": 0.0005, ...}},
    {"job_id": "exp_003", "config": {"learning_rate": 0.0001, ...}},
    # Add as many as you want!
]
```

### Step 4: Monitor

```bash
# Visit dashboard
http://localhost:5000/status

# Or command line:
curl http://localhost:5000/status | jq
```

---

## Example: Training 9 Different Configurations

With 3 RPis, you can run 9 experiments in the time of 3:

```
RPi #1: Job 1 → Job 4 → Job 7
RPi #2: Job 2 → Job 5 → Job 8
RPi #3: Job 3 → Job 6 → Job 9

Serial (1 device): 9 × 2 days = 18 days
Parallel (3 devices): 3 × 2 days = 6 days
```

**3x faster!**

---

## Next Steps

1. Implement master server
2. Implement worker daemon
3. Create setup scripts
4. Test with 1 RPi
5. Scale to multiple RPis
6. Add web dashboard (optional)
7. Implement Git auto-sync

Want me to create the complete implementation files?
