"""
Evaluation and Submission System
Robust evaluation with automatic high score submission
"""
import time
import numpy as np
from stable_baselines3 import PPO
from stable_web_env import StableWebSpaceInvadersEnv
from get_high_score import get_current_high_score, get_high_score_info
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

class ModelEvaluator:
    """Evaluates models and handles high score submission"""

    def __init__(self, headless=True):
        self.headless = headless
        self.env = None
        self.driver = None

    def setup_evaluation_env(self):
        """Setup environment for evaluation"""
        self.env = StableWebSpaceInvadersEnv(headless=self.headless)

    def evaluate_model(self, model_path, num_episodes=20, max_steps_per_episode=2000):
        """Evaluate model performance"""
        print(f"📊 Evaluating model: {model_path}")

        if not self.env:
            self.setup_evaluation_env()

        try:
            model = PPO.load(model_path)
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return None

        scores = []
        episode_lengths = []
        victories = 0

        target_score = get_current_high_score()
        print(f"🎯 Target high score: {target_score}")

        for episode in range(num_episodes):
            print(f"🎮 Episode {episode + 1}/{num_episodes}")

            obs, _ = self.env.reset()
            episode_score = 0
            steps = 0
            done = False

            while not done and steps < max_steps_per_episode:
                # Get action from model
                action, _ = model.predict(obs, deterministic=True)

                # Step environment
                obs, reward, done, _, info = self.env.step(action)

                # Track score
                current_score = info.get('score', 0)
                episode_score = max(episode_score, current_score)
                steps += 1

                # Small delay to not overwhelm
                time.sleep(0.02)

            scores.append(episode_score)
            episode_lengths.append(steps)

            if episode_score >= target_score:
                victories += 1
                print(f"🏆 VICTORY! Score: {episode_score} >= {target_score}")
            else:
                print(f"Score: {episode_score}")

        # Calculate statistics
        avg_score = np.mean(scores)
        max_score = max(scores)
        min_score = min(scores)
        std_score = np.std(scores)
        win_rate = victories / num_episodes * 100

        results = {
            'average_score': avg_score,
            'max_score': max_score,
            'min_score': min_score,
            'std_score': std_score,
            'win_rate': win_rate,
            'victories': victories,
            'total_episodes': num_episodes,
            'target_score': target_score,
            'all_scores': scores
        }

        print("📈 Evaluation Results:")
        print(f"   Average Score: {avg_score:.1f} ± {std_score:.1f}")
        print(f"   Max Score: {max_score}")
        print(f"   Min Score: {min_score}")
        print(f"   Win Rate: {win_rate:.1f}% ({victories}/{num_episodes})")
        print(f"   Target: {target_score}")

        return results

    def find_best_model(self, model_dir="models"):
        """Find the best performing model"""
        import os

        model_files = [f for f in os.listdir(model_dir) if f.endswith('.zip')]
        if not model_files:
            print("❌ No models found")
            return None

        best_model = None
        best_score = 0

        print("🔍 Evaluating all models...")

        for model_file in model_files:
            model_path = os.path.join(model_dir, model_file)
            print(f"Testing {model_file}...")

            try:
                results = self.evaluate_model(model_path, num_episodes=5)  # Quick test
                if results and results['max_score'] > best_score:
                    best_score = results['max_score']
                    best_model = model_path
                    print(f"   New best: {best_score}")
            except Exception as e:
                print(f"   Failed: {e}")

        print(f"🏆 Best model: {best_model} (score: {best_score})")
        return best_model

    def submit_high_score(self, score, player_name="John H"):
        """Submit high score to website"""
        print(f"📤 Attempting to submit score: {score} as '{player_name}'")

        # Setup browser for submission
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        if self.headless:
            options.add_argument('--headless')

        try:
            driver = webdriver.Chrome(options=options)
            driver.get("https://jordancota.site/")
            time.sleep(3)

            # Scroll to game section
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
            time.sleep(2)

            # Look for score submission form
            # This will need to be adapted based on the actual website structure
            try:
                # Try to find input fields
                inputs = driver.find_elements(By.TAG_NAME, "input")
                name_input = None
                score_input = None

                for inp in inputs:
                    inp_type = inp.get_attribute("type")
                    inp_name = inp.get_attribute("name") or ""
                    inp_placeholder = inp.get_attribute("placeholder") or ""

                    if inp_type == "text" and ("name" in inp_name.lower() or "name" in inp_placeholder.lower()):
                        name_input = inp
                    elif inp_type in ["number", "text"] and ("score" in inp_name.lower() or "score" in inp_placeholder.lower()):
                        score_input = inp

                if name_input and score_input:
                    # Fill form
                    name_input.clear()
                    name_input.send_keys(player_name)

                    score_input.clear()
                    score_input.send_keys(str(score))

                    # Look for submit button
                    submit_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Submit')]")
                    if submit_buttons:
                        submit_buttons[0].click()
                        print("✅ Score submitted successfully")
                        time.sleep(2)
                        return True
                    else:
                        # Try input type submit
                        submit_inputs = driver.find_elements(By.XPATH, "//input[@type='submit']")
                        if submit_inputs:
                            submit_inputs[0].click()
                            print("✅ Score submitted successfully")
                            time.sleep(2)
                            return True

                print("❌ Could not find submission form elements")

            except Exception as e:
                print(f"❌ Submission failed: {e}")

            driver.quit()
            return False

        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            return False

    def run_full_evaluation(self, model_path=None):
        """Run complete evaluation and submission pipeline"""
        print("🚀 Starting Full Evaluation Pipeline")

        # Find best model if not specified
        if not model_path:
            model_path = self.find_best_model()
            if not model_path:
                return False

        # Detailed evaluation
        results = self.evaluate_model(model_path, num_episodes=30)

        if not results:
            print("❌ Evaluation failed")
            return False

        # Check if we beat the high score
        target_score = results['target_score']
        max_achieved = results['max_score']

        if max_achieved >= target_score:
            print(f"🎉 SUCCESS! Beat high score {target_score} with {max_achieved}")

            # Submit the score
            success = self.submit_high_score(max_achieved)
            if success:
                print("✅ High score submitted successfully!")
                return True
            else:
                print("❌ High score submission failed")
                return False
        else:
            print(f"❌ Did not beat high score. Best: {max_achieved}, Target: {target_score}")
            return False

    def cleanup(self):
        """Clean up resources"""
        if self.env:
            self.env.close()
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

def main():
    """Main evaluation function"""
    import argparse

    parser = argparse.ArgumentParser(description='Space Invaders Model Evaluation')
    parser.add_argument('--model', type=str, help='Specific model to evaluate')
    parser.add_argument('--evaluate-only', action='store_true', help='Only evaluate, no submission')
    parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode')

    args = parser.parse_args()

    evaluator = ModelEvaluator(headless=args.headless)

    try:
        if args.evaluate_only:
            if args.model:
                results = evaluator.evaluate_model(args.model)
            else:
                evaluator.find_best_model()
        else:
            success = evaluator.run_full_evaluation(args.model)
            if success:
                print("🎊 Mission Accomplished!")
            else:
                print("💪 Keep training - victory is near!")

    finally:
        evaluator.cleanup()

if __name__ == "__main__":
    main()