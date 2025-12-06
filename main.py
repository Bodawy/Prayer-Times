import sys
import os
import requests
import time
import threading
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
    QHBoxLayout, QSizePolicy       
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer
from geopy.geocoders import Nominatim
import pygame
from plyer import notification  # 🔔 added (desktop notification)

# ------------------ CORE FUNCTIONS ------------------
def get_location():
    geolocator = Nominatim(user_agent="prayer_app")
    location = geolocator.geocode("Cairo, Egypt")
    return location.latitude, location.longitude
# 1
def get_prayer_times(lat, lon):
    url = f"http://api.aladhan.com/v1/timings/{int(time.time())}?latitude={lat}&longitude={lon}&method=5"
    response = requests.get(url)
    data = response.json()["data"]["timings"]
    return {
        "الفجر": convert_time(data["Fajr"]),
        "الظهر": convert_time(data["Dhuhr"]),
        "العصر": convert_time(data["Asr"]),
        "المغرب": convert_time(data["Maghrib"]),
        "العشاء": convert_time(data["Isha"])
    }
#
def convert_time(time_str):
    try:
        return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
    except:
        return time_str

# ------------------ AUDIO CONTROL ------------------
pygame.mixer.init()

def play_adhan():
    pygame.mixer.music.load("adhan.mp3")
    pygame.mixer.music.play()

def stop_adhan():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    

# ------------------ MAIN APP UI ------------------
class PrayerTimesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مواقيت الصلاة")
        self.setGeometry(100, 100, 400, 650)
        self.setStyleSheet("background-color: #EAFBE0; color: #1C5D2D;")
        self.prayer_times = {}
        self.notified = set()
        self.card_widgets = {}  # 🆕 store card widgets so we can update their style
        self.init_ui()
        self.fetch_times()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_time)
        self.timer.start(20000)  # every 20 seconds

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("مواقيت الصلاة")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)

        date_label = QLabel(datetime.now().strftime("%d %B %Y"))
        date_label.setFont(QFont("Arial", 14))
        date_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(date_label)

        self.cards = {}
        for name in ["الفجر", "الظهر", "العصر", "المغرب", "العشاء"]:
            card = self.create_prayer_card(name, "--:--")
            self.layout.addWidget(card)
            self.cards[name] = card.findChild(QLabel, "time")
            self.card_widgets[name] = card

        self.stop_button = QPushButton("إيقاف الأذان")
        self.stop_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.stop_button.setStyleSheet("background-color: #E74C3C; color: white; border-radius: 15px; padding: 15px;")
        self.stop_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.stop_button.clicked.connect(self.stop_adhan)
        self.stop_button.setVisible(False)
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)

    def create_prayer_card(self, name, time, highlight=False):
        icon_map = {
            "الفجر": "fajr",
            "الظهر": "dhuhr",
            "العصر": "asr",
            "المغرب": "maghrib",
            "العشاء": "isha"
        }

        border_style = "3px solid #28a745" if highlight else "none"

        container = QWidget()
        container.setStyleSheet(f"""
            background-color: #DFF5D1;
            border-radius: 15px;
            border: {border_style};
        """)
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(15, 10, 15, 10)

        icon_label = QLabel()
        icon_filename = icon_map.get(name, "default")
        icon_path = f"icons/{icon_filename}.png"
        pixmap = QPixmap(icon_path)
        pixmap = pixmap.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(28, 28)

        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 16, QFont.Bold))
        name_label.setStyleSheet("color: #1C5D2D;")

        time_label = QLabel(time)
        time_label.setObjectName("time")
        time_label.setFont(QFont("Arial", 16, QFont.Bold))
        time_label.setStyleSheet("color: #1C5D2D;")

        h_layout.addWidget(icon_label)
        h_layout.addSpacing(10)
        h_layout.addWidget(name_label)
        h_layout.addStretch()
        h_layout.addWidget(time_label)

        container.setLayout(h_layout)
        return container

    def fetch_times(self):
        lat, lon = get_location()
        self.prayer_times = get_prayer_times(lat, lon)

        for name, time_str in self.prayer_times.items():
             if name in self.cards:
                self.cards[name].setText(time_str)

    def get_next_prayer(self):
        now = datetime.now()
        for name, time_str in self.prayer_times.items():
            try:
                prayer_time = datetime.strptime(time_str, "%I:%M %p")
                prayer_time = prayer_time.replace(year=now.year, month=now.month, day=now.day)
                if prayer_time > now:
                    return name
            except:
                continue
        return None

    def check_time(self):
        now = datetime.now().strftime("%I:%M %p")
        next_prayer = self.get_next_prayer()

        # 🔄 update card styles according to the next prayer
        for name, widget in self.card_widgets.items():
            border = "3px solid #28a745" if name == next_prayer else "none"
            widget.setStyleSheet(f"""
                background-color: #DFF5D1;
                border-radius: 15px;
                border: {border};
            """)

        # 🔔 play adhan at the scheduled time
        for name, time_str in self.prayer_times.items():
            if now == time_str and name not in self.notified:
                self.send_notification(name, time_str)
                play_adhan()
                self.stop_button.setVisible(True)
                self.notified.add(name)

    def send_notification(self, prayer_name, time_str):
        notification.notify(
            title=f"🕌 حان الآن موعد صلاة {prayer_name}",
            message=f"الوقت الآن: {time_str}",
            app_name="مواقيت الصلاة"
        )

    def stop_adhan(self):
        stop_adhan()
        self.stop_button.setVisible(False)


# ------------------ START APP ------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PrayerTimesApp()
    window.show()
    sys.exit(app.exec_())