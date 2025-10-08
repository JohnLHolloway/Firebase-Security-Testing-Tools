"""
Test Worker - Simulates a training worker for testing the master server
Runs on Windows to test the distributed system locally
"""
import requests
import socket
import json
import time
from datetime import datetime
import random

class TestWorker:
    def __init__(self, master_ip="localhost"):
        self.master_ip = master_ip
        self.hostname = f"test-worker-{socket.gethostname()}"
        self.worker_id = None

    def register(self):
        """Register with master"""
        url = f"http://{self.master_ip}:5000/register"
        data = {
            "hostname": self.hostname,
            "capabilities": {
                "cpu_cores": 4,
                "platform": "Windows-Test",
                "machine": "x86_64"
            }
        }

        try:
            response = requests.post(url, json=data, timeout=5)
            if response.status_code == 200:
                self.worker_id = response.json().get("worker_id")
                print(f"✅ Registered as: {self.hostname}")
                return True
        except Exception as e:
            print(f"❌ Registration failed: {e}")
        return False

    def send_heartbeat(self):
        """Send heartbeat"""
        try:
            url = f"http://{self.master_ip}:5000/heartbeat"
            requests.post(url, json={"status": "idle"}, timeout=2)
        except:
            pass

    def get_job(self):
        """Get a job from master"""
        try:
            url = f"http://{self.master_ip}:5000/get_job"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None

    def simulate_training(self, job):
        """Simulate training job"""
        job_id = job.get("job_id")
        config = job.get("config")

        print(f"\n{'='*60}")
        print(f"🎮 Simulating job: {job_id}")
        print(f"   {config.get('description')}")
        print(f"   Config: {config}")
        print(f"{'='*60}\n")

        # Simulate training for 10 seconds with progress updates
        for i in range(10):
            print(f"   Training... {(i+1)*10}% complete")
            time.sleep(1)

        # Simulate random score (higher LR sometimes gets better scores)
        lr = config.get("learning_rate", 0.001)
        base_score = 100 + (1/lr) * random.randint(50, 150)
        best_score = int(base_score)

        print(f"\n✅ Training complete! Best score: {best_score}\n")

        return {
            "success": True,
            "job_id": job_id,
            "model_path": f"./models/test_{job_id}.zip",
            "metrics": {
                "best_score": best_score,
                "training_time": 10,
                "episodes": 50
            }
        }

    def report_result(self, result):
        """Report results to master"""
        try:
            url = f"http://{self.master_ip}:5000/report_result"
            response = requests.post(url, json=result, timeout=10)
            if response.status_code == 200:
                print(f"✅ Reported results for {result['job_id']}")
                return True
        except Exception as e:
            print(f"❌ Failed to report: {e}")
        return False

    def run(self):
        """Main test worker loop"""
        print("="*60)
        print(f"TEST WORKER: {self.hostname}")
        print("="*60 + "\n")

        if not self.register():
            print("Failed to register. Is master running?")
            return

        print("✅ Worker ready! Requesting jobs...\n")

        # Process jobs until queue is empty
        jobs_completed = 0

        while True:
            # Send heartbeat
            self.send_heartbeat()

            # Get job
            job = self.get_job()

            if job:
                # Simulate training
                result = self.simulate_training(job)

                # Report results
                self.report_result(result)

                jobs_completed += 1
                print(f"📊 Jobs completed: {jobs_completed}\n")

            else:
                print("⏳ No more jobs. Check the dashboard!")
                break

            time.sleep(2)

        print(f"\n{'='*60}")
        print(f"✅ Test worker finished! Completed {jobs_completed} jobs")
        print(f"   Check the dashboard to see results!")
        print("="*60)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--master", default="localhost", help="Master IP")
    args = parser.parse_args()

    worker = TestWorker(master_ip=args.master)
    worker.run()
