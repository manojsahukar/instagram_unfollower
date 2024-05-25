import instaloader
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Create an instance of Instaloader
L = instaloader.Instaloader()

# Login to Instagram
username = 'user'
password = 'pwd'
L.login(username, password)

os.system('say "Login complete"')  # Uses the say command on Mac

# Load your profile
profile = instaloader.Profile.from_username(L.context, username)

os.system('say "Profile complete"')  # Uses the say command on Mac

# Get the list of followers and following
followers = {follower.username for follower in profile.get_followers()}
os.system('say "followers complete"')  # Uses the say command on Mac

following = {followee.username for followee in profile.get_followees()}
os.system('say "following complete"')  # Uses the say command on Mac

# Find out who you are following that doesn't follow you back
non_followers = following - followers

os.system('say "non_followers complete"')  # Uses the say command on Mac

# Filter out private accounts using Instaloader
public_non_followers = []
for user in non_followers:
    user_profile = instaloader.Profile.from_username(L.context, user)
    if not user_profile.is_private:
        public_non_followers.append(user)

os.system('say "private account filter complete"')  # Uses the say command on Mac

# Create a timestamped filename for the report
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_filename = f"unfollowed_users_report_{timestamp}.txt"

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
    for user in sorted(public_non_followers):
        driver.get(f'https://www.instagram.com/{user}/')
        time.sleep(2)

        try:
            # Use JavaScript to find and click the "Following" button
            following_button = driver.execute_script(
                'return document.querySelectorAll("button")[0];'
            )
            if following_button:
                following_button.click()
                time.sleep(1)
                # Find and click the "Unfollow" button by specific style
                unfollow_span = driver.find_element(By.XPATH, '//span[text()="Unfollow"]')
                unfollow_span.click()
                print(f"Unfollowed {user}")
                report_file.write(f"Unfollowed {user}\n")
            else:
                print(f"Failed to find unfollow button for {user}")
                report_file.write(f"Failed to find unfollow button for {user}\n")
        except Exception as e:
            print(f"Failed to unfollow {user}: {e}")
            report_file.write(f"Failed to unfollow {user}: {e}\n")

    driver.quit()
    os.system('say "unfollow action complete"')  # Uses the say command on Mac

print(f"Unfollowed users who didn't follow you back and were not private accounts.")
print(f"Report saved as {report_filename}.")