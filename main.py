from stable_baselines3 import PPO
from advanced_env import AdvancedSpaceInvadersEnv
import requests
from bs4 import BeautifulSoup
import re
import os

def get_current_high_score():
    """Scrape the current high score from the website"""
    try:
        response = requests.get("https://jordancota.site/")
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find the high scores section
        page_text = response.text
        scores = re.findall(r'(\d+) \(Level \d+\)', page_text)
        if scores:
            return max(int(score) for score in scores)
    except Exception as e:
        print(f"Error fetching high score: {e}")
    return 25940  # Current known high score

def evaluate_agent(model_path, episodes=3):
    """Evaluate the trained agent with multiple episodes"""
    if not os.path.exists(model_path):
        print(f"Model file {model_path} not found!")
        return 0
        
    model = PPO.load(model_path)
    scores = []
    
    for episode in range(episodes):
        print(f"Running evaluation episode {episode + 1}/{episodes}")
        env = AdvancedSpaceInvadersEnv(headless=False)  # Show browser for evaluation
        
        obs, _ = env.reset()
        episode_score = 0
        done = False
        step = 0
        max_steps = 2000
        
        while not done and step < max_steps:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, _, info = env.step(action)
            current_score = info.get('score', 0)
            episode_score = max(episode_score, current_score)
            step += 1
            
            if step % 100 == 0:
                print(f"Step {step}, Score: {current_score}, Lives: {info.get('lives', 0)}")
        
        scores.append(episode_score)
        print(f"Episode {episode + 1} final score: {episode_score}")
        env.close()
    
    return max(scores) if scores else 0

def submit_high_score_to_site(score, name):
    """Attempt to submit high score to the website"""
    env = AdvancedSpaceInvadersEnv(headless=False)
    try:
        success = env.submit_high_score(name)
        if success:
            print(f"Successfully submitted high score of {score} for {name}!")
        else:
            print(f"Could not automatically submit. Please manually enter:")
            print(f"Name: {name}")
            print(f"Score: {score}")
            print("Visit https://jordancota.site/ to submit manually if prompted.")
    finally:
        env.close()

def main():
    print("=== Advanced Space Invaders ML Agent ===")
    
    # Check for available models (updated paths)
    model_paths = [
        "models/working_error_backup.zip",  # Best model (450 points)
        "models/space_invaders_ppo.zip",
        "models/error_backup_model.zip"
    ]
    
    model_path = None
    for path in model_paths:
        if os.path.exists(path):
            model_path = path
            break
    
    if not model_path:
        print("No trained model found! Please run training first.")
        print("Available options:")
        print("1. Run: py advanced_agent.py  (for advanced training)")
        print("2. Run: py train.py  (for basic training)")
        return
    
    print(f"Using model: {model_path}")
    current_high = get_current_high_score()
    print(f"Current website high score: {current_high}")

    print("\nEvaluating agent performance...")
    agent_score = evaluate_agent(model_path, episodes=2)
    print(f"\nAgent's best score: {agent_score}")

    if agent_score > current_high:
        print("🎉 CONGRATULATIONS! NEW HIGH SCORE! 🎉")
        print(f"Your AI beat the current high score of {current_high}!")
        
        # Use "John H" as requested
        name = "John H"
        print(f"Submitting score for: {name}")
        submit_high_score_to_site(agent_score, name)
    else:
        print(f"Agent scored {agent_score}, which is below the current high score of {current_high}")
        print("Keep training to improve performance!")
        
        if agent_score == 0:
            print("\nTroubleshooting tips:")
            print("- Check if the website is accessible")
            print("- Try running with headless=False to see what's happening")
            print("- The model might need more training")

if __name__ == "__main__":
    main()
