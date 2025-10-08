"""
Master Training Orchestrator Server
Runs on Windows PC - coordinates distributed training across Raspberry Pis
"""
from flask import Flask, request, jsonify, render_template_string
import socket
import threading
import json
from datetime import datetime, timedelta
import subprocess
import ipaddress
import concurrent.futures
import sys
import io

# Fix console encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

app = Flask(__name__)

# Global state
workers = {}  # {ip: {hostname, last_seen, status, current_job, specs}}
job_queue = []
completed_jobs = []
job_history = []

class WorkerDiscovery:
    """Auto-discover RPis on local network"""

    def __init__(self, port=5000):
        self.port = port
        self.broadcast_port = 5001

    def get_local_network(self):
        """Get local network range"""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            return network, local_ip
        except Exception as e:
            print(f"Error getting network: {e}")
            return None, None

    def scan_network(self):
        """Scan local network for workers"""
        network, local_ip = self.get_local_network()
        if not network:
            return []

        print(f"Scanning network: {network}")
        active_workers = []

        def check_host(ip):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)
                result = sock.connect_ex((str(ip), self.port))
                sock.close()
                if result == 0:
                    return str(ip)
            except:
                pass
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(check_host, network.hosts())
            active_workers = [ip for ip in results if ip and ip != local_ip]

        return active_workers

    def broadcast_discovery(self):
        """Broadcast UDP to find workers"""
        print("Broadcasting discovery message...")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(3)

        # Broadcast discovery message
        message = json.dumps({"type": "discover", "master": True}).encode()

        try:
            sock.sendto(message, ('<broadcast>', self.broadcast_port))

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
        except Exception as e:
            print(f"Broadcast error: {e}")
            sock.close()
            return []

# API Endpoints

