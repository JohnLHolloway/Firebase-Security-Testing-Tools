import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from selenium_stealth import stealth
import os
import sys


class GameController:
    """Controller for interacting with the Space Invaders game on the website."""
    
    def __init__(self, headless=False):
        """Initialize the game controller with a browser instance."""
        self.url = "https://jordancota.site/"
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        
        # Additional options to make Chrome more stable
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-features=NetworkService")
        chrome_options.add_argument("--window-size=1200,800")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            
            print("Setting up Chrome driver...")
            driver_path = ChromeDriverManager().install()
            print(f"Using Chrome driver at: {driver_path}")
            
            # First try with Service
            try:
                self.driver = webdriver.Chrome(
                    service=Service(driver_path),
                    options=chrome_options
                )
            except Exception as e:
                print(f"Error with Service approach: {e}")
                # Try without Service
                self.driver = webdriver.Chrome(
                    options=chrome_options
                )
            
            # If we got here, we have a driver
            print("Chrome browser initialized successfully!")
            
            # Apply stealth measures to avoid detection if available
            try:
                stealth(
                    self.driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True
                )
                print("Stealth measures applied")
            except Exception as e:
                print(f"Could not apply stealth (non-critical): {e}")
                
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            print("Please make sure Chrome is installed on your system.")
            print("Trying Firefox as fallback...")
            
            try:
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                from selenium.webdriver.firefox.service import Service as FirefoxService
                from webdriver_manager.firefox import GeckoDriverManager
                
                firefox_options = FirefoxOptions()
                if headless:
                    firefox_options.add_argument("--headless")
                    
                self.driver = webdriver.Firefox(
                    service=FirefoxService(GeckoDriverManager().install()),
                    options=firefox_options
                )
                print("Firefox browser initialized as fallback!")
            except Exception as e2:
                print(f"Failed to initialize Firefox as well: {e2}")
                print("Could not initialize any supported browser.")
                sys.exit(1)
        self.driver.set_window_size(1200, 800)
        self.game_active = False
        self.lives = 3
        self.score = 0
        self.high_score = 0
    
    def start_game(self):
        """Load the website and start the game."""
        print(f"Loading website: {self.url}")
        self.driver.get(self.url)
        time.sleep(5)  # Longer wait for page to fully load
        
        # Print the current page title to debug
        print(f"Page title: {self.driver.title}")
        
        try:
            # Try multiple selector approaches to find the start button
            selectors = [
                "button.start-button",
                "button[class*='start']",
                "button:contains('Start')",
                "button",
                ".start-button",
                "[class*='start']"
            ]
            
            start_button = None
            for selector in selectors:
                print(f"Trying to find start button with selector: {selector}")
                try:
                    if selector.endswith("contains('Start')"):
                        # Special case for text content
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            if "start" in button.text.lower():
                                start_button = button
                                break
                    else:
                        start_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    if start_button:
                        print(f"Found start button using selector: {selector}")
                        break
                except Exception:
                    continue
            
            if start_button:
                print("Clicking start button...")
                start_button.click()
                self.game_active = True
                time.sleep(2)  # Wait for game to initialize
                self.read_high_score()
                print("Game started successfully!")
                return True
            else:
                # As a fallback, try to press ENTER key
                print("Could not find start button, pressing ENTER key as fallback...")
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
                time.sleep(1)
                self.game_active = True
                self.read_high_score()
                return True
                
        except Exception as e:
            print(f"Error starting game: {e}")
            print("Taking screenshot for debugging...")
            try:
                self.driver.save_screenshot("game_start_error.png")
                print("Screenshot saved as 'game_start_error.png'")
            except:
                pass
            return False
    
    def read_high_score(self):
        """Read the current high score from the game."""
        try:
            high_score_element = self.driver.find_element(By.CSS_SELECTOR, ".high-score")
            if high_score_element:
                high_score_text = high_score_element.text
                # Extract numeric value using regex
                match = re.search(r'\d+', high_score_text)
                if match:
                    self.high_score = int(match.group())
                    print(f"Current high score: {self.high_score}")
        except Exception as e:
            print(f"Could not read high score: {e}")
    
    def move_left(self):
        """Press the left arrow key to move left."""
        if self.game_active:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_LEFT)
    
    def move_right(self):
        """Press the right arrow key to move right."""
        if self.game_active:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_RIGHT)
    
    def shoot(self):
        """Press the space bar to shoot."""
        if self.game_active:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SPACE)
    
    def get_screenshot(self):
        """Take a screenshot of the current game state."""
        if not self.game_active:
            return None
        
        try:
            # First check for and dismiss any alerts
            try:
                alert = self.driver.switch_to.alert
                print(f"Alert detected: {alert.text}")
                alert.accept()  # Accept the alert
                print("Alert accepted")
                time.sleep(0.5)  # Wait for alert to be dismissed
            except Exception:
                # No alert present, which is fine
                pass
                
            return self.driver.get_screenshot_as_png()
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None
    
    def get_current_score(self):
        """Read the current score from the game."""
        try:
            score_element = self.driver.find_element(By.CSS_SELECTOR, ".score")
            if score_element:
                score_text = score_element.text
                # Extract numeric value using regex
                match = re.search(r'\d+', score_text)
                if match:
                    self.score = int(match.group())
                    return self.score
        except Exception:
            pass
        return self.score
    
    def get_lives(self):
        """Read the current number of lives from the game."""
        try:
            lives_element = self.driver.find_element(By.CSS_SELECTOR, ".lives")
            if lives_element:
                lives_text = lives_element.text
                # Extract numeric value using regex
                match = re.search(r'\d+', lives_text)
                if match:
                    self.lives = int(match.group())
                    return self.lives
        except Exception:
            pass
        return self.lives
    
    def check_game_over(self):
        """Check if the game is over by looking for the game over screen."""
        try:
            game_over = self.driver.find_element(By.CSS_SELECTOR, ".game-over")
            if game_over and game_over.is_displayed():
                self.game_active = False
                return True
        except Exception:
            pass
        
        # Also check if lives are 0
        if self.get_lives() <= 0:
            self.game_active = False
            return True
            
        return False
    
    def restart_game(self):
        """Restart the game after game over."""
        if not self.game_active:
            try:
                restart_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.restart-button"))
                )
                restart_button.click()
                self.game_active = True
                self.lives = 3
                self.score = 0
                time.sleep(1)
                return True
            except Exception as e:
                print(f"Error restarting game: {e}")
                return False
    
    def enter_high_score(self, name):
        """Enter a name for the high score if prompted."""
        try:
            input_field = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.high-score-input"))
            )
            input_field.clear()
            input_field.send_keys(name)
            
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button.submit-score")
            submit_button.click()
            return True
        except Exception as e:
            print(f"Error entering high score: {e}")
            return False
    
    def close(self):
        """Close the browser and clean up."""
        if self.driver:
            self.driver.quit()
