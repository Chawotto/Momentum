# app.py
import customtkinter as ctk
from models import Habit
from data_manager import DataManager
from pages import HabitListPage
from settings import APP_NAME, WINDOW_SIZE


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        ctk.set_appearance_mode("System")
        self.configure(fg_color=("gray92", "black"))

        self.habits = DataManager.load_habits()

        # --- Система навигации ---
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.page_stack = []
        self.current_page = None

        self.navigate_to(HabitListPage)

    def navigate_to(self, PageClass, **kwargs):
        new_page = PageClass(self.container, self, **kwargs)

        if self.current_page:
            self.current_page.destroy()
            self.page_stack.append(PageClass)

        self.current_page = new_page
        self.current_page.pack(fill="both", expand=True)

    def navigate_back(self):
        if not self.page_stack: return

        self.current_page.destroy()
        self.page_stack.pop()

        if not self.page_stack:
            PreviousPageClass = HabitListPage
        else:
            PreviousPageClass = self.page_stack.pop()

        self.navigate_to(PreviousPageClass)

    def _save_data_and_refresh(self):
        DataManager.save_habits(self.habits)
        if hasattr(self.current_page, 'display_habits'):
            self.current_page.display_habits()

    def _add_or_update_habit(self, data: dict, habit_id=None):
        if habit_id:
            habit = next((h for h in self.habits if h.id == habit_id), None)
            if habit:
                habit.text, habit.goal, habit.units = data["text"], data["goal"], data["units"]
                habit.icon, habit.color = data["icon"], data["color"]
        else:
            self.habits.append(Habit(**data))
        self._save_data_and_refresh()

    def _delete_habit(self, habit_id):
        self.habits = [h for h in self.habits if h.id != habit_id]
        self._save_data_and_refresh()

    def _add_progress_to_habit(self, habit: Habit, value: float):
        habit.add_progress(value)
        self._save_data_and_refresh()