@app.route('/')
def dashboard():
    """Web dashboard"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>ML Training Cluster Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: monospace; background: #1a1a1a; color: #0f0; padding: 20px; }
        h1 { color: #0ff; }
        .section { background: #0a0a0a; padding: 15px; margin: 15px 0; border: 1px solid #0f0; }
        .worker { background: #1a2a1a; margin: 10px 0; padding: 10px; border-left: 4px solid #0f0; }
        .idle { border-left-color: #0f0; }
        .training { border-left-color: #ff0; }
        .offline { border-left-color: #f00; }
        .job { background: #2a1a1a; margin: 10px 0; padding: 10px; }
        .stats { display: flex; gap: 20px; }
        .stat-box { flex: 1; text-align: center; padding: 15px; background: #0a2a0a; }
        .stat-value { font-size: 32px; font-weight: bold; color: #0ff; }
        button { background: #0a4a0a; color: #0f0; border: 1px solid #0f0; padding: 10px 20px; cursor: pointer; }
        button:hover { background: #0f0; color: #000; }
    </style>
</head>
<body>
    <h1>🎮 Space Invaders ML Training Cluster</h1>

    <div class="stats">
        <div class="stat-box">
            <div class="stat-value">{{ workers|length }}</div>
            <div>Active Workers</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{{ jobs_pending }}</div>
            <div>Jobs Pending</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{{ jobs_completed }}</div>
            <div>Jobs Completed</div>
        </div>
    </div>

    <div class="section">
        <h2>👷 Workers</h2>
        {% if workers %}
            {% for ip, worker in workers.items() %}
            <div class="worker {{ worker.status }}">
                <strong>{{ worker.hostname }}</strong> ({{ ip }})<br>
                Status: {{ worker.status }}<br>
                Last seen: {{ worker.last_seen }}<br>
                {% if worker.current_job %}
                Current job: {{ worker.current_job }}<br>
                {% endif %}
            </div>
            {% endfor %}
        {% else %}
            <p>No workers registered. Waiting for workers to connect...</p>
        {% endif %}
    </div>

    <div class="section">
        <h2>📋 Job Queue ({{ jobs_pending }})</h2>
        {% for job in queue %}
        <div class="job">
            <strong>{{ job.job_id }}</strong>: {{ job.config.description }}<br>
            LR={{ job.config.learning_rate }}, Batch={{ job.config.batch_size }}, Steps={{ job.config.timesteps }}
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>✅ Completed Jobs ({{ jobs_completed }})</h2>
        {% for job in completed[:5] %}
        <div class="job">
            <strong>{{ job.job_id }}</strong> - Worker: {{ job.worker }}<br>
            Best Score: {{ job.metrics.get('best_score', 'N/A') }}<br>
            Completed: {{ job.timestamp }}
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>🔧 Actions</h2>
        <button onclick="location.reload()">Refresh Now</button>
        <button onclick="if(confirm('Create 3 new test jobs?')) fetch('/create_test_jobs', {method: 'POST'}).then(() => location.reload())">Create Test Jobs</button>
        <button onclick="scanNetwork()">Scan for RPis</button>
    </div>

    <div class="section" id="rpi-deployment" style="display:none;">
        <h2>🥧 Deploy to Raspberry Pis</h2>
        <div id="discovered-pis"></div>
    </div>

    <script>
    function scanNetwork() {
        document.getElementById('rpi-deployment').style.display = 'block';
        document.getElementById('discovered-pis').innerHTML = '<p>Scanning network...</p>';

        fetch('/scan_rpis')
            .then(response => response.json())
            .then(data => {
                if (data.found && data.found.length > 0) {
                    let html = '<h3>Found ' + data.found.length + ' Raspberry Pi(s)</h3>';
                    data.found.forEach(pi => {
                        html += '<div class="worker" style="display:flex; justify-content:space-between; align-items:center;">';
                        html += '<div><strong>' + pi.hostname + '</strong> (' + pi.ip + ')</div>';
                        html += '<button onclick="deployToPi(\'' + pi.ip + '\', \'' + pi.hostname + '\')">Deploy Worker</button>';
                        html += '</div>';
                    });
                    document.getElementById('discovered-pis').innerHTML = html;
                } else {
                    document.getElementById('discovered-pis').innerHTML = '<p>No Raspberry Pis found on network.</p>';
                }
            })
            .catch(err => {
                document.getElementById('discovered-pis').innerHTML = '<p>Error scanning: ' + err + '</p>';
            });
    }

    function deployToPi(ip, hostname) {
        const username = prompt('Enter SSH username for ' + hostname + ':', 'pi');
        if (!username) return;

        const password = prompt('Enter SSH password:');
        if (!password) return;

        document.getElementById('discovered-pis').innerHTML += '<p>Deploying to ' + hostname + '...</p>';

        fetch('/deploy_worker', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                ip: ip,
                hostname: hostname,
                username: username,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Successfully deployed worker to ' + hostname + '!\\nWorker should connect automatically.');
                location.reload();
            } else {
                alert('Deployment failed: ' + data.error);
            }
        })
        .catch(err => {
            alert('Error deploying: ' + err);
        });
    }
    </script>
</body>
</html>
    """
    return render_template_string(
        html,
        workers=workers,
        jobs_pending=len(job_queue),
        jobs_completed=len(completed_jobs),
        queue=job_queue,
        completed=completed_jobs[::-1]  # Reverse for latest first
    )

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
    print(f"   Specs: {data.get('capabilities')}")
    return jsonify({"status": "registered", "worker_id": worker_ip})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """Worker heartbeat"""
    worker_ip = request.remote_addr
    if worker_ip in workers:
        workers[worker_ip]["last_seen"] = datetime.now().isoformat()
        data = request.json
        workers[worker_ip]["status"] = data.get("status", "idle")

        # Optional: Update progress
        if "progress" in data:
            workers[worker_ip]["progress"] = data["progress"]

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

        print(f"📤 Assigned job {job['job_id']} to {workers[worker_ip]['hostname']} ({worker_ip})")
        return jsonify(job)

    return jsonify({"status": "no_jobs"}), 204

