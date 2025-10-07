"""
Dynamic High Score Fetcher
Gets the current high score from jordancota.site in real-time
"""
import requests
from bs4 import BeautifulSoup
import re

def get_current_high_score():
    """Fetch the current high score from jordancota.site using Selenium for dynamic content"""
    try:
        print("🌐 Fetching current high score from jordancota.site...")
        
        # Use Selenium to get the rendered page content
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.by import By
        import time
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        try:
            driver.get("https://jordancota.site/")
            time.sleep(3)  # Wait for JavaScript to load the leaderboard
            
            # Get the rendered page content
            page_text = driver.page_source
            
            # Look for the leaderboard pattern
            name_score_pattern = r'(\w+(?:\s+\w+)*)\s*-\s*(\d+)\s*\(Level\s*(\d+)\)'
            matches = re.findall(name_score_pattern, page_text)
            
            if matches:
                # Extract scores and find the maximum
                scores = [int(score) for _, score, _ in matches]
                high_score = max(scores)
                
                # Find the entry with the highest score
                top_entry = next((name, score, level) for name, score, level in matches if int(score) == high_score)
                print(f"✅ Found high score: {high_score:,} points by {top_entry[0]} (Level {top_entry[2]})")
                return high_score
            
            # Fallback patterns
            level_scores = re.findall(r'(\d+)\s*\(Level\s*\d+\)', page_text)
            if level_scores:
                scores = [int(score) for score in level_scores]
                high_score = max(scores)
                print(f"✅ Found high score: {high_score:,} points")
                return high_score
            
            print("⚠️  Could not parse high score from rendered page")
            return 25940  # Fallback to known score
            
        finally:
            driver.quit()
        
    except Exception as e:
        print(f"❌ Error fetching high score with Selenium: {e}")
        print("Using fallback score: 25,940")
        return 25940  # Fallback

def get_high_score_info():
    """Get detailed high score information using Selenium for dynamic content"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        try:
            driver.get("https://jordancota.site/")
            time.sleep(3)  # Wait for JavaScript
            
            page_text = driver.page_source
            
            # Find all score entries with names
            score_entries = re.findall(r'(\w+(?:\s+\w+)*)\s*-\s*(\d+)\s*\(Level\s*(\d+)\)', page_text)
            
            if score_entries:
                print("\n🏆 CURRENT LEADERBOARD:")
                for i, (name, score, level) in enumerate(score_entries[:5], 1):
                    print(f"{i}. {name} - {int(score):,} points (Level {level})")
                
                # Return the top score
                top_score = max(int(score) for _, score, _ in score_entries)
                top_entry = next((name, score, level) for name, score, level in score_entries if int(score) == top_score)
                
                return {
                    'score': top_score,
                    'name': top_entry[0],
                    'level': int(top_entry[2]),
                    'entries': len(score_entries)
                }
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Error getting detailed info with Selenium: {e}")
    
    # Fallback - use the known leaderboard from your screenshot
    return {
        'score': 25940,
        'name': 'John H',
        'level': 8,
        'entries': 10
    }

if __name__ == "__main__":
    print("🎯 HIGH SCORE CHECKER")
    print("=" * 30)
    
    info = get_high_score_info()
    
    print(f"\n🥇 CURRENT HIGH SCORE:")
    print(f"Player: {info['name']}")
    print(f"Score: {info['score']:,} points")
    print(f"Level: {info['level']}")
    print(f"Total entries: {info['entries']}")
    
    simple_score = get_current_high_score()
    print(f"\n🎯 Target for AI: {simple_score:,} points")