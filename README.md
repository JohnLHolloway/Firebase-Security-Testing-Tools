# Firebase Security Testing Tools

Automated security testing tools for demonstrating Firebase Firestore vulnerabilities.

**Target:** jordancota.site Space Invaders leaderboard
**Purpose:** Security testing and vulnerability demonstration

## Overview

This repository contains tools to test and demonstrate critical security vulnerabilities in web applications using Firebase Firestore without proper security rules.

## Files

- **[security_test.py](security_test.py)** - One-time security vulnerability demonstration
- **[security_worker.py](security_worker.py)** - Continuous automated security testing worker
- **[deploy_to_rpi.sh](deploy_to_rpi.sh)** - Deployment script for Raspberry Pi

## Vulnerability Description

The target website exposes Firebase credentials in client-side JavaScript and has no security rules, allowing:

1. **Arbitrary Database Writes** - Anyone can submit scores without playing
2. **No Authentication** - No validation of legitimate gameplay
3. **Public Data Access** - Full database readable by anyone
4. **No Rate Limiting** - Automated scripts can spam submissions

## Usage

### One-Time Security Test

Run the demonstration script to show the vulnerability:

```bash
python security_test.py
```

This will:
- Show exposed Firebase credentials
- Demonstrate payload structure
- Test database read access
- Display security recommendations

**Note:** Runs in DRY RUN mode - no actual submissions

### Continuous Security Testing (Raspberry Pi)

Deploy the automated worker to continuously test the vulnerability:

```bash
# 1. Edit deploy_to_rpi.sh with your RPi IP address
# 2. Run deployment script
bash deploy_to_rpi.sh

# 3. Monitor on Raspberry Pi
ssh pi@192.168.1.194 'sudo journalctl -u security-worker -f'
```

The worker will:
- Check leaderboard every 30 minutes
- Only submit if "John H" is NOT currently the leader
- Submit score 10 points higher than current high score when needed
- Increment level with each submission
- Run continuously as system service
- Demonstrate reactive vulnerability exploitation

### Manual Worker Execution

To run the worker without deploying to RPi:

```bash
python security_worker.py
```

Press Ctrl+C to stop.

## Configuration

Edit `security_worker.py` to customize:

```python
PLAYER_NAME = "John H"          # Name to submit
CHECK_INTERVAL = 30 * 60        # 30 minutes (in seconds)
SCORE_INCREMENT = 10            # Points to add each time
```

## Security Recommendations

### For Website Owner:

**1. Implement Firebase Security Rules:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /scores/{score} {
      allow read: if true;
      allow write: if false;  // Disable all client writes
    }
  }
}
```

**2. Use Firebase Cloud Functions:**
- Move score submission to server-side
- Validate gameplay before accepting scores
- Implement rate limiting

**3. Add Authentication:**
- Use Firebase Authentication
- Track user sessions
- Require auth for score submission

**4. Implement Anti-Cheat:**
- Verify game state progression
- Use signed tokens
- Track session timestamps
- Validate score increments

**5. Protect API Keys:**
- Use environment variables
- Restrict API keys to specific domains
- Never expose credentials in client code

## Deployment to Raspberry Pi

The `deploy_to_rpi.sh` script will:
1. Copy worker script to RPi
2. Create systemd service
3. Enable auto-start on boot
4. Start the worker

**Commands:**
```bash
# Check status
ssh pi@192.168.1.194 'sudo systemctl status security-worker'

# View logs
ssh pi@192.168.1.194 'sudo journalctl -u security-worker -f'

# Stop worker
ssh pi@192.168.1.194 'sudo systemctl stop security-worker'

# Restart worker
ssh pi@192.168.1.194 'sudo systemctl restart security-worker'
```

## Requirements

```bash
pip install requests
```

That's it! The scripts only need the `requests` library.

## Ethical Considerations

These tools are for:
- ✅ Security testing with permission
- ✅ Demonstrating vulnerabilities to developers
- ✅ Educational purposes
- ✅ Improving web application security

**NOT** for:
- ❌ Malicious hacking
- ❌ Unauthorized access
- ❌ Data theft
- ❌ Service disruption

Always obtain permission before testing third-party systems.

## Results

The automated worker demonstrates:
- Continuous exploitation over time
- Lack of detection mechanisms
- Need for proper security implementation
- Impact of missing validation

Expected behavior:
- Worker monitors leaderboard every 30 minutes
- Only submits when someone else beats "John H"
- When submitting, adds 10 points to current high score
- Level increments with each submission
- No alerts or blocking mechanisms trigger
- Database accepts all submissions without validation
- Demonstrates reactive, competitive exploitation

## License

MIT License - For educational and security testing purposes only.

## Contact

For questions about security testing or vulnerability reporting, contact the website administrator directly.