@app.route('/report_result', methods=['POST'])
def report_result():
    """Worker reports training results"""
    data = request.json
    worker_ip = request.remote_addr

    result = {
        "worker": worker_ip,
        "worker_name": workers.get(worker_ip, {}).get("hostname", "unknown"),
        "job_id": data.get("job_id"),
        "metrics": data.get("metrics", {}),
        "model_path": data.get("model_path"),
        "timestamp": datetime.now().isoformat(),
        "success": data.get("success", False)
    }

    completed_jobs.append(result)
    job_history.append(result)

    if worker_ip in workers:
        workers[worker_ip]["status"] = "idle"
        workers[worker_ip]["current_job"] = None

    print(f"\n{'='*60}")
    print(f"✅ Job {data.get('job_id')} completed")
    print(f"   Worker: {result['worker_name']} ({worker_ip})")
    print(f"   Best score: {data.get('metrics', {}).get('best_score', 'N/A')}")
    print(f"   Success: {data.get('success')}")
    print(f"{'='*60}\n")

    return jsonify({"status": "recorded"})

@app.route('/status', methods=['GET'])
def status():
    """Get cluster status (JSON API)"""
    return jsonify({
        "workers": workers,
        "jobs_pending": len(job_queue),
        "jobs_completed": len(completed_jobs),
        "queue": job_queue,
        "completed": completed_jobs
    })

@app.route('/create_test_jobs', methods=['POST'])
def create_test_jobs():
    """Create test jobs on demand"""
    global job_queue
    new_jobs = create_jobs()
    job_queue.extend(new_jobs)
    print(f"📋 Created {len(new_jobs)} new test jobs")
    return jsonify({"status": "created", "count": len(new_jobs)})

@app.route('/scan_rpis', methods=['GET'])
def scan_rpis():
    """Scan network for Raspberry Pis"""
    try:
        # Get local network
        discovery = WorkerDiscovery()
        network, local_ip = discovery.get_local_network()

        if not network:
            return jsonify({"found": [], "error": "Could not determine network"})

        print(f"Scanning {network} for Raspberry Pis...")

        # Simple approach: scan for open SSH port (22)
        found_pis = []

        # Quick scan for SSH on common RPi IPs
        import concurrent.futures

        def check_pi(ip_str):
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip_str, 22))  # SSH port
                sock.close()

                if result == 0:
                    # Try to get hostname
                    try:
                        hostname = socket.gethostbyaddr(ip_str)[0]
                    except:
                        hostname = ip_str

                    # Check if it looks like a Pi
                    if any(x in hostname.lower() for x in ['raspberrypi', 'rpi', 'pi']):
                        return {"ip": ip_str, "hostname": hostname}
                    # Or if SSH is open, assume it might be a Pi
                    elif hostname != ip_str:
                        return {"ip": ip_str, "hostname": hostname}
            except:
                pass
            return None

        # Scan network
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(check_pi, [str(ip) for ip in network.hosts()])
            found_pis = [pi for pi in results if pi]

        print(f"Found {len(found_pis)} potential Raspberry Pis")
        return jsonify({"found": found_pis})

    except Exception as e:
        print(f"Error scanning: {e}")
        return jsonify({"found": [], "error": str(e)})

