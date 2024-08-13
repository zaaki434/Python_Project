import speech_recognition as sr
import subprocess
import re
import tkinter as tk
from threading import Thread

# Path to NirCmd in System32
nircmd_path = "C:\\Windows\\System32\\nircmd.exe"

# Initialize the recognizer
recognizer = sr.Recognizer()

def recognize_speech():
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)
        
        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"Recognized command: {command}")
            
            if "chrome" in command:
                print("Opening Chrome...")
                subprocess.run(["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"])
            elif "file explorer" in command:
                print("Opening File Explorer...")
                subprocess.run(["C:\\Windows\\explorer.exe"])
            elif "visual studio code" in command:
                print("Opening Visual Studio Code...")
                subprocess.run(["C:\\Users\\muham\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"])
            elif "change my volume to" in command:
                print("Changing volume...")
                change_volume(command)
            else:
                print("Command not recognized")
        except sr.UnknownValueError:
            print("Sorry, I did not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

def change_volume(command):
    # Extract the volume level from the command
    volume_level = re.search(r'\d+', command)
    if volume_level:
        volume_value = int(volume_level.group())
        if 0 <= volume_value <= 100:
            # Convert volume to the range required by NirCmd
            volume_value = int(volume_value * 655.35)
            try:
                subprocess.run([nircmd_path, "setsysvolume", str(volume_value)], shell=True, check=True)
                print(f"Volume changed to {volume_value / 655.35}%")
            except subprocess.CalledProcessError as e:
                print(f"Failed to change volume: {e}")
        else:
            print("Volume value must be between 0 and 100.")
    else:
        print("No valid volume level found in the command.")

def start_recognition():
    while True:
        recognize_speech()

def start_recognition_thread():
    thread = Thread(target=start_recognition, daemon=True)
    thread.start()

# Create the GUI
def create_gui():
    window = tk.Tk()
    window.title("Voice Command App")
    window.geometry("300x150")

    # Start recognition button
    start_button = tk.Button(window, text="Start Listening", command=start_recognition_thread)
    start_button.pack(pady=20)

    # Exit button
    exit_button = tk.Button(window, text="Exit", command=window.quit)
    exit_button.pack(pady=20)

    window.mainloop()

# Main entry point
if __name__ == "__main__":
    create_gui()
