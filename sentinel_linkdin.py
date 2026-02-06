import os
import time
import random
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Load the secret sauce
load_dotenv()

class VoidCareerHacker:
    def __init__(self):
        print(">> 🐀 Initializing the Career Hacker...")
        
        # Setup Chrome Options (Keep it clean)
        self.options = Options()
        # self.options.add_argument("--headless") # Don't hide the browser yet, we need to see the chaos
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-notifications")

        current_dir = os.getcwd()
        profile_path = os.path.join(current_dir, "linkedin_profile")
        self.options.add_argument(f"user-data-dir={profile_path}")
        
        # Initialize Driver
        self.driver = webdriver.Chrome(options=self.options)
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")

        if not self.email or not self.password:
            print(">> ❌ ERROR: Credentials missing in .env file!")
            exit()

    def human_sleep(self, min_s=2, max_s=5):
        """Sleeps for a random human-like interval."""
        time.sleep(random.uniform(min_s, max_s))

    def login(self):
        """
        Breaches the LinkedIn Mainframe.
        """
        print(">> 🔓 Navigating to LinkedIn Login...")
        self.driver.get("https://www.linkedin.com/login")
        self.human_sleep(2, 4)

        try:
            # 1. Enter Email
            email_box = self.driver.find_element(By.ID, "username")
            email_box.clear()
            # Type slowly like a human (optional, but safer)
            for char in self.email:
                email_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            self.human_sleep(1, 2)

            # 2. Enter Password
            pass_box = self.driver.find_element(By.ID, "password")
            pass_box.send_keys(self.password)
            
            self.human_sleep(1, 2)

            # 3. Smash that Sign In Button
            print(">> 👊 Clicking Sign In...")
            self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            
            # Wait for the feed to load (Check for the 'search' bar or 'me' icon)
            self.human_sleep(5, 8)
            
            if "feed" in self.driver.current_url:
                print(">> ✅ Login Successful. We are in.")
            else:
                print(">> ⚠️ Captcha or 2FA might be blocking us. Handle it manually!")
                input("Press Enter here once you have solved the Captcha...")

        except Exception as e:
            print(f">> ❌ Login Failed: {e}")

    def go_to_jobs(self):
        """
        Navigates to the 'Easy Apply' Job Search.
        """
        print(">> 🕵️ Hunting for 'Easy Apply' jobs...")
        
        # URL Parameters:
        # keywords = python developer
        # f_AL = true (This turns on the 'Easy Apply' filter)
        # location = India (or Remote)
        
        search_url = "https://www.linkedin.com/jobs/search/?currentJobId=3798967988&f_AL=true&keywords=python%20developer&location=India&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
        
        self.driver.get(search_url)
        self.human_sleep(3, 5)
        print(">> 📜 Job List Loaded.")
        
        # --- TEST: Count the buttons ---
        try:
            # Find all job cards on the left rail
            job_cards = self.driver.find_elements(By.CLASS_NAME, "job-card-container")
            print(f">> 🔢 Found {len(job_cards)} potential targets on this page.")
            
        except Exception as e:
            print(f">> ⚠️ Could not count jobs: {e}")

    def close(self):
        print(">> 🐀 Mission Complete. Returning to the sewers.")
        self.driver.quit()

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    bot = VoidCareerHacker()
    bot.login()
    bot.go_to_jobs()
    
    # Keep it open so you can see your empire
    print(">> ⏸️ Script finished. Browser stays open for inspection.")
    input("Press Enter to close browser...")
    bot.close()