@app.route('/deploy_worker', methods=['POST'])
def deploy_worker():
    """Deploy worker to Raspberry Pi via SSH"""
    import paramiko
    import os

    data = request.json
    ip = data.get('ip')
    hostname = data.get('hostname')
    username = data.get('username')
    password = data.get('password')

    print(f"\nDeploying worker to {hostname} ({ip})...")

    try:
        # Connect via SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)

        print(f"✅ Connected to {hostname}")

        # Get master IP
        master_ip = request.host.split(':')[0]

        # Create deployment script
        deploy_script = f"""
#!/bin/bash
set -e

echo "Setting up ML training worker on {hostname}..."

# Update system
sudo apt update

# Install dependencies
sudo apt install -y python3-pip git chromium-browser chromium-chromedriver

# Create project directory
mkdir -p ~/ml-training
cd ~/ml-training

# Install Python packages
pip3 install flask requests stable-baselines3 selenium opencv-python pillow numpy beautifulsoup4

echo "Installation complete!"
echo "Master server: {master_ip}:5000"
"""

        # Upload files
        sftp = ssh.open_sftp()

        # Upload worker daemon
        project_dir = os.path.dirname(os.path.abspath(__file__))
        files_to_upload = [
            'worker_daemon.py',
            'stable_web_env.py',
            'train_fixed.py',
            'get_high_score.py',
            'requirements.txt'
        ]

        for filename in files_to_upload:
            local_path = os.path.join(project_dir, filename)
            remote_path = f'/home/{username}/ml-training/{filename}'

            if os.path.exists(local_path):
                print(f"  Uploading {filename}...")
                sftp.put(local_path, remote_path)

        sftp.close()

        # Run setup
        print("  Running setup...")
        stdin, stdout, stderr = ssh.exec_command('cd ~/ml-training && pip3 install flask requests')
        stdout.channel.recv_exit_status()  # Wait for completion

        # Start worker in background
        print("  Starting worker...")
        command = f'cd ~/ml-training && nohup python3 worker_daemon.py --master {master_ip} > worker.log 2>&1 &'
        ssh.exec_command(command)

        ssh.close()

        print(f"✅ Successfully deployed to {hostname}")
        return jsonify({"success": True, "message": f"Worker deployed to {hostname}"})

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return jsonify({"success": False, "error": str(e)})

# Job Creation

def create_jobs():
    """Create training jobs with different hyperparameters"""
    jobs = [
        {
            "job_id": f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_001",
            "config": {
                "learning_rate": 0.001,
                "batch_size": 32,
                "timesteps": 50000,
                "description": "High learning rate, fast test"
            }
        },
        {
            "job_id": f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_002",
            "config": {
                "learning_rate": 0.0005,
                "batch_size": 32,
                "timesteps": 50000,
                "description": "Medium learning rate, fast test"
            }
        },
        {
            "job_id": f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_003",
            "config": {
                "learning_rate": 0.0001,
                "batch_size": 64,
                "timesteps": 50000,
                "description": "Low learning rate, larger batch"
            }
        }
    ]
    return jobs

def cleanup_offline_workers():
    """Remove workers that haven't been seen in 5 minutes"""
    while True:
        import time
        time.sleep(60)  # Check every minute

        now = datetime.now()
        offline_timeout = timedelta(minutes=5)

        for ip in list(workers.keys()):
            last_seen = datetime.fromisoformat(workers[ip]["last_seen"])
            if now - last_seen > offline_timeout:
                print(f"❌ Worker {workers[ip]['hostname']} ({ip}) went offline")
                del workers[ip]

def start_master():
    """Start master server"""
    print("="*60)
    print("🎮 SPACE INVADERS ML - DISTRIBUTED TRAINING MASTER")
    print("="*60)

    # Get local IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"\n💻 Master Node: {hostname} ({local_ip})")

    # Discover workers
    print("\n🔍 Discovering workers on network...")
    discovery = WorkerDiscovery()

    # Try broadcast discovery
    found_workers = discovery.broadcast_discovery()
    if found_workers:
        print(f"✅ Found {len(found_workers)} workers via broadcast:")
        for w in found_workers:
            print(f"   • {w['hostname']} ({w['ip']})")
    else:
        print("⚠️  No workers responded to broadcast")
        print("   Workers will register when they start")

    # Create initial job queue
    global job_queue
    job_queue = create_jobs()
    print(f"\n📋 Created {len(job_queue)} initial training jobs")

    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_offline_workers, daemon=True)
    cleanup_thread.start()

    # Start server
    print(f"\n🚀 Master server starting...")
    print(f"   API: http://{local_ip}:5000")
    print(f"   Dashboard: http://{local_ip}:5000")
    print(f"   Or: http://localhost:5000")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == "__main__":
    try:
        start_master()
    except KeyboardInterrupt:
        print("\n\n👋 Master server shutting down...")
        print("Goodbye!")
