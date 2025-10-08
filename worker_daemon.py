"""
Training Worker Daemon
Runs on Raspberry Pi - executes training jobs from master
"""
import requests
import socket
import json
import time
import subprocess
import os
import sys
from datetime import datetime
import threading
import platform

class TrainingWorker:
    def __init__(self, master_ip=None, project_dir=None):
        self.master_ip = master_ip
        self.hostname = socket.gethostname()
        self.worker_id = None
        self.running = True
        self.project_dir = project_dir or os.getcwd()

    def discover_master(self):
        """Listen for master broadcast"""
        print("🔍 Looking for master node...")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            sock.bind(('', 5001))
            sock.settimeout(10)

            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    message = json.loads(data.decode())

                    if message.get("type") == "discover" and message.get("master"):
                        # Respond to master
                        response = json.dumps({
                            "type": "worker",
                            "hostname": self.hostname,
                            "capabilities": self.get_capabilities()
                        }).encode()

                        sock.sendto(response, addr)
                        master_ip = addr[0]

                        sock.close()
                        print(f"✅ Found master at {master_ip}")
                        return master_ip

                except socket.timeout:
                    print("⏱️  Discovery timeout, retrying...")
                    continue

        except Exception as e:
            print(f"❌ Discovery error: {e}")
            sock.close()
            return None

    def get_capabilities(self):
        """Get system capabilities"""
        return {
            "cpu_cores": os.cpu_count(),
            "platform": platform.system(),
            "machine": platform.machine(),
            "python_version": platform.python_version()
        }

    def register(self):
        """Register with master"""
        if not self.master_ip:
            self.master_ip = self.discover_master()

        if not self.master_ip:
            return False

        url = f"http://{self.master_ip}:5000/register"
        data = {
            "hostname": self.hostname,
            "capabilities": self.get_capabilities()
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
            elif response.status_code == 204:
                # No jobs available
                return None
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

        # Build command
        python_cmd = "python3" if platform.system() != "Windows" else "python"
        cmd = [
            python_cmd, "train_fixed.py",
            "--timesteps", str(config.get("timesteps")),
        ]

        # Note: train_fixed.py would need to accept these args
        # For now, we'll modify the command to work with existing script

        start_time = time.time()

        try:
            # Execute training
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=self.project_dir
            )

            # Stream output
            for line in process.stdout:
                print(line, end='')

            process.wait()
            elapsed = time.time() - start_time

            # Check for success
            if process.returncode == 0:
                # Find best model
                models_dir = os.path.join(self.project_dir, "models")
                if os.path.exists(models_dir):
                    models = [f for f in os.listdir(models_dir) if f.endswith('.zip')]
                    if models:
                        latest_model = max(models, key=lambda f: os.path.getmtime(os.path.join(models_dir, f)))
                        model_path = os.path.join(models_dir, latest_model)

                        # TODO: Extract metrics from training output or saved file
                        # For now, just report success
                        return {
                            "success": True,
                            "model_path": model_path,
                            "job_id": job_id,
                            "metrics": {
                                "training_time": elapsed,
                                "best_score": "unknown"  # Would need to parse from logs
                            }
                        }

            return {
                "success": False,
                "error": f"Process exited with code {process.returncode}",
                "job_id": job_id
            }

        except Exception as e:
            print(f"❌ Job failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "job_id": job_id
            }

    def report_result(self, result):
        """Report job completion to master"""
        try:
            url = f"http://{self.master_ip}:5000/report_result"
            response = requests.post(url, json=result, timeout=10)

            if response.status_code == 200:
                print(f"✅ Reported results for {result['job_id']}")
                return True
            else:
                print(f"⚠️  Result report returned {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to report results: {e}")

        return False

    def git_push_model(self, model_path):
        """Push model to Git (optional)"""
        try:
            print(f"📤 Pushing model to Git...")

            # Add model
            subprocess.run(["git", "add", model_path], cwd=self.project_dir)

            # Commit
            commit_msg = f"Model from {self.hostname} - {datetime.now().isoformat()}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.project_dir)

            # Push
            subprocess.run(["git", "push"], cwd=self.project_dir)

            print(f"✅ Model pushed to Git")
            return True
        except Exception as e:
            print(f"⚠️  Git push failed: {e}")
            return False

    def run(self):
        """Main worker loop"""
        print("="*60)
        print(f"🤖 TRAINING WORKER: {self.hostname}")
        print(f"   Platform: {platform.system()} {platform.machine()}")
        print(f"   CPUs: {os.cpu_count()}")
        print(f"   Project dir: {self.project_dir}")
        print("="*60 + "\n")

        # Register with master
        max_register_attempts = 5
        for attempt in range(max_register_attempts):
            if self.register():
                break
            print(f"Retry registration in 10 seconds... ({attempt + 1}/{max_register_attempts})")
            time.sleep(10)
        else:
            print("❌ Could not register with master after multiple attempts. Exiting.")
            return

        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self.send_heartbeat, daemon=True)
        heartbeat_thread.start()

        print("\n✅ Worker ready. Waiting for jobs...\n")

        # Main job loop
        job_wait_interval = 30  # Check for jobs every 30 seconds

        while self.running:
            try:
                job = self.get_job()

                if job:
                    # Execute job
                    result = self.execute_job(job)

                    # Report results
                    self.report_result(result)

                    # Optional: Push to Git
                    if result.get("success") and result.get("model_path"):
                        # Uncomment to enable Git push:
                        # self.git_push_model(result["model_path"])
                        pass

                else:
                    # No jobs available, wait
                    print(f"⏳ No jobs available. Checking again in {job_wait_interval}s...")
                    time.sleep(job_wait_interval)

            except KeyboardInterrupt:
                print("\n\n⏹️  Worker shutting down...")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(job_wait_interval)

        print("👋 Worker stopped.")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Training Worker Daemon')
    parser.add_argument('--master', type=str, help='Master node IP address')
    parser.add_argument('--project-dir', type=str, help='Project directory path')
    args = parser.parse_args()

    worker = TrainingWorker(
        master_ip=args.master,
        project_dir=args.project_dir
    )

    try:
        worker.run()
    except KeyboardInterrupt:
        print("\n\nShutting down...")

if __name__ == "__main__":
    main()
