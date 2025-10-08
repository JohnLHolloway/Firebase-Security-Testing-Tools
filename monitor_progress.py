"""
Quick Training Progress Monitor
"""
import re
import sys
import io

# Fix console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def extract_scores_from_output(text):
    """Extract game scores from training output"""
    scores = []
    pattern = r'Game Over! Final Score: (\d+)'
    matches = re.findall(pattern, text)
    return [int(s) for s in matches]

def extract_training_stats(text):
    """Extract training statistics"""
    stats = {}

    # Extract timesteps
    timestep_match = re.search(r'total_timesteps\s*\|\s*(\d+)', text)
    if timestep_match:
        stats['timesteps'] = int(timestep_match.group(1))

    # Extract episode stats
    ep_len_match = re.search(r'ep_len_mean\s*\|\s*([\d.]+)', text)
    if ep_len_match:
        stats['avg_episode_length'] = float(ep_len_match.group(1))

    ep_rew_match = re.search(r'ep_rew_mean\s*\|\s*([\d.]+)', text)
    if ep_rew_match:
        stats['avg_reward'] = float(ep_rew_match.group(1))

    return stats

def monitor_training_log():
    """Monitor training from tensorboard logs"""
    import os

    # Read most recent training output
    tensorboard_dir = "./tensorboard/"
    if os.path.exists(tensorboard_dir):
        print("="*60)
        print("TRAINING PROGRESS MONITOR")
        print("="*60)

        # Get latest log file
        files = []
        for root, dirs, filenames in os.walk(tensorboard_dir):
            for f in filenames:
                if f.startswith("events.out"):
                    files.append(os.path.join(root, f))

        if files:
            latest_file = max(files, key=os.path.getmtime)
            print(f"Monitoring: {latest_file}")
            print("="*60)

    # For now, just show simple stats
    print("\nTo view detailed training progress:")
    print("  tensorboard --logdir=./tensorboard/")
    print("\nOr check the background process output in Claude")
    print("\nCurrent status: Training is running in background")
    print("Target: 25,940 points")
    print("="*60)

if __name__ == "__main__":
    monitor_training_log()
