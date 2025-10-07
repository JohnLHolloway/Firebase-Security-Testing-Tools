import gym
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from PIL import Image
from io import BytesIO

class SpaceInvadersEnv(gym.Env):
    def __init__(self):
        super(SpaceInvadersEnv, self).__init__()
        self.action_space = gym.spaces.Discrete(3)  # 0: left, 1: right, 2: shoot
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=(84, 84, 3), dtype=np.uint8)
        
        # Set up Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode for training
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        self.driver.get("https://jordancota.site/")
        time.sleep(5)  # Wait for page to load
        
        self.high_score = self.get_high_score()
        self.current_score = 0
        self.lives = 3
        self.prev_score = 0
        self.prev_lives = 3
        
    def get_high_score(self):
        # Placeholder: adjust based on actual site structure
        try:
            # Assume high score is in an element with id 'highscore'
            return int(self.driver.find_element(By.ID, 'highscore').text)
        except:
            return 0
    
    def reset(self):
        self.driver.refresh()
        time.sleep(2)
        self.current_score = 0
        self.lives = 3
        self.prev_score = 0
        self.prev_lives = 3
        
        obs = self.get_observation()
        return obs
    
    def step(self, action):
        if action == 0:
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_LEFT)
        elif action == 1:
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_RIGHT)
        elif action == 2:
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.SPACE)
        
        time.sleep(0.1)  # Small delay for action
        
        obs = self.get_observation()
        self.current_score = self.get_score()
        self.lives = self.get_lives()
        
        reward = self.current_score - self.prev_score
        if self.lives < self.prev_lives:
            reward -= 100  # Penalty for losing a life
        self.prev_score = self.current_score
        self.prev_lives = self.lives
        
        done = self.lives <= 0 or self.is_game_over()
        
        return obs, reward, done, {}
    
    def get_observation(self):
        screenshot = self.driver.get_screenshot_as_png()
        img = Image.open(BytesIO(screenshot))
        img = img.resize((84, 84))
        obs = np.array(img)
        return obs
    
    def get_score(self):
        # Placeholder: adjust based on actual site
        try:
            return int(self.driver.find_element(By.ID, 'score').text)
        except:
            return self.prev_score
    
    def get_lives(self):
        # Placeholder
        try:
            return int(self.driver.find_element(By.ID, 'lives').text)
        except:
            return 3
    
    def is_game_over(self):
        # Placeholder
        try:
            self.driver.find_element(By.ID, 'gameover')
            return True
        except:
            return False
    
    def close(self):
        self.driver.quit()