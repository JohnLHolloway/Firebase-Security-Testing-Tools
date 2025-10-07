"""
Web Score Submission System
Handles high score submission to jordancota.site with "John H"
"""
import os
import time
from stable_baselines3 import PPO
from web_env import WebSpaceInvadersEnv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from get_high_score import get_current_high_score, get_high_score_info
import re

def submit_high_score_to_website(model_path, player_name="John H", play_episodes=3):
    """Play the game and submit high score if achieved"""
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return False
    
    # Get current high score target
    high_score_info = get_high_score_info()
    target_score = high_score_info['score']
    
    print(f"🤖 Loading model: {model_path}")
    print(f"👤 Player name: {player_name}")
    print(f"🏆 Current Leader: {high_score_info['name']} - {target_score:,} points")
    print(f"🎯 Target: Beat {target_score:,} points")
    print()
    
    model = PPO.load(model_path)
    env = WebSpaceInvadersEnv(headless=False)  # Visible so we can watch
    
    best_score = 0
    
    try:
        for episode in range(play_episodes):
            print(f"🎬 Episode {episode + 1}/{play_episodes}")
            
            obs, _ = env.reset()
            episode_score = 0
            steps = 0
            max_steps = 3000
            
            while steps < max_steps:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, done, _, info = env.step(action)
                
                episode_score = info['score']
                steps += 1
                
                # Log progress
                if steps % 200 == 0:
                    print(f"  Step {steps}: Score = {episode_score}")
                
                if done:
                    print(f"  Game Over at step {steps}")
                    break
            
            print(f"✅ Episode {episode + 1} Final Score: {episode_score}")
            best_score = max(best_score, episode_score)
            
            # Check if we beat the high score
            if episode_score > target_score:
                print(f"🎉 HIGH SCORE ACHIEVED! {episode_score} > {target_score:,}")
                
                # Try to submit the score
                success = attempt_score_submission(env, player_name, episode_score)
                
                if success:
                    print(f"✅ Score submitted successfully!")
                    return True
                else:
                    print(f"❌ Automatic submission failed")
                    print(f"📝 Manual submission needed:")
                    print(f"   Name: {player_name}")
                    print(f"   Score: {episode_score}")
                    print(f"   Website: https://jordancota.site/")
                    return False
        
        # Final results
        print(f"\n📊 FINAL RESULTS:")
        print(f"Best Score: {best_score:,}")
        print(f"Target: {target_score:,}")
        progress = (best_score / target_score) * 100
        print(f"Progress: {progress:.2f}%")
        
        if best_score <= target_score:
            print("🔄 High score not beaten. Continue training for better performance.")
        
        return best_score > target_score
        
    except Exception as e:
        print(f"❌ Error during gameplay: {e}")
        return False
    finally:
        input("Press Enter to close browser...")
        env.close()

def attempt_score_submission(env, player_name, score):
    """Attempt to submit score to the website"""
    
    print(f"🏆 Attempting to submit {score} for {player_name}...")
    
    try:
        # Wait for any game over screens
        time.sleep(5)
        
        # Look for name input field
        name_input_selectors = [
            "//input[@type='text']",
            "//input[@placeholder*='name' or @placeholder*='Name']",
            "//*[@id='name' or @id='playerName']",
            "//input[@class*='name']"
        ]
        
        name_input = None
        for selector in name_input_selectors:
            try:
                elements = env.driver.find_elements(By.XPATH, selector)
                if elements:
                    name_input = elements[0]
                    print(f"✅ Found name input field")
                    break
            except:
                continue
        
        if name_input:
            # Clear and enter name
            name_input.clear()
            name_input.send_keys(player_name)
            print(f"✅ Entered name: {player_name}")
            
            # Look for submit button
            submit_selectors = [
                "//button[contains(text(), 'Submit')]",
                "//input[@type='submit']",
                "//button[@type='submit']",
                "//*[@id='submit']"
            ]
            
            submitted = False
            for selector in submit_selectors:
                try:
                    elements = env.driver.find_elements(By.XPATH, selector)
                    if elements:
                        elements[0].click()
                        print("✅ Clicked submit button")
                        submitted = True
                        break
                except:
                    continue
            
            # If no submit button found, try pressing Enter
            if not submitted:
                name_input.send_keys(Keys.RETURN)
                print("✅ Pressed Enter to submit")
                submitted = True
            
            if submitted:
                time.sleep(3)  # Wait for submission to process
                return True
        
        else:
            print("❌ No name input field found")
            
            # Check if there's a high score prompt or form
            page_source = env.driver.page_source.lower()
            if any(phrase in page_source for phrase in ['high score', 'new record', 'enter name']):
                print("⚠️  High score form detected but couldn't interact with it")
                return False
            else:
                print("ℹ️  No high score submission form found")
                return False
    
    except Exception as e:
        print(f"❌ Submission error: {e}")
        return False

def main():
    print("🏆 WEB HIGH SCORE SUBMISSION SYSTEM")
    print("=" * 40)
    
    # Find available models
    model_dir = 'models'
    if not os.path.exists(model_dir):
        print("❌ No models directory found. Train a model first!")
        return
    
    models = [f for f in os.listdir(model_dir) if f.endswith('.zip')]
    if not models:
        print("❌ No trained models found. Train a model first!")
        return
    
    print("Available models:")
    for i, model in enumerate(models):
        print(f"{i+1}. {model}")
    
    try:
        choice = int(input("\nChoose model to test: ")) - 1
        if 0 <= choice < len(models):
            model_path = os.path.join(model_dir, models[choice])
            
            # Confirm player name
            player_name = input("Enter player name (default: John H): ").strip()
            if not player_name:
                player_name = "John H"
            
            print(f"\n🎮 Testing model: {models[choice]}")
            print(f"👤 Player name: {player_name}")
            
            success = submit_high_score_to_website(model_path, player_name)
            
            if success:
                print("🎉 HIGH SCORE SUBMITTED SUCCESSFULLY!")
            else:
                print("📝 Manual submission may be required")
        else:
            print("Invalid selection")
    except ValueError:
        print("Invalid input")

if __name__ == "__main__":
    main()