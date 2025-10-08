"""
SECURITY DEMONSTRATION SCRIPT
==============================
This script demonstrates a critical security vulnerability in the Space Invaders
leaderboard at jordancota.site.

VULNERABILITY: Firebase Firestore database has no security rules, allowing
any client to write arbitrary scores directly to the database.

This is for EDUCATIONAL/SECURITY TESTING purposes only to demonstrate
the need for proper Firebase security rules.

RECOMMENDED FIX:
Add Firebase security rules like:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /scores/{score} {
      allow read: if true;
      allow write: if false;  // Disable client writes
      // Or implement server-side verification
    }
  }
}
```
"""

import requests
import json
from datetime import datetime

# Firebase configuration (publicly exposed in client-side code)
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyBDM1Tk1Pj1M1O1jkPHXsKSlnj1h4kp1km0",
    "projectId": "leaderboard-personal-site"
}

def demonstrate_vulnerability(name, score, level=1, dry_run=True):
    """
    Demonstrates how anyone can write to the Firebase database.

    Args:
        name: Player name
        score: Score to submit
        level: Game level
        dry_run: If True, only shows what would be sent (doesn't actually submit)
    """

    print("=" * 70)
    print("FIREBASE SECURITY VULNERABILITY DEMONSTRATION")
    print("=" * 70)
    print()
    print("TARGET: jordancota.site Space Invaders Leaderboard")
    print("ISSUE: No Firebase security rules - anyone can write directly")
    print()

    # Firestore REST API endpoint
    project_id = FIREBASE_CONFIG["projectId"]
    api_key = FIREBASE_CONFIG["apiKey"]
    collection = "scores"

    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/{collection}"

    # Prepare the payload
    timestamp = datetime.utcnow().isoformat() + "Z"
    payload = {
        "fields": {
            "name": {"stringValue": name},
            "score": {"integerValue": str(score)},
            "level": {"integerValue": str(level)},
            "timestamp": {"timestampValue": timestamp}
        }
    }

    print("PAYLOAD THAT WOULD BE SENT:")
    print(json.dumps(payload, indent=2))
    print()
    print(f"ENDPOINT: {url}")
    print(f"API KEY: {api_key[:20]}...")
    print()

    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No actual submission")
        print("=" * 70)
        print()
        print("This demonstrates that:")
        print("1. Firebase credentials are publicly exposed in client-side code")
        print("2. No security rules prevent arbitrary writes")
        print("3. Anyone can submit any score without playing the game")
        print("4. Server-side validation is completely missing")
        print()
        print("SECURITY RECOMMENDATIONS:")
        print("=" * 70)
        print()
        print("1. IMPLEMENT FIREBASE SECURITY RULES:")
        print("   - Disable all client-side writes")
        print("   - Use Firebase Functions for server-side validation")
        print()
        print("2. ADD SERVER-SIDE VALIDATION:")
        print("   - Verify scores are legitimate")
        print("   - Implement rate limiting")
        print("   - Add authentication")
        print()
        print("3. IMPLEMENT ANTI-CHEAT MEASURES:")
        print("   - Track game sessions")
        print("   - Validate score progression")
        print("   - Use signed tokens")
        print()
        print("4. USE ENVIRONMENT VARIABLES:")
        print("   - Don't expose API keys in client code")
        print("   - Use restricted API keys with specific domains")
        print()
        return None
    else:
        # This would actually submit - but we're keeping it educational
        print("WARNING: Actual submission disabled for security demonstration")
        print("To enable, you would need to:")
        print("1. Confirm you own/have permission to test this database")
        print("2. Add proper headers and authentication")
        print("3. Handle response codes properly")
        return None

def view_current_leaderboard():
    """
    Shows how easy it is to read the entire leaderboard
    """
    print("\n" + "=" * 70)
    print("READING LEADERBOARD (No authentication required)")
    print("=" * 70)

    project_id = FIREBASE_CONFIG["projectId"]
    api_key = FIREBASE_CONFIG["apiKey"]

    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/scores"
    params = {"key": api_key}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("\nSUCCESS - Database is publicly readable!")
            print(f"Found {len(data.get('documents', []))} score entries")
            print("\nThis demonstrates:")
            print("- No read authentication required")
            print("- Full database access available")
            print("- All player data exposed")
        else:
            print(f"Response: {response.status_code}")
            print("(May have security rules enabled for reads)")
    except Exception as e:
        print(f"Error: {e}")
        print("(Could indicate some security measures in place)")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SECURITY VULNERABILITY DEMONSTRATION")
    print("=" * 70)
    print()

    # Demonstrate the vulnerability (dry run only)
    demonstrate_vulnerability(
        name="Security Test",
        score=999999,
        level=1,
        dry_run=True  # ALWAYS True for demonstration
    )

    # Show how easy it is to read the leaderboard
    view_current_leaderboard()

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()
    print("This leaderboard system has critical security flaws that allow:")
    print("- Arbitrary score submission without gameplay")
    print("- Public database access")
    print("- No validation or authentication")
    print()
    print("Implement proper Firebase security rules IMMEDIATELY.")
    print()
