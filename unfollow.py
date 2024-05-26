import instaloader
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

username = os.getenv('INSTAGRAM_USERNAME')
password = os.getenv('INSTAGRAM_PASSWORD')
print("user:",username)

# Create an instance of Instaloader
L = instaloader.Instaloader()

# Login to Instagram
L.login(username, password)

os.system('say "Login complete"')  # Uses the say command on Mac

# Load your profile
profile = instaloader.Profile.from_username(L.context, username)

os.system('say "Profile complete"')  # Uses the say command on Mac

# Load followers and following from storage if available
followers_file = f'{username}_followers.json'
following_file = f'{username}_following.json'
non_followers_file= f'{username}_non_followers.json'

if os.path.exists(followers_file) and os.path.exists(following_file):
    with open(followers_file, 'r') as f:
        followers = set(json.load(f))
    with open(following_file, 'r') as f:
        following = set(json.load(f))
else:
    # Get the list of followers and following
    followers = {follower.username for follower in profile.get_followers()}
    with open(followers_file, 'w') as f:
        json.dump(list(sorted(followers)), f)
    os.system('say "followers complete"')  # Uses the say command on Mac

    following = {followee.username for followee in profile.get_followees()}
    with open(following_file, 'w') as f:
        json.dump(list(sorted(following)), f)
    os.system('say "following complete"')  # Uses the say command on Mac

# Find out who you are following that doesn't follow you back
non_followers = following - followers
with open(non_followers_file, 'w') as f:
    json.dump(list(sorted(non_followers)), f)
os.system('say "non_followers complete"')  # Uses the say command on Mac

# Load public non-followers from storage if available
# public_non_followers_file = 'public_non_followers.json'

# if os.path.exists(public_non_followers_file):
#     with open(public_non_followers_file, 'r') as f:
#         public_non_followers = json.load(f)
# else:
#     # Filter out private accounts using Instaloader
#     public_non_followers = []
#     for user in non_followers:
#         user_profile = instaloader.Profile.from_username(L.context, user)
#         if not user_profile.is_private:
#             public_non_followers.append(user)
#     with open(public_non_followers_file, 'w') as f:
#         json.dump(sorted(public_non_followers), f)
#     os.system('say "private account filter complete"')  # Uses the say command on Mac

# If you wish to avoid checking whether the non-followers are private profiles.
public_non_followers=non_followers 

# Create a timestamped filename for the report
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_filename = f"{username}_report_{timestamp}.txt"

# Open a file to write the report
with open(report_filename, "w") as report_file:
    # Write the followers and following information
    report_file.write("Followers:\n")
    for follower in sorted(followers):
        report_file.write(f"{follower}\n")
    
    report_file.write("\nFollowing:\n")
    for followee in sorted(following):
        report_file.write(f"{followee}\n")

    report_file.write("\nnon_followers:\n")
    for non_follower in sorted(non_followers):
        report_file.write(f"{non_follower}\n")
    
    report_file.write("\nUnfollowed Users:\n")
    # Setup Selenium WebDriver (e.g., Chrome)
    driver = webdriver.Chrome()  # Ensure chromedriver is in PATH or provide the executable path

    # Login to Instagram via WebDriver
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(2)

    # Enter username and password
    username_input = driver.find_element(By.NAME, 'username')
    password_input = driver.find_element(By.NAME, 'password')

    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

    time.sleep(5)  # Wait for login to complete

    # Unfollow those who don't follow you back and are not private accounts
    for user in sorted(public_non_followers, reverse=True):
        driver.get(f'https://www.instagram.com/{user}/')
        time.sleep(2)

        try:
            # Use JavaScript to find and click the "Following" button
            following_button = driver.execute_script(
                'return document.querySelectorAll("button")[0];'
            )
            if following_button:
                button_text = following_button.find_element(By.XPATH, './*[1]/*[1]').text
                if button_text == "Following":
                    following_button.click()
                    time.sleep(1)
                    # Find and click the "Unfollow" button by specific style
                    unfollow_span = driver.find_element(By.XPATH, '//span[text()="Unfollow"]')
                    unfollow_span.click()
                    time.sleep(1)
                    button_text = following_button.find_element(By.XPATH, './*[1]/*[1]').text
                    if button_text == "Follow":
                        print(f"Unfollowed {user}")
                        report_file.write(f"{user}\n")
                    else:
                        print(f"Failed to unfollow {user}")
                        report_file.write(f"Failed to unfollow {user}\n")
                        os.system(f'say "Failed to unfollow {user}"')  # Uses the say command on Mac
        except Exception as e:
            print(f"Failed to unfollow {user}: {e}")
            report_file.write(f"Failed to unfollow {user}: {e}\n")
    driver.quit()
    os.system('say "unfollow action complete"')  # Uses the say command on Mac

print(f"Unfollowed users who didn't follow you back and were not private accounts.")
print(f"Report saved as {report_filename}.")
