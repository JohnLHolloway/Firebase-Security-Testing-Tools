"""
Simple Training - Direct Chrome without webdriver-manager
"""
import os
import time
from stable_baselines3 import PPO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
from PIL import Image
from io import BytesIO
import cv2
import gymnasium as gym
from gymnasium import spaces

class SimpleWebEnv(gym.Env):
    """Simplified web environment without webdriver-manager"""
    
    def __init__(self):
        super().__init__()
        
        self.action_space = spaces.Discrete(4)  # Left, Right, Shoot, No-op
        self.observation_space = spaces.Box(low=0, high=255, shape=(84, 84, 3), dtype=np.uint8)
        
        self.driver = None
        self.canvas = None
        self.episode_score = 0
        self.steps_taken = 0
        self.max_steps = 1000
        
        self.setup_browser()
    
    def setup_browser(self):
        """Setup browser with direct Chrome path"""
        print("🌐 Setting up Chrome browser...")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            # Try to use Chrome directly without webdriver-manager
            self.driver = webdriver.Chrome(options=options)
            
            print("📱 Opening jordancota.site...")
            self.driver.get("https://jordancota.site/")
            time.sleep(3)
            
            # Scroll to game
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
            time.sleep(1)
            
            print("✅ Browser setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            return False
    
    def start_game(self):
        """Start the game"""
        try:
            canvases = self.driver.find_elements(By.TAG_NAME, "canvas")
            if canvases:
                self.canvas = canvases[0]
                
                # Click start button if exists
                try:
                    start_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Start Game')]")
                    start_button.click()
                    time.sleep(1)
                except:
                    pass
                
                # Click canvas and press space
                self.canvas.click()
                time.sleep(0.5)
                
                actions = ActionChains(self.driver)
                actions.send_keys(" ")  # Space to start
                actions.perform()
                time.sleep(1)
                
                return True
        except Exception as e:
            print(f"Error starting game: {e}")
        
        return False
    
    def get_observation(self):
        """Get screenshot"""
        try:
            if self.canvas:
                location = self.canvas.location
                size = self.canvas.size
                
                screenshot = self.driver.get_screenshot_as_png()
                img = Image.open(BytesIO(screenshot))
                
                # Crop to canvas
                left = location['x']
                top = location['y']
                right = left + size['width']
                bottom = top + size['height']
                
                canvas_img = img.crop((left, top, right, bottom))
                img_array = np.array(canvas_img)
                
                if img_array.shape[2] == 4:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
                
                resized = cv2.resize(img_array, (84, 84))
                return resized.astype(np.uint8)
                
        except Exception as e:
            print(f"Screenshot error: {e}")
        
        return np.zeros((84, 84, 3), dtype=np.uint8)
    
    def take_action(self, action):
        """Execute action"""
        try:
            if self.canvas:
                self.canvas.click()
            
            actions = ActionChains(self.driver)
            
            if action == 0:  # Left
                actions.key_down("ArrowLeft").key_up("ArrowLeft")
            elif action == 1:  # Right
                actions.key_down("ArrowRight").key_up("ArrowRight")
            elif action == 2:  # Shoot
                actions.key_down(" ").key_up(" ")
            
            actions.perform()
            
        except Exception as e:
            print(f"Action error: {e}")
    
    def get_score(self):
        """Get current score"""
        try:
            page_source = self.driver.page_source
            import re
            scores = re.findall(r'Score:\s*(\d+)', page_source)
            if scores:
                return int(scores[-1])
        except:
            pass
        return 0
    
    def reset(self, seed=None, options=None):
        """Reset environment"""
        if not self.driver:
            self.setup_browser()
        
        self.driver.refresh()
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
        time.sleep(1)
        
        self.start_game()
        self.episode_score = 0
        self.steps_taken = 0
        
        obs = self.get_observation()
        return obs, {}
    
    def step(self, action):
        """Step environment"""
        self.steps_taken += 1
        
        self.take_action(action)
        time.sleep(0.1)
        
        obs = self.get_observation()
        current_score = self.get_score()
        
        reward = (current_score - self.episode_score) + 0.1  # Score increase + alive bonus
        
        self.episode_score = max(self.episode_score, current_score)
        
        done = (self.steps_taken >= self.max_steps)
        
        info = {'score': current_score, 'episode_score': self.episode_score}
        
        return obs, reward, done, False, info
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()

def simple_train():
    """Simple training without complex dependencies"""
    
    print("🚀 SIMPLE WEB TRAINING")
    print("Target: Beat 25,940 points")
    print()
    
    os.makedirs('models', exist_ok=True)
    
    try:
        env = SimpleWebEnv()
        
        print("🤖 Creating PPO model...")
        model = PPO("CnnPolicy", env, verbose=1, learning_rate=0.0003)
        
        print("🎮 Starting training...")
        
        best_score = 0
        
        for step in range(0, 20000, 2000):  # Train in 2K chunks
            print(f"📈 Training steps {step} to {step + 2000}...")
            
            model.learn(total_timesteps=2000, reset_num_timesteps=False)
            
            # Quick test
            obs, _ = env.reset()
            episode_score = 0
            
            for _ in range(200):  # Short test
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, done, _, info = env.step(action)
                episode_score = info['score']
                if done:
                    break
            
            if episode_score > best_score:
                best_score = episode_score
                model_path = f"models/simple_best_{best_score}.zip"
                model.save(model_path)
                print(f"🏆 NEW BEST! Score: {best_score}")
                
                if best_score > 25940:
                    print("🎉 HIGH SCORE BEATEN!")
                    break
            
            progress = (best_score / 25940) * 100
            print(f"Progress: {progress:.2f}%\n")
        
        print(f"✅ Training complete! Best score: {best_score}")
        
    except Exception as e:
        print(f"❌ Training error: {e}")
    finally:
        try:
            env.close()
        except:
            pass

if __name__ == "__main__":
    simple_train()