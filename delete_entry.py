"""
DELETE SPECIFIC FIREBASE ENTRY
===============================
This script deletes a specific entry from the Firebase Firestore database.

Target: Remove "John H" entry with score 27470 and level 1
"""

import requests
import json

# Firebase configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyBDM1Tk1Pj1M1O1jkPHXsKSlnj1h4kp1km0",
    "projectId": "leaderboard-personal-site"
}

class FirebaseDeleter:
    def __init__(self):
        self.project_id = FIREBASE_CONFIG["projectId"]
        self.api_key = FIREBASE_CONFIG["apiKey"]
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"

    def get_all_entries(self):
        """Fetch all entries from the leaderboard"""
        try:
            url = f"{self.base_url}/scores"
            params = {"key": self.api_key}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                return documents
            else:
                print(f"Error fetching entries: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error getting entries: {e}")
            return []

    def find_entry(self, target_name, target_score, target_level):
        """Find the document ID for a specific entry"""
        documents = self.get_all_entries()

        matching_entries = []

        for doc in documents:
            fields = doc.get('fields', {})
            name = fields.get('name', {}).get('stringValue', '')
            score = int(fields.get('score', {}).get('integerValue', '0'))
            level = int(fields.get('level', {}).get('integerValue', '0'))
            doc_id = doc.get('name', '').split('/')[-1]

            if name == target_name and score == target_score and level == target_level:
                matching_entries.append({
                    'doc_id': doc_id,
                    'name': name,
                    'score': score,
                    'level': level,
                    'full_path': doc.get('name', '')
                })

        return matching_entries

    def delete_entry(self, doc_id):
        """Delete a specific document by ID"""
        try:
            url = f"{self.base_url}/scores/{doc_id}?key={self.api_key}"

            response = requests.delete(url, timeout=10)

            if response.status_code == 200:
                return True
            else:
                print(f"Deletion failed: {response.status_code}")
                print(response.text)
                return False

        except Exception as e:
            print(f"Error deleting entry: {e}")
            return False

def main():
    """Main function to delete the specific entry"""
    print("=" * 70)
    print("FIREBASE ENTRY DELETION")
    print("=" * 70)
    print()

    TARGET_NAME = "John H"
    TARGET_SCORE = 27470
    TARGET_LEVEL = 1

    deleter = FirebaseDeleter()

    print(f"Searching for entry: {TARGET_NAME}, Score: {TARGET_SCORE}, Level: {TARGET_LEVEL}")
    print()

    matching_entries = deleter.find_entry(TARGET_NAME, TARGET_SCORE, TARGET_LEVEL)

    if not matching_entries:
        print("X No matching entry found!")
        print()
        print("Fetching all entries to show what's available:")
        all_docs = deleter.get_all_entries()
        print(f"\nFound {len(all_docs)} total entries:")
        for doc in all_docs:
            fields = doc.get('fields', {})
            name = fields.get('name', {}).get('stringValue', '')
            score = int(fields.get('score', {}).get('integerValue', '0'))
            level = int(fields.get('level', {}).get('integerValue', '0'))
            print(f"  - {name}: Score={score}, Level={level}")
        return

    print(f"Found {len(matching_entries)} matching entry(ies):")
    for i, entry in enumerate(matching_entries, 1):
        print(f"\n  Entry #{i}:")
        print(f"    Name: {entry['name']}")
        print(f"    Score: {entry['score']}")
        print(f"    Level: {entry['level']}")
        print(f"    Document ID: {entry['doc_id']}")

    print()
    print("=" * 70)
    print("DELETING ENTRIES...")
    print("=" * 70)
    print()

    deleted_count = 0
    for entry in matching_entries:
        print(f"Deleting document ID: {entry['doc_id']}...")
        success = deleter.delete_entry(entry['doc_id'])

        if success:
            print(f"Successfully deleted: {entry['name']} (Score: {entry['score']}, Level: {entry['level']})")
            deleted_count += 1
        else:
            print(f"X Failed to delete: {entry['doc_id']}")

    print()
    print("=" * 70)
    print(f"COMPLETE: Deleted {deleted_count} of {len(matching_entries)} entries")
    print("=" * 70)

if __name__ == "__main__":
    main()
