# models.py
import uuid
from datetime import date, timedelta
import random
from settings import AVAILABLE_ICONS, COLORS

class Habit:
    """
    Класс, представляющий одну измеримую привычку с целью.
    """
    def __init__(self, text: str, goal: float, units: str, color: str = None, icon: str = None,
                 progress_log: dict = None, habit_id: str = None):
        self.id = habit_id if habit_id else str(uuid.uuid4())
        self.text = text
        self.goal = float(goal)
        self.units = units
        self.color = color if color else random.choice(list(COLORS.values()))
        self.icon = icon if icon else random.choice(AVAILABLE_ICONS)
        self.progress_log = progress_log if progress_log else {}

    def get_progress_on(self, check_date: date) -> float:
        """Возвращает прогресс за указанный день."""
        return self.progress_log.get(check_date.isoformat(), 0.0)

    def add_progress(self, value: float, on_date: date = date.today()):
        """Добавляет значение к прогрессу за указанный день."""
        key = on_date.isoformat()
        current_progress = self.get_progress_on(on_date)
        self.progress_log[key] = current_progress + float(value)

    def get_progress_percent(self, on_date: date = date.today()) -> float:
        """Возвращает процент выполнения цели за день."""
        if self.goal == 0: return 100.0
        progress = self.get_progress_on(on_date)
        return min(100.0, (progress / self.goal) * 100.0)

    def is_completed_on(self, check_date: date) -> bool:
        """Проверяет, достигнута ли цель в указанный день."""
        return self.get_progress_on(check_date) >= self.goal

    def get_summary_text(self, on_date: date = date.today()) -> str:
        """Возвращает текстовое описание прогресса."""
        progress = self.get_progress_on(on_date)
        return f"{progress:.1f} из {self.goal:.1f} {self.units}"

    def get_weekly_data(self, today: date = date.today()) -> dict:
        """Возвращает данные о прогрессе за последние 7 дней."""
        data = {}
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            data[day] = self.get_progress_on(day)
        return data

    def to_dict(self) -> dict:
        return {
            "id": self.id, "text": self.text, "goal": self.goal, "units": self.units,
            "color": self.color, "icon": self.icon, "progress_log": self.progress_log
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            habit_id=data.get("id"), text=data.get("text"), goal=data.get("goal", 1),
            units=data.get("units", "раз"), color=data.get("color"), icon=data.get("icon"),
            progress_log=data.get("progress_log", {})
        )