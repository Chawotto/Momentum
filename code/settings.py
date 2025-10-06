# settings.py
import os

APP_NAME = "Momentum"
WINDOW_SIZE = "500x750"
DATA_FILE = "data.json"

COLORS = {
    "blue": "#007AFF", "green": "#34C759", "indigo": "#5856D6",
    "orange": "#FF9500", "pink": "#FF2D55", "teal": "#5AC8FA", "yellow": "#FFCC00"
}
DESTRUCTIVE_COLOR = "#FF3B30"
ERROR_COLOR = "#D32F2F"

ASSETS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
ICONS_PATH = os.path.join(ASSETS_PATH, "icons")

try:
    AVAILABLE_ICONS = sorted([f for f in os.listdir(ICONS_PATH) if f.endswith('.png')])
    if not AVAILABLE_ICONS: AVAILABLE_ICONS = ["default.png"]
except FileNotFoundError:
    print(f"ВНИМАНИЕ: Папка {ICONS_PATH} не найдена!")
    AVAILABLE_ICONS = ["default.png"]