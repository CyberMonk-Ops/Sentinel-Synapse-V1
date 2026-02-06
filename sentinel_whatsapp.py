import time
import random
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc 

import brain

# --- CONFIG ---
# UPDATE THIS PATH TO YOUR CHROME USER DATA
# Type "chrome://version" in your browser to find the "Profile Path"
CHROME_PROFILE = None   

class SentinelWA:
    def __init__(self):
        print(">> 🦾 Sentinel WhatsApp: Initializing...")
        #options = webdriver.ChromeOptions()
        # Use existing login
        #options.add_argument(f"user-data-dir={CHROME_PROFILE}")
        #options.add_argument(f"--profile-directory={PROFILE_DIR}")
        bot_profile_path = os.path.join(os.getcwd(), "sentinel_browser_data")
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={bot_profile_path}")
        #options.add_experimental_option("detach", True) # Keep open
        
        self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=144)   #webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 20)
        
        print(">> 🌐 Opening WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        # Human wait for load
        time.sleep(random.uniform(5.0, 8.0))
        input(">> action requirec ")
        print("granted")
    def human_type(self, element, text):
        """Types like a bored 24-year-old."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2)) # Normal typing
            if random.random() < 0.05: # 5% chance to pause/think
                time.sleep(random.uniform(0.5, 1.0))

    def send_message(self, contact_name, message):
        try:
            print(f">> 📨 Targeting: {contact_name}")
            
            # 1. SEARCH BOX (Update XPath using Inspect Element if this fails!)
            # Look for: contenteditable="true" and data-tab="3" (Side Panel)
            search_box = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            search_box.clear()
            self.human_type(search_box, contact_name)
            
            time.sleep(2)
            search_box.send_keys(Keys.ENTER)
            
            # 2. CHAT BOX (Update XPath if needed!)
            # Look for: contenteditable="true" and data-tab="10" (Main Panel)
            msg_box = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            
            # 3. TYPE & SEND
            time.sleep(random.uniform(1.0, 3.0)) # Read previous text
            self.human_type(msg_box, message)
            
            time.sleep(1)
            msg_box.send_keys(Keys.ENTER)
            print(f"✅ Sent: {message}")
            return True

        except Exception as e:
            print(f"❌ Failed: {e}")
            return False

    def clean_text_for_selenium(self, text):
        """
        Removes characters that crash Selenium (Non-BMP emojis).
        Also strips asterisks ** because WhatsApp doesn't need Markdown bolding from bots.
        """
        # 1. Strip Non-BMP characters (The complex emojis that caused the crash)
        cleaned = "".join(c for c in text if c <= "\uFFFF")

        # 2. Remove Markdown bolding (The **GitHub** stuff looked robotic)
        cleaned = cleaned.replace("**", "").replace("##", "")
    
        return cleaned

    def human_type(self, element, text):
        """
        Types like a human:
        - Random delay between keys.
        - Occasional pauses for 'thinking'.
        """
        for char in text:
            if char == "\n":
                element.send_keys(Keys.RETURN)
                time.sleep(random.uniform(1.0,3.0))
                continue


            element.send_keys(char)
        
            # Base speed: 0.05s to 0.15s per key (Fast but human)
            delay = random.uniform(0.05, 0.15)
        
            # 10% chance to pause (simulating thinking or finding the key)
            if random.random() < 0.1:
                delay += 0.3

                time.sleep(delay)


    



   
    def check_for_unread(self):
        """
        Scans the 'Side' panel for any Green Unread Bubbles.
        Returns: True if found and clicked, False if silence.
        """
        print(">> 🕵️ Scanning for unread messages...")
        
        try:
            # The Magic XPath for the Green Bubble
            # It looks for a span with an 'aria-label' usually containing 'unread message'
            # OR just looks for the visual green badge class (which changes often, so we use logic)
            
            # METHOD 1: Look for the text "unread message" in the side panel
            unread_chats = self.driver.find_elements(By.XPATH, '//div[@id="side"]//span[@aria-label and contains(@aria-label, "unread message")]')
            
            if not unread_chats:
                # METHOD 2: Fallback (Look for the green color icon specifically)
                # This is risky but often works if Method 1 fails
                unread_chats = self.driver.find_elements(By.XPATH, '//div[@id="side"]//span[@data-icon="unread-count"]')

            if unread_chats:
                print(f">> 🟢 Found {len(unread_chats)} unread chat(s)!")
                for chats in unread_chats:

                
                # Pick the first one and click it
                #target = unread_chats[0]
                
                # We need to click the PARENT container, not the tiny bubble
                # This moves up the tree to find the clickable chat row
                #chat_row = target_chat.find_element(By.XPATH, './ancestor::div[@role="row"]')
                #chat_row.click()
                    try:
                        row = chats.find_element(By.XPATH, './ancestor::div[@role="row" or @role="botton"]')
                        row_text=row.text
                        if "Archived" in row_text:
                            continue
                            print(f"skipping {chats.text} ")

                        try:
                            print(f"norml click {row_text.splitlines()[0]}")
                            chats.click()
                            time.sleep(random.uniform(2,4))
                            return True
                        except:
                            print("js force click")
                            self.driver.execute_script("arguments[0].click();",chats)
                            time.sleep(random.uniform(2,6))

                            return True
                    except Exception as e :
                        print(f" error processing badge {e}")
                        continue


                #print(">> 🖱️ Chat opened.")
                time.sleep(random.uniform(1.5, 3.0)) # Human pause to "read"
                #return True
            
            else:
                print(">> 🌑 Silence. No new messages.")
                return False

        except Exception as e:
            print(f">> ⚠️ Error checking unread: {e}")
            return False



    def get_last_received_message(self):
        """
        Reads the very last message bubble in the main chat window.
        """
        try:
            # Locate all message containers in the Main panel
            # We filter for messages that are NOT from 'message-out' (which are yours)
            # We want 'message-in' (which are theirs)
            
            # This is a broad search for message rows
            all_messages = self.driver.find_elements(By.XPATH, '//div[@id="main"]//div[contains(@class, "message-in") or contains(@class, "message_out")]')
            
            if all_messages:
                last_msg_container = all_messages[-1] # Get the very last one
                
                # Extract the text span inside
                try:

                    try:
                        print('using selectable_path')
                        text_span= last_msg_container.find_element(By.XPATH, './/span[contains(class, "selectable-text")]')
                    except:
                        print('using copyable path')
                        text_span= last_msg_container.find_element(By.XPATH, './/span[contains(class, "copyable-text")]')

                    print("recieved")
                    message_text = text_span.text
                    print(f">> 📩 Received: '{message_text}'")
                    return message_text
                except:
                    print("non text")
                    return "[non text message]" 

                #text_span = last_msg_container.find_element(By.XPATH, './/span[@class="_11JPr selectable-text copyable-text"]') 
                # Note: '_11JPr' is a class that changes. 
                # BETTER STABLE XPATH: Look for any text container
                #text_span = last_msg_container.find_element(By.XPATH, './/span[contains(@class, "selectable-text")]')
                
               
            
            return None
            
        except Exception as e:
            print(f">> ⚠️ Could not read message: {e}")
            return None




    def get_last_received_message2(self):
        """
        Reads the last message bubble (Incoming OR Outgoing).
        Uses a generic CSS selector to find the text container.
        """
        print(">> 📖 Reading last message...")
        
        try:
            # 1. Find ALL message rows (In and Out)
            # We use a CSS selector because it's faster and cleaner than XPath for multiple classes
            all_messages = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
            
            if not all_messages:
                print(">> ⚠️ DOM is empty. No messages found.")
                return None
                
            # 2. Target the very last one
            last_bubble = all_messages[-1]

            classes = last_bubble.get_attribute("class")
            print(f"classes are {classes} ")
            if "message-out" in classes:
                print("last was mine")
                return None
            
            # 3. Extract Text using the "Copyable" class logic
            # This class 'copyable-text' is usually on the container that holds the message data
            try:
                # We try to find the class that contains the text
                text_container = last_bubble.find_element(By.CSS_SELECTOR, "span.copyable-text")
                
                # If that fails, try the selectable-text class
                # text_container = last_bubble.find_element(By.CSS_SELECTOR, "span.selectable-text")
                
                clean_text = text_container.text
                print(f">> 📩 READ SUCCESS: '{clean_text}'")
                return clean_text
                
            except Exception as e:
                # If we fail to find text, it's likely an image, system message, or deleted msg
                print(f">> ⚠️ Message found but no text extracted. (Type: {last_bubble.get_attribute('class')})")
                return "[NON-TEXT]"

        except Exception as e:
            print(f">> ❌ Critical Error: {e}")
            return None




    def reply_to_chat(self):
        """
        The Full Cycle: Read -> Think -> Type -> Wait.
        """
        # 1. Read the last message
        incoming_text = self.get_last_received_message2()
        
        if not incoming_text or incoming_text == "[NON-TEXT]":
            print(">> 😴 Nothing to reply to.")
            return

        print(f">> 🧠 Thinking about: '{incoming_text}'...")
        
        try:
            # The header usually has class '_amig' or similar, but checking the header title is safer
            chat_title_element = self.driver.find_element(By.XPATH, "//header//span[@dir='auto']")
            chat_name = chat_title_element.text
        except:
            chat_name = "Unknown_User"

            print(f">> 🧠 Loaded Context for: {chat_name}")
        # 2. CALL THE BRAIN (Import your script here)
        # form brain_module import generate_response
        reply_text =  brain.query_llm2(incoming_text , chat_name) #generate_response(incoming_text) 
        
        # --- PLACEHOLDER FOR TESTING ---
        #reply_text = f" '{reply_text}'. "
        # -------------------------------

        print(f">> 🤖 Generated Reply: '{reply_text}'")
        safe_reply = self.clean_text_for_selenium(reply_text)

        # 3. THE "ANTI-NUKE" DELAY (Crucial!)
        # Meta detects bots that type instantly. 
        # We must wait 3-6 seconds to simulate "Reading time" and "Thinking time".
        wait_time = random.uniform(4.0, 8.0)
        print(f">> ⏳ Simulation 'Thinking' for {wait_time:.1f}s...")
        time.sleep(wait_time)

        # 4. Send the Message
        # You already have a send_message function, right? Use it.
        # But we don't need to search for the user again, we are already IN the chat.
        # So just find the input box and type.
        
        try:
            # Find the input box (The text area)
            input_box = self.driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            
            # Click it just to be safe
            input_box.click()
            
            # Simulate Human Typing (One character at a time? Optional but safer)
            # For now, just send the whole chunk.
            self.human_type(input_box, safe_reply)
            #input_box.send_keys(reply_text)
            time.sleep(random.uniform(4.0, 15.0))
            input_box.send_keys(Keys.ENTER)
            
            print(f">> 🚀 REPLY SENT: {reply_text}")
            
            # 5. POST-SEND COOL DOWN
            # Don't check for new messages instantly. Wait.
            print(">> 💤 Resting...")
            time.sleep(random.uniform(2.0, 5.0))
            
        except Exception as e:
            print(f">> ❌ Failed to send reply: {e}")



    def start_sentinel(self):
        """
        The Main Loop. The Rat Life.
        """
        print(">> 🐀 Sentinel is Awake. Monitoring the Void...")
        
        try:
            while True:
                # 1. SCAN: Look for green bubbles
                # This function handles the clicking/opening of the chat
                found_new_chat = self.check_for_unread()

                print(f"massage is {found_new_chat}")
                
                if found_new_chat == None or found_new_chat:
                    print(">> 🚪 Door opened. Engaging protocol...")
                    
                    # 2. ENGAGE: Read -> Think -> Reply
                    # We are already in the chat, so we just run the cycle
                    self.reply_to_chat()
                    
                    # 3. ESCAPE: Clear the selection
                    # Press ESC to unselect the chat so we can see the green badges again clearly
                    # (Optional, but helps prevent reading the same chat twice if logic fails)
                    try:
                        webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                        print(">> 🔙 Returned to Overwatch.")
                    except:
                        pass
                    wait_time = random.uniform(5, 20)
                    print(f">> 💤 No targets. Sleeping for {wait_time:.1f}s...")
                    time.sleep(wait_time)    
                else:
                    # No new messages? Just wait and scan again.
                    # Don't spin the CPU at 100%. Chill.
                    wait_time = random.uniform(5, 20)
                    print(f">> 💤 No targets. Sleeping for {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    
        except KeyboardInterrupt:
            print(">> 🛑 Manual Override. Sentinel Shutting Down.")


# --- TEST AREA ---
if __name__ == "__main__":
    bot = SentinelWA()
    
    # TEST 1: Send a message to yourself (Save your number as "Me" or "Sauvik")
    #bot.send_message("Me", "Sentinel System Check: Online.")
    
    # TEST 2: The Loop (Uncomment to annoy your sister)
    # bot.send_message("Sister Name", "This message was typed by a python script. Hello.")
    #bot.check_for_unread()
    #bot.get_last_received_message()
    #bot.get_last_received_message2()
    #bot.reply_to_chat()
    bot.start_sentinel()


