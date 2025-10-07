import cv2
import numpy as np
from PIL import Image
import io
import pytesseract
import time


class VisionSystem:
    """Vision system for processing game screenshots and detecting game elements."""
    
    def __init__(self):
        """Initialize the vision system with detection parameters."""
        # Set paths to templates if needed
        self.player_template = None
        self.enemy_template = None
        self.bullet_template = None
        
        # Detection parameters
        self.player_color = [0, 255, 0]  # Green
        self.enemy_color = [255, 0, 0]   # Red
        self.bullet_color = [255, 255, 255]  # White
        
        # Game area coordinates - these will need to be calibrated
        self.game_area = {
            'top': 200,
            'bottom': 700,
            'left': 300,
            'right': 900
        }
        
        # Configure pytesseract if needed for score reading
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def process_screenshot(self, screenshot_bytes):
        """Process the screenshot and extract game state."""
        # Convert screenshot bytes to an OpenCV image
        image = Image.open(io.BytesIO(screenshot_bytes))
        image_np = np.array(image)
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        
        # Crop to game area for better processing
        game_image = image_cv[
            self.game_area['top']:self.game_area['bottom'], 
            self.game_area['left']:self.game_area['right']
        ]
        
        # Extract game state
        player_position = self._detect_player(game_image)
        enemies = self._detect_enemies(game_image)
        bullets = self._detect_bullets(game_image)
        
        # Save processed image for debugging
        debug_image = self._draw_debug(game_image.copy(), player_position, enemies, bullets)
        cv2.imwrite('debug_vision.png', debug_image)
        
        return {
            'player_position': player_position,
            'enemies': enemies,
            'bullets': bullets,
            'player_bullets': [b for b in bullets if b['direction'] == 'up'],
            'enemy_bullets': [b for b in bullets if b['direction'] == 'down'],
            'raw_image': game_image
        }
    
    def _detect_player(self, image):
        """Detect the player's position in the image."""
        # Convert to HSV for better color filtering
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Green color range for player
        lower_green = np.array([40, 100, 100])
        upper_green = np.array([80, 255, 255])
        
        # Create mask and find contours
        mask = cv2.inRange(hsv, lower_green, upper_green)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find the largest contour (likely the player)
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Player position is the center bottom of the bounding box
            player_x = x + w // 2
            player_y = y + h
            
            return {'x': player_x, 'y': player_y, 'width': w}
        
        # If no player detected, return estimated position
        return {'x': image.shape[1] // 2, 'y': image.shape[0] - 50, 'width': 30}
    
    def _detect_enemies(self, image):
        """Detect enemies in the image."""
        # Convert to HSV for better color filtering
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Red color range for enemies (red is at both ends of HSV hue spectrum)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        # Create masks and combine
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        enemies = []
        for contour in contours:
            # Filter by size to avoid noise
            if cv2.contourArea(contour) > 50:
                x, y, w, h = cv2.boundingRect(contour)
                enemies.append({
                    'x': x + w // 2,
                    'y': y + h // 2,
                    'width': w,
                    'height': h
                })
        
        return enemies
    
    def _detect_bullets(self, image):
        """Detect bullets in the image."""
        # Convert to grayscale and threshold for bullets
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bullets = []
        for contour in contours:
            # Filter by size to find bullet shapes
            area = cv2.contourArea(contour)
            if 5 < area < 100:  # Bullets are typically small
                x, y, w, h = cv2.boundingRect(contour)
                
                # Determine bullet direction based on its shape and position
                # Typically player bullets move up, enemy bullets move down
                direction = 'up' if h > w else 'down'
                
                bullets.append({
                    'x': x + w // 2,
                    'y': y + h // 2,
                    'direction': direction
                })
        
        return bullets
    
    def _draw_debug(self, image, player, enemies, bullets):
        """Draw debug information on the image."""
        # Draw player
        if player:
            cv2.circle(image, (player['x'], player['y']), 10, (0, 255, 0), 2)
        
        # Draw enemies
        for enemy in enemies:
            cv2.rectangle(image, 
                        (enemy['x'] - enemy['width']//2, enemy['y'] - enemy['height']//2),
                        (enemy['x'] + enemy['width']//2, enemy['y'] + enemy['height']//2),
                        (0, 0, 255), 2)
        
        # Draw bullets
        for bullet in bullets:
            color = (0, 255, 255) if bullet['direction'] == 'up' else (255, 0, 255)
            cv2.circle(image, (bullet['x'], bullet['y']), 3, color, -1)
        
        return image
    
    def calibrate(self, screenshot_bytes):
        """Calibrate the vision system based on a sample screenshot."""
        # This method can be implemented to automatically adjust the game area
        # based on the actual screenshot from the website
        print("Vision system calibration started...")
        
        # Convert screenshot to image
        image = Image.open(io.BytesIO(screenshot_bytes))
        image_np = np.array(image)
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        
        # Save calibration image
        cv2.imwrite('calibration.png', image_cv)
        
        # TODO: Implement auto-calibration logic based on game elements
        print("Vision system calibration completed.")
