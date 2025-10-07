"""
Web-Based Space Invaders Environment
Trains directly on jordancota.site for perfect compatibility
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from io import BytesIO
import cv2
import re

class WebSpaceInvadersEnv(gym.Env):
    """OpenAI Gym environment for Space Invaders on jordancota.site"""
    
    def __init__(self, headless=True):
        super(WebSpaceInvadersEnv, self).__init__()
        
        # Action space: 0=Left, 1=Right, 2=Shoot, 3=No-op
        self.action_space = spaces.Discrete(4)
        
        # Observation space: 84x84 RGB image
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(84, 84, 3), dtype=np.uint8
        )
        
        self.driver = None
        self.canvas = None
        self.headless = headless
        self.episode_score = 0
        self.last_score = 0
        self.steps_taken = 0
        self.max_steps = 2000
        self.game_started = False
        
        # Performance tracking
        self.setup_browser()
    
    def setup_browser(self):
        """Initialize browser and navigate to game"""
        print("🌐 Setting up web browser...")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if self.headless:
            options.add_argument('--headless')
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            
            # Hide automation detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to game
            self.driver.get("https://jordancota.site/")
            time.sleep(2)
            
            # Scroll to game section
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
            time.sleep(1)
            
            print("✅ Browser setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            return False
    
    def start_game(self):
        """Start a new game on the website"""
        try:
            # Find canvas
            canvases = self.driver.find_elements(By.TAG_NAME, "canvas")
            if canvases:
                self.canvas = canvases[0]
            else:
                print("❌ No canvas found")
                return False
            
            # Click start button if exists
            try:
                start_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Start Game')]")
                start_button.click()
                time.sleep(1)
            except:
                pass  # Start button might not exist
            
            # Click canvas to focus and start
            self.canvas.click()
            time.sleep(0.5)
            
            # Press space to ensure game starts
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.SPACE)
            actions.perform()
            time.sleep(1)
            
            self.game_started = True
            print("✅ Game started")
            return True
            
        except Exception as e:
            print(f"❌ Could not start game: {e}")
            return False
    
    def get_observation(self):
        """Get current game screen as observation"""
        try:
            if self.canvas:
                # Get canvas screenshot
                location = self.canvas.location
                size = self.canvas.size
                
                screenshot = self.driver.get_screenshot_as_png()
                img = Image.open(BytesIO(screenshot))
                
                # Crop to canvas area
                left = location['x']
                top = location['y']
                right = left + size['width']
                bottom = top + size['height']
                
                canvas_img = img.crop((left, top, right, bottom))
                img_array = np.array(canvas_img)
                
                # Convert RGBA to RGB if needed
                if img_array.shape[2] == 4:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
                
                # Resize to standard size
                resized = cv2.resize(img_array, (84, 84))
                return resized.astype(np.uint8)
            
        except Exception as e:
            print(f"Screenshot error: {e}")
        
        # Return black screen as fallback
        return np.zeros((84, 84, 3), dtype=np.uint8)
    
    def get_score(self):
        """Extract current score from webpage"""
        try:
            page_source = self.driver.page_source
            
            # Look for score patterns
            score_patterns = [
                r'Score:\s*(\d+)',
                r'score:\s*(\d+)',
                r'Score\s*(\d+)'
            ]
            
            for pattern in score_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    return int(matches[-1])
                    
        except Exception as e:
            print(f"Score extraction error: {e}")
        
        return 0
    
    def is_game_over(self):
        """Check if game is over"""
        try:
            page_source = self.driver.page_source.lower()
            game_over_indicators = [
                'game over',
                'gameover',
                'game ended'
            ]
            
            for indicator in game_over_indicators:
                if indicator in page_source:
                    return True
                    
            # Also check if lives are 0 (if visible)
            if 'lives: 0' in page_source:
                return True
                
        except:
            pass
        
        return False
    
    def take_action(self, action):
        """Execute action in the web game"""
        try:
            # Ensure canvas is focused
            if self.canvas:
                self.canvas.click()
            
            actions = ActionChains(self.driver)
            
            if action == 0:  # Left
                actions.key_down(Keys.ARROW_LEFT)
                actions.pause(0.05)
                actions.key_up(Keys.ARROW_LEFT)
            elif action == 1:  # Right
                actions.key_down(Keys.ARROW_RIGHT)
                actions.pause(0.05)
                actions.key_up(Keys.ARROW_RIGHT)
            elif action == 2:  # Shoot
                actions.key_down(Keys.SPACE)
                actions.pause(0.05)
                actions.key_up(Keys.SPACE)
            # action == 3 is no-op (do nothing)
            
            actions.perform()
            
        except Exception as e:
            print(f"Action execution error: {e}")
    
    def reset(self, seed=None, options=None):
        """Reset environment for new episode"""
        # Handle seed parameter for gymnasium compatibility
        if seed is not None:
            np.random.seed(seed)
        
        if not self.driver:
            self.setup_browser()
        
        # Refresh page to reset game
        self.driver.refresh()
        time.sleep(2)
        
        # Scroll to game
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
        time.sleep(1)
        
        # Start new game
        if not self.start_game():
            print("❌ Could not reset game")
        
        # Reset episode variables
        self.episode_score = 0
        self.last_score = 0
        self.steps_taken = 0
        
        # Get initial observation
        obs = self.get_observation()
        return obs, {}
    
    def step(self, action):
        """Execute one step in the environment"""
        self.steps_taken += 1
        
        # Execute action
        self.take_action(action)
        
        # Small delay to let game update
        time.sleep(0.1)
        
        # Get new observation
        obs = self.get_observation()
        
        # Get current score
        current_score = self.get_score()
        
        # Calculate reward
        score_reward = current_score - self.last_score
        
        # Small penalty for time to encourage action
        time_penalty = -0.01
        
        # Bonus for staying alive
        alive_bonus = 0.1
        
        reward = score_reward + time_penalty + alive_bonus
        
        # Update tracking
        self.episode_score = max(self.episode_score, current_score)
        self.last_score = current_score
        
        # Check if episode is done
        done = False
        if self.is_game_over():
            done = True
            reward -= 10  # Penalty for dying
        elif self.steps_taken >= self.max_steps:
            done = True
        
        # Info for monitoring
        info = {
            'score': current_score,
            'episode_score': self.episode_score,
            'steps': self.steps_taken,
            'lives': 3  # Default, could extract if visible
        }
        
        return obs, reward, done, False, info
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
        print("🔒 Environment closed")

def test_environment():
    """Test the web environment"""
    print("🧪 Testing Web Environment...")
    
    env = WebSpaceInvadersEnv(headless=False)
    
    try:
        obs, _ = env.reset()
        print(f"✅ Reset successful, observation shape: {obs.shape}")
        
        # Take a few random actions
        for i in range(10):
            action = env.action_space.sample()
            obs, reward, done, _, info = env.step(action)
            
            action_names = ['LEFT', 'RIGHT', 'SHOOT', 'NO-OP']
            print(f"Step {i+1}: Action={action_names[action]}, Reward={reward:.2f}, Score={info['score']}, Done={done}")
            
            if done:
                print("Episode ended!")
                break
        
        print("✅ Environment test completed!")
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
    finally:
        env.close()

if __name__ == "__main__":
    test_environment()