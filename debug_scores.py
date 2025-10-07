"""
Debug High Score Detection
Find the exact text patterns on the webpage
"""
import requests
import re

def debug_high_score_patterns():
    """Debug what patterns exist on the page"""
    
    try:
        response = requests.get("https://jordancota.site/", timeout=10)
        page_text = response.text
        
        print("🔍 DEBUGGING HIGH SCORE PATTERNS")
        print("=" * 40)
        
        # Look for the High Scores section specifically
        high_scores_index = page_text.find("High Scores")
        if high_scores_index != -1:
            # Extract text around the High Scores section
            start = max(0, high_scores_index - 100)
            end = min(len(page_text), high_scores_index + 1000)
            section_text = page_text[start:end]
            
            print("📄 High Scores section text:")
            print("-" * 30)
            print(section_text)
            print("-" * 30)
            
            # Test different patterns
            patterns = [
                r'(\w+(?:\s+\w+)*)\s*-\s*(\d+)\s*\(Level\s*(\d+)\)',
                r'John H\s*-\s*(\d+)',
                r'(\d+)\s*\(Level\s*\d+\)',
                r'(\d{4,5})',
                r'\b(\d+)\b'
            ]
            
            for i, pattern in enumerate(patterns, 1):
                matches = re.findall(pattern, section_text, re.IGNORECASE)
                print(f"\nPattern {i}: {pattern}")
                print(f"Matches: {matches}")
        
        else:
            print("❌ 'High Scores' text not found on page")
            
            # Look for any mention of "25940"
            if "25940" in page_text:
                print("✅ Found '25940' in page text")
                # Find context around it
                index = page_text.find("25940")
                start = max(0, index - 50)
                end = min(len(page_text), index + 100)
                context = page_text[start:end]
                print(f"Context: {context}")
            else:
                print("❌ '25940' not found in page text")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_high_score_patterns()