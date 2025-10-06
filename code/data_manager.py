# data_manager.py
import json
import os
from models import Habit
from settings import DATA_FILE


class DataManager:
    @staticmethod
    def save_habits(habits: list[Habit]):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([h.to_dict() for h in habits], f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Критическая ошибка: Не удалось сохранить данные в {DATA_FILE}. Причина: {e}")

    @staticmethod
    def load_habits() -> list[Habit]:
        if not os.path.exists(DATA_FILE):
            return []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    print(f"Ошибка: {DATA_FILE} содержит неверный формат данных (не список).")
                    return []
        except (IOError, json.JSONDecodeError) as e:
            print(f"Критическая ошибка: Не удалось прочитать или декодировать {DATA_FILE}. Причина: {e}")
            return []

        valid_habits = []
        for habit_data in data:
            try:
                if not isinstance(habit_data.get("goal"), (int, float)) or habit_data["goal"] <= 0:
                    print(f"Пропущена привычка с неверной целью: {habit_data.get('text')}")
                    continue
                if not all(key in habit_data for key in ["text", "units", "goal"]):
                    print(f"Пропущена привычка с отсутствующими полями: {habit_data.get('text')}")
                    continue

                valid_habits.append(Habit.from_dict(habit_data))
            except (TypeError, KeyError, ValueError) as e:
                print(f"Пропущена поврежденная запись о привычке: {habit_data}. Причина: {e}")

        return valid_habits