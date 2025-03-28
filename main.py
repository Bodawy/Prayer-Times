import requests
import tkinter as tk
from geopy.geocoders import Nominatim
import time
from datetime import datetime
from plyer import notification
from playsound import playsound
import threading

# Dictionary to store prayer timings
saved_timings = {}

# Set to keep track of prayers that have already been notified
notified_prayers = set()

# Function to get the latitude and longitude of a location (default: Cairo, Egypt)
def get_location():
    geolocator = Nominatim(user_agent="prayer_time_app")
    location = geolocator.geocode("Cairo, Egypt")
    return location.latitude, location.longitude

# Function to fetch prayer times from the Aladhan API
def get_prayer_times(latitude, longitude):
    url = f"http://api.aladhan.com/v1/timings/{int(time.time())}?latitude={latitude}&longitude={longitude}&method=5"
    response = requests.get(url)
    data = response.json()
    
    # Format prayer times into 12-hour format
    formatted_timings = {}
    for prayer, time_str in data['data']['timings'].items():
        try:
            time_24 = datetime.strptime(time_str, "%H:%M")
            time_12 = time_24.strftime("%I:%M %p")
            formatted_timings[prayer] = time_12
        except ValueError:
            # If formatting fails, keep the original time string
            formatted_timings[prayer] = time_str
    return formatted_timings

# Function to play the Adhan (call to prayer)
def play_adhan():
    playsound("adhan.mp3")

# Function to send a desktop notification for a specific prayer
def send_notification(prayer, time):
    notification.notify(
        title=f"🕌 موعد صلاة {prayer}",
        message=f"حان الآن موعد صلاة {prayer} - {time}",
        app_name="Prayer Times App",
        timeout=10
    )
    # Play the Adhan in a separate thread
    threading.Thread(target=play_adhan).start()

# Function to check if it's time for any prayer and send notifications
def check_prayer_times():
    current_time = datetime.now().strftime("%I:%M %p")  # Get current time in 12-hour format
    for prayer, time in saved_timings.items():
        if current_time == time and prayer not in notified_prayers:
            send_notification(prayer, time)
            notified_prayers.add(prayer)  # Mark the prayer as notified

# Function to update prayer times in the GUI and check for notifications
def update_times():
    for prayer, time in saved_timings.items():
        if prayer in prayer_times:
            prayer_times[prayer].config(text=f"{prayer}: {time}")  # Update the label text
    check_prayer_times()  # Check for prayer notifications
    root.after(30000, update_times)  # Schedule the function to run every 30 seconds

# Function to fetch and save prayer times
def fetch_prayer_times():
    latitude, longitude = get_location()  # Get location coordinates
    global saved_timings
    saved_timings = get_prayer_times(latitude, longitude)  # Fetch prayer times and save them

# Initialize the Tkinter GUI
root = tk.Tk()
root.title("Prayer Times App")
root.geometry("300x400")

# Title label for the app
title_label = tk.Label(root, text="مواقيت الصلاة", font=("amine_mod", 20, "bold"))
title_label.pack(pady=20)

# Dictionary to store prayer time labels
prayer_times = {}
for prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
    label = tk.Label(root, text=f"{prayer}: Loading...", font=("Arial", 14))
    label.pack(pady=5)
    prayer_times[prayer] = label

# Fetch prayer times and start updating them
fetch_prayer_times()
update_times()

# Start the Tkinter main loop
root.mainloop()