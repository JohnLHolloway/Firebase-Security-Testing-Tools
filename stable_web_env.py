"""
Stable Web Environment - Refined for Reliability
Handles browser issues and provides robust game interaction
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO
import cv2
import re
import os

class StableWebSpaceInvadersEnv(gym.Env):
    """Stable web environment with robust error handling"""

    def __init__(self, headless=True, max_retries=3):
        super(StableWebSpaceInvadersEnv, self).__init__()

        # Action space: 0=Left, 1=Right, 2=Shoot, 3=No-op
        self.action_space = spaces.Discrete(4)

        # Observation space: 84x84 RGB image
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(84, 84, 3), dtype=np.uint8
        )

        self.driver = None
        self.canvas = None
        self.headless = headless
        self.max_retries = max_retries
        self.episode_score = 0
        self.last_score = 0
        self.steps_taken = 0
        self.max_steps = 1500  # Shorter episodes for stability
        self.game_started = False
        self.retry_count = 0

        # Setup browser
        self.setup_browser()

    def setup_browser(self):
        """Setup Chrome browser with stability options"""
        print("🌐 Setting up stable Chrome browser...")

        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        if self.headless:
            options.add_argument('--headless')

        # Try different Chrome paths
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser"
        ]

        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                options.binary_location = chrome_path
                break

        try:
            # Try direct Chrome first
            self.driver = webdriver.Chrome(options=options)
            print("✅ Direct Chrome connection successful")
        except Exception as e:
            print(f"Direct Chrome failed: {e}")
            try:
                # Fallback to webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                print("✅ WebDriver Manager fallback successful")
            except Exception as e2:
                print(f"❌ All browser setup methods failed: {e2}")
                return False

        try:
            # Hide automation detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Navigate to game
            print("📱 Opening jordancota.site...")
            self.driver.get("https://jordancota.site/")
            time.sleep(3)

            # Scroll to game section
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
            time.sleep(2)

            print("✅ Browser setup complete")
            return True

        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False

    def find_game_elements(self):
        """Find and validate game elements"""
        try:
            # Find canvas
            canvases = self.driver.find_elements(By.TAG_NAME, "canvas")
            if canvases:
                self.canvas = canvases[0]
                print("✅ Canvas found")
            else:
                print("❌ No canvas found")
                return False

            # Check if game is loaded
            page_source = self.driver.page_source.lower()
            if 'space invaders' not in page_source and 'game' not in page_source:
                print("❌ Game content not found on page")
                return False

            return True

        except Exception as e:
            print(f"❌ Element detection failed: {e}")
            return False

    def start_game_safe(self):
        """Safely start the game with multiple attempts"""
        for attempt in range(3):
            try:
                print(f"🎮 Starting game (attempt {attempt + 1}/3)...")

                # Ensure canvas is focused
                if self.canvas:
                    self.canvas.click()
                    time.sleep(0.5)

                # Try start button
                try:
                    start_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Start')]")
                    for button in start_buttons:
                        if 'start' in button.text.lower():
                            button.click()
                            time.sleep(1)
                            break
                except:
                    pass

                # Press space to start
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.SPACE)
                actions.perform()
                time.sleep(1)

                # Verify game started by checking for score
                initial_score = self.get_score()
                if initial_score >= 0:  # Game should show score
                    print(f"✅ Game started (initial score: {initial_score})")
                    return True

            except Exception as e:
                print(f"Start attempt {attempt + 1} failed: {e}")
                time.sleep(1)

        print("❌ Failed to start game after 3 attempts")
        return False

    def dismiss_alert(self):
        """Dismiss any alert popups"""
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
        except:
            pass

    def get_observation(self):
        """Get stable game screenshot"""
        try:
            # Dismiss any alerts first
            self.dismiss_alert()

            if not self.canvas:
                return np.zeros((84, 84, 3), dtype=np.uint8)

            # Get canvas location and size
            location = self.canvas.location
            size = self.canvas.size

            # Take screenshot
            screenshot = self.driver.get_screenshot_as_png()
            img = Image.open(BytesIO(screenshot))

            # Crop to canvas area with padding
            left = max(0, location['x'] - 5)
            top = max(0, location['y'] - 5)
            right = min(img.width, left + size['width'] + 10)
            bottom = min(img.height, top + size['height'] + 10)

            if right > left and bottom > top:
                canvas_img = img.crop((left, top, right, bottom))

                # Convert to numpy array
                img_array = np.array(canvas_img)

                # Handle different image formats
                if len(img_array.shape) == 2:
                    # Grayscale to RGB
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
                elif img_array.shape[2] == 4:
                    # RGBA to RGB
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)

                # Resize to model input size
                resized = cv2.resize(img_array, (84, 84))
                return resized.astype(np.uint8)
            else:
                return np.zeros((84, 84, 3), dtype=np.uint8)

        except Exception as e:
            print(f"Screenshot error: {e}")
            return np.zeros((84, 84, 3), dtype=np.uint8)

    def take_action_safe(self, action):
        """Execute action with error handling"""
        try:
            # Dismiss any alerts first
            self.dismiss_alert()

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
            # action == 3 is no-op

            actions.perform()

        except Exception as e:
            print(f"Action error: {e}")

    def get_score(self):
        """Extract score from page with multiple methods"""
        try:
            # Dismiss any alerts first
            self.dismiss_alert()

            page_source = self.driver.page_source

            # Method 1: Look for "Score: XXX" pattern
            score_match = re.search(r'Score:\s*(\d+)', page_source)
            if score_match:
                return int(score_match.group(1))

            # Method 2: Look for score in various formats
            score_patterns = [
                r'score:\s*(\d+)',
                r'Score\s*(\d+)',
                r'(\d+)\s*pts',
                r'(\d+)\s*points'
            ]

            for pattern in score_patterns:
                match = re.search(pattern, page_source, re.IGNORECASE)
                if match:
                    return int(match.group(1))

            # Method 3: Look for large numbers that could be scores
            numbers = re.findall(r'\b(\d{3,6})\b', page_source)
            if numbers:
                # Filter reasonable score ranges
                scores = [int(n) for n in numbers if 0 <= int(n) <= 100000]
                if scores:
                    return max(scores)  # Take highest number as current score

        except Exception as e:
            print(f"Score extraction error: {e}")

        return 0

    def is_game_over(self):
        """Check if game is over by monitoring actual game state"""
        try:
            # Check if gameRunning variable is false in JavaScript
            game_running = self.driver.execute_script("return typeof gameRunning !== 'undefined' ? gameRunning : true;")

            if game_running is False:
                print("Game over detected: gameRunning = false")
                return True

            # Check lives from the page display (not just text search)
            try:
                lives_text = self.driver.execute_script("return typeof lives !== 'undefined' ? lives : 3;")
                if lives_text is not None and lives_text <= 0:
                    print(f"Game over detected: lives = {lives_text}")
                    return True
            except:
                pass

            # Check if score hasn't changed for too long (stuck detection)
            # Only check after enough steps and be more lenient
            if self.steps_taken > 200 and self.episode_score == self.last_score == 0:
                print(f"Game appears stuck: {self.steps_taken} steps, score still 0")
                return True

        except Exception:
            # Don't end game on errors - just log them
            pass

        return False

    def reset(self, seed=None, options=None):
        """Reset environment with retry logic"""
        # Handle seed parameter for gymnasium compatibility
        if seed is not None:
            np.random.seed(seed)

        success = False
        for attempt in range(self.max_retries):
            try:
                print(f"🔄 Reset attempt {attempt + 1}/{self.max_retries}")

                # Refresh page
                self.driver.refresh()
                time.sleep(3)

                # Scroll to game
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
                time.sleep(2)

                # Find game elements
                if not self.find_game_elements():
                    continue

                # Start game
                if not self.start_game_safe():
                    continue

                # Reset episode variables
                self.episode_score = 0
                self.last_score = 0
                self.steps_taken = 0
                self.game_started = True

                # Get initial observation
                obs = self.get_observation()
                success = True
                print("✅ Environment reset successful")
                break

            except Exception as e:
                print(f"Reset attempt {attempt + 1} failed: {e}")
                time.sleep(2)

        if not success:
            print("❌ Environment reset failed after all retries")
            # Return blank observation as fallback
            obs = np.zeros((84, 84, 3), dtype=np.uint8)

        return obs, {}

    def step(self, action):
        """Execute step with error handling"""
        self.steps_taken += 1

        # Execute action
        self.take_action_safe(action)

        # Small delay for game to update
        time.sleep(0.08)

        # Get new observation
        obs = self.get_observation()

        # Get current score
        current_score = self.get_score()

        # Calculate reward
        score_reward = max(0, current_score - self.last_score)  # Only positive score changes
        time_penalty = -0.005  # Small penalty to encourage action
        alive_bonus = 0.05    # Bonus for staying alive

        reward = score_reward + time_penalty + alive_bonus

        # Update tracking
        self.episode_score = max(self.episode_score, current_score)
        self.last_score = current_score

        # Check if episode is done
        done = False
        if self.is_game_over():
            done = True
            reward -= 5  # Penalty for dying
        elif self.steps_taken >= self.max_steps:
            done = True

        # Info for monitoring
        info = {
            'score': current_score,
            'episode_score': self.episode_score,
            'steps': self.steps_taken,
            'action': action
        }

        return obs, reward, done, False, info

    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                print("🔒 Browser closed")
            except:
                pass
        self.driver = None

def test_stable_env():
    """Test the stable environment"""
    print("🧪 Testing Stable Web Environment")

    env = StableWebSpaceInvadersEnv(headless=False)

    try:
        obs, _ = env.reset()
        print(f"✅ Reset successful, observation shape: {obs.shape}")

        # Take a few test actions
        for i in range(5):
            action = env.action_space.sample()
            obs, reward, done, _, info = env.step(action)

            action_names = ['LEFT', 'RIGHT', 'SHOOT', 'NO-OP']
            print(f"Step {i+1}: Action={action_names[action]}, Reward={reward:.3f}, Score={info['score']}, Done={done}")

            if done:
                print("Episode ended")
                break

        print("✅ Environment test completed")

    except Exception as e:
        print(f"❌ Environment test failed: {e}")
    finally:
        env.close()

if __name__ == "__main__":
    test_stable_env()