# Prayer-Times

🕌 Prayer Times App  
A Python application that fetches and displays Islamic prayer times for a specific location using the Aladhan API. The app also provides notifications and plays the Adhan (call to prayer) when it's time for a prayer.

## 📌 Features
- 📍 Fetches prayer times based on location (default: Cairo, Egypt)
- 🔔 Sends desktop notifications for each prayer time
- 🔊 Plays Adhan when it's time for a prayer
- 🕒 Automatically updates prayer times every 30 seconds

## 🛠️ Installation
Clone the repository:

```bash
git clone https://github.com/your-username/prayer-times-app.git
cd prayer-times-app
```

Install required dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

## 📦 Dependencies
This project requires the following Python libraries:
- `requests` (for API calls)
- `tkinter` (for the GUI)
- `geopy` (for location retrieval)
- `plyer` (for notifications)
- `playsound` (for playing Adhan audio)
- `threading` (for handling audio in a separate thread)

You can install all dependencies using:

```bash
pip install requests geopy plyer playsound
```

## 🎵 Audio File
Ensure you have an `adhan.mp3` file in the project directory to play the Adhan when a prayer time is reached.

## 📌 Notes
- The app currently uses Cairo, Egypt as the default location.
- Prayer times are retrieved from [Aladhan API](https://aladhan.com/).
- Make sure to allow notifications on your operating system.

## 🔗 API Reference
[Aladhan API](https://aladhan.com/)

## 📜 License
This project is open-source and available under the MIT License.# Prayer-Times
