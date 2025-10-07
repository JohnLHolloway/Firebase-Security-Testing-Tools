from stable_baselines3 import PPO
from space_invaders_env import SpaceInvadersEnv

# Load the trained model
model = PPO.load("ppo_space_invaders")

# Create environment (not headless for testing)
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

class SpaceInvadersEnvTest(SpaceInvadersEnv):
    def __init__(self):
        super().__init__()
        # Override to not be headless
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Comment out for visible browser
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get("https://jordancota.site/")
        time.sleep(5)
        self.high_score = self.get_high_score()
        self.current_score = 0
        self.lives = 3
        self.prev_score = 0

env = SpaceInvadersEnvTest()

obs = env.reset()
done = False
total_reward = 0

while not done:
    action, _ = model.predict(obs)
    obs, reward, done, info = env.step(action)
    total_reward += reward

final_score = env.current_score
print(f"Final score: {final_score}")
print(f"High score: {env.high_score}")

if final_score > env.high_score:
    name = input("New high score! Enter your name: ")
    # If the site has a form, you can add code here to submit
    # For example:
    # env.driver.find_element(By.ID, 'name_input').send_keys(name)
    # env.driver.find_element(By.ID, 'submit').click()
    print(f"High score beaten by {name}")
else:
    print("Did not beat the high score.")

env.close()