import pyautogui
import time

# Function to press volume up key
def volume_up():
    pyautogui.press('volumeup')

# Function to press volume down key
def volume_down():
    pyautogui.press('volumedown')

# Increase volume
for _ in range(20):
    volume_up()
    time.sleep(0.1)

# # Decrease volume
# for _ in range(5):
#     volume_down()
#     time.sleep(0.1)
