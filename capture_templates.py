import os
import time
import cv2
import numpy as np
from PIL import Image
import io
from game_controller import GameController

def capture_templates(save_dir="templates"):
    """Capture templates of game elements for vision system."""
    
    # Create save directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    print("Starting game to capture templates...")
    controller = GameController(headless=False)
    
    try:
        if controller.start_game():
            print("Game started. Capturing screenshots...")
            time.sleep(3)  # Wait for game to fully initialize
            
            # Capture full game screen
            screenshot = controller.get_screenshot()
            if screenshot:
                # Save raw screenshot
                with open(os.path.join(save_dir, "full_game.png"), "wb") as f:
                    f.write(screenshot)
                
                # Convert to OpenCV format
                image = Image.open(io.BytesIO(screenshot))
                image_np = np.array(image)
                image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                
                # Save as game screenshot
                cv2.imwrite('game_screenshot.png', image_cv)
                print("Saved game screenshot")
                
                # Move player and take additional screenshots for calibration
                controller.move_left()
                time.sleep(0.5)
                left_screenshot = controller.get_screenshot()
                with open(os.path.join(save_dir, "player_left.png"), "wb") as f:
                    f.write(left_screenshot)
                
                controller.move_right()
                controller.move_right()
                time.sleep(0.5)
                right_screenshot = controller.get_screenshot()
                with open(os.path.join(save_dir, "player_right.png"), "wb") as f:
                    f.write(right_screenshot)
                
                # Shoot some bullets
                controller.shoot()
                time.sleep(0.3)
                shoot_screenshot = controller.get_screenshot()
                with open(os.path.join(save_dir, "player_shooting.png"), "wb") as f:
                    f.write(shoot_screenshot)
                
                print(f"Templates captured and saved to {save_dir}")
                
            else:
                print("Failed to capture screenshot")
        else:
            print("Failed to start game")
    
    finally:
        time.sleep(2)
        controller.close()
        print("Template capture complete")

if __name__ == "__main__":
    capture_templates()
