# pages.py
import customtkinter as ctk
from PIL import Image
import os
from datetime import date
from models import Habit
from settings import ICONS_PATH, AVAILABLE_ICONS, COLORS, DESTRUCTIVE_COLOR, ERROR_COLOR

class Page(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color=("gray92", "black"))
        self.app = app_controller


class ConfirmationDialog(ctk.CTkToplevel):
    def __init__(self, master, title, text, command):
        super().__init__(master)
        self.command = command
        self.title(title)
        self.geometry("350x150")
        self.transient(master);
        self.grab_set();
        self.lift()

        ctk.CTkLabel(self, text=text, font=("SF Pro Display", 16), wraplength=300).pack(pady=20, padx=20, expand=True)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Нет", width=100, command=self.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Да, удалить", width=100, fg_color=DESTRUCTIVE_COLOR, hover_color="#C22B21",
                      command=self._confirm).pack(side="left", padx=10)

    def _confirm(self):
        self.command()
        self.destroy()


class AddProgressWindow(ctk.CTkToplevel):
    def __init__(self, master, habit, callback):
        super().__init__(master)
        self.habit, self.callback = habit, callback
        self.configure(fg_color=self.master.winfo_toplevel().cget("fg_color"))
        self.title(f"Добавить {self.habit.units}");
        self.geometry("300x180")
        self.transient(master);
        self.grab_set();
        self.lift()

        ctk.CTkLabel(self, text=f"Сколько {self.habit.units} добавить?").pack(pady=(10, 5))
        self.entry = ctk.CTkEntry(self, placeholder_text="Только положительные числа")
        self.entry.pack(padx=20, fill="x")
        self.entry.bind("<KeyRelease>", self._validate)

        self.error_label = ctk.CTkLabel(self, text="", text_color=ERROR_COLOR)
        self.error_label.pack()

        self.add_button = ctk.CTkButton(self, text="Добавить", command=self._save)
        self.add_button.pack(pady=10, padx=20, fill="x", ipady=5)
        self._validate()  # Первичная проверка, чтобы отключить кнопку

    def _validate(self, event=None):
        value_str = self.entry.get().strip()
        is_valid = False
        try:
            value = float(value_str)
            if value > 0:
                is_valid = True
        except ValueError:
            pass  # Не число

        if not value_str:
            self.error_label.configure(text="")
        elif not is_valid:
            self.error_label.configure(text="Введите число больше нуля")
        else:
            self.error_label.configure(text="")

        self.add_button.configure(state="normal" if is_valid else "disabled")
        self.entry.configure(border_color=ERROR_COLOR if value_str and not is_valid else "gray50")

    def _save(self):
        try:
            self.callback(self.habit, float(self.entry.get().strip())); self.destroy()
        except (ValueError, TypeError):
            pass

class SummaryGraph(ctk.CTkFrame):
    def __init__(self, master, habit: Habit, bg_color):
        super().__init__(master, fg_color=bg_color, corner_radius=16)
        self.habit = habit
        self.canvas = ctk.CTkCanvas(self, height=120, highlightthickness=0, bg=self._apply_appearance_mode(bg_color))
        self.canvas.pack(fill="x", expand=True, padx=15, pady=15)
        self.canvas.bind("<Configure>", self.update_graph)

    def update_graph(self, event=None):
        self.canvas.delete("all")
        weekly_data = self.habit.get_weekly_data()
        max_val = max(self.habit.goal, max(weekly_data.values()) if weekly_data else 0)
        if max_val == 0: max_val = 1
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width <= 1 or height <= 1: return
        bar_width, gap = 20, (width - (7 * 20)) / 6
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        goal_y = height - (self.habit.goal / max_val) * (height - 25) - 20
        self.canvas.create_line(0, goal_y, width, goal_y, fill="gray", width=1, dash=(2, 2))
        for i, (day, value) in enumerate(weekly_data.items()):
            x = i * (bar_width + gap) + bar_width / 2
            bar_height = (value / max_val) * (height - 25)
            y_top, y_bottom = height - bar_height - 20, height - 20
            if bar_height > 0: self.canvas.create_line(x, y_bottom, x, y_top, fill=self.habit.color, width=bar_width,
                                                       capstyle='round')
            self.canvas.create_text(x, height - 10, text=days[day.weekday()],
                                    fill=self._apply_appearance_mode(("#6B6B6B", "#9E9E9E")))


class HabitCard(ctk.CTkFrame):
    def __init__(self, master, habit: Habit, app):
        super().__init__(master, fg_color=("white", "#1C1C1E"), corner_radius=16)
        self.habit, self.app, self.is_expanded = habit, app, False
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="x", padx=15, pady=10)
        self.main_frame.grid_columnconfigure(1, weight=1)
        icon_label = self._create_icon_label(self.main_frame, self.habit.icon, self.habit.color)
        icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 15))
        label = ctk.CTkLabel(self.main_frame, text=self.habit.text, font=("SF Pro Display", 17, "bold"), anchor="w");
        label.grid(row=0, column=1, sticky="ew")
        progress_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent");
        progress_frame.grid(row=1, column=1, sticky="ew");
        progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_bar = ctk.CTkProgressBar(progress_frame, progress_color=self.habit.color);
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.summary_label = ctk.CTkLabel(progress_frame, text="", font=("SF Pro Display", 12), text_color="gray");
        self.summary_label.grid(row=0, column=1)
        buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent");
        buttons_frame.grid(row=0, column=2, rowspan=2, padx=(15, 0))
        settings_icon = self._load_icon("settings.png");
        ctk.CTkButton(buttons_frame, text="", image=settings_icon, width=35, height=35, fg_color="transparent",
                      hover_color=("#F2F2F7", "#2C2C2E"), command=self._open_edit_page).pack(side="right")
        ctk.CTkButton(buttons_frame, text="+", width=35, height=35, corner_radius=10,
                      command=self._open_add_progress).pack(side="right", padx=5)
        card_bg_color = self._apply_appearance_mode(self.cget("fg_color"))
        self.summary_widget = SummaryGraph(self, self.habit, bg_color=card_bg_color)
        self.bind("<Button-1>", self.toggle_summary);
        self.main_frame.bind("<Button-1>", self.toggle_summary);
        label.bind("<Button-1>", self.toggle_summary);
        icon_label.bind("<Button-1>", self.toggle_summary)
        self.update_visual_state()

    def _load_icon(self, filename, size=(20, 20)):
        try:
            return ctk.CTkImage(Image.open(os.path.join(ICONS_PATH, filename)).resize(size))
        except:
            return None

    def _create_icon_label(self, master, icon_file, color):
        icon = self._load_icon(icon_file, size=(28, 28));
        return ctk.CTkLabel(master, text="", image=icon, fg_color=color, width=50, height=50, corner_radius=12)

    def toggle_summary(self, event=None):
        if event and any(isinstance(event.widget, c) for c in (ctk.CTkButton, ctk.CTkProgressBar)): return
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.summary_widget.pack(fill="x", after=self.main_frame, padx=1, pady=(0, 1))
        else:
            self.summary_widget.pack_forget()

    def _open_add_progress(self):
        AddProgressWindow(self, self.habit, self.app._add_progress_to_habit)

    def _open_edit_page(self):
        self.app.navigate_to(AddOrEditHabitPage, habit=self.habit)

    def update_visual_state(self):
        self.progress_bar.set(self.habit.get_progress_percent() / 100);
        self.summary_label.configure(text=self.habit.get_summary_text())


class HabitListPage(Page):
    def __init__(self, master, app_controller):
        super().__init__(master, app_controller)
        header = ctk.CTkFrame(self, fg_color="transparent");
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="Привычки", font=("SF Pro Display", 34, "bold")).pack(side="left")
        stats_button = ctk.CTkButton(header, text="Сводка", command=lambda: self.app.navigate_to(StatisticsPage));
        stats_button.pack(side="right")
        add_button = ctk.CTkButton(header, text="+", width=35,
                                   command=lambda: self.app.navigate_to(AddOrEditHabitPage));
        add_button.pack(side="right", padx=10)
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent");
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.display_habits()

    def display_habits(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        for habit in sorted(self.app.habits, key=lambda h: h.text): HabitCard(self.scroll_frame, habit, self.app).pack(
            fill="x", pady=6)


class AddOrEditHabitPage(Page):
    def __init__(self, master, app_controller, habit=None):
        super().__init__(master, app_controller)
        self.habit, self.is_edit_mode = habit, habit is not None

        header = ctk.CTkFrame(self, fg_color="transparent");
        header.pack(fill="x", padx=10, pady=(20, 10))
        ctk.CTkButton(header, text="Отмена", fg_color="transparent", command=self.app.navigate_back).pack(side="left")
        ctk.CTkLabel(header, text="Изменить" if self.is_edit_mode else "Новая",
                     font=("SF Pro Display", 18, "bold")).pack(side="left", expand=True)
        self.done_button = ctk.CTkButton(header, text="Готово", command=self._save);
        self.done_button.pack(side="right")

        form_frame = ctk.CTkFrame(self, fg_color=("white", "#1C1C1E"), corner_radius=16);
        form_frame.pack(fill="x", padx=20, pady=20)
        main_frame = ctk.CTkFrame(form_frame, fg_color="transparent");
        main_frame.pack(padx=20, pady=20, fill="both", expand=True);
        main_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(main_frame, text="Название").grid(row=0, column=0, sticky="w");
        self.text_entry = ctk.CTkEntry(main_frame, placeholder_text="Выпить воды");
        self.text_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15));
        self.text_entry.bind("<KeyRelease>", self._validate)
        ctk.CTkLabel(main_frame, text="Цель").grid(row=2, column=0, sticky="w");
        self.goal_entry = ctk.CTkEntry(main_frame, placeholder_text="2");
        self.goal_entry.grid(row=3, column=0, sticky="ew", pady=(0, 15), padx=(0, 5));
        self.goal_entry.bind("<KeyRelease>", self._validate)
        ctk.CTkLabel(main_frame, text="Единицы").grid(row=2, column=1, sticky="w");
        self.units_entry = ctk.CTkEntry(main_frame, placeholder_text="литра");
        self.units_entry.grid(row=3, column=1, sticky="ew", pady=(0, 15), padx=(5, 0));
        self.units_entry.bind("<KeyRelease>", self._validate)
        ctk.CTkLabel(main_frame, text="Иконка").grid(row=4, column=0, sticky="w");
        self.icon_menu = ctk.CTkOptionMenu(main_frame, values=AVAILABLE_ICONS);
        self.icon_menu.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        ctk.CTkLabel(main_frame, text="Цвет").grid(row=6, column=0, sticky="w");
        self.color_var = ctk.StringVar();
        color_frame = ctk.CTkFrame(main_frame, fg_color="transparent");
        color_frame.grid(row=7, column=0, columnspan=2, sticky="ew")
        for i, (n, h) in enumerate(COLORS.items()): ctk.CTkRadioButton(color_frame, text="", variable=self.color_var,
                                                                       value=n, width=30, height=30, fg_color=h,
                                                                       border_color=h).grid(row=0, column=i, padx=5)

        if self.is_edit_mode:
            self.text_entry.insert(0, self.habit.text);
            self.goal_entry.insert(0, str(self.habit.goal));
            self.units_entry.insert(0, self.habit.units);
            self.icon_menu.set(self.habit.icon)
            color_name = next((n for n, h in COLORS.items() if h == self.habit.color), list(COLORS.keys())[0]);
            self.color_var.set(color_name)
            ctk.CTkButton(self, text="Удалить привычку", fg_color=DESTRUCTIVE_COLOR, hover_color="#C22B21",
                          command=self._delete).pack(fill="x", padx=20, pady=10, ipady=5)

        self.color_var.set(list(COLORS.keys())[0])
        self._validate()

    def _validate(self, event=None):
        name_ok = len(self.text_entry.get().strip()) > 0
        units_ok = len(self.units_entry.get().strip()) > 0
        goal_ok = False
        try:
            if float(self.goal_entry.get().strip()) > 0: goal_ok = True
        except ValueError:
            pass

        self.text_entry.configure(border_color=ERROR_COLOR if self.text_entry.get() and not name_ok else "gray50")
        self.units_entry.configure(border_color=ERROR_COLOR if self.units_entry.get() and not units_ok else "gray50")
        self.goal_entry.configure(border_color=ERROR_COLOR if self.goal_entry.get() and not goal_ok else "gray50")

        self.done_button.configure(state="normal" if name_ok and units_ok and goal_ok else "disabled")

    def _save(self):
        data = {"text": self.text_entry.get().strip(), "goal": float(self.goal_entry.get().strip()),
                "units": self.units_entry.get().strip(), "icon": self.icon_menu.get(),
                "color": COLORS[self.color_var.get()]}
        self.app._add_or_update_habit(data, self.habit.id if self.is_edit_mode else None)
        self.app.navigate_back()

    def _delete(self):
        ConfirmationDialog(self, title="Удалить привычку",
                           text=f"Вы уверены, что хотите удалить '{self.habit.text}'? Это действие необратимо.",
                           command=lambda: (self.app._delete_habit(self.habit.id), self.app.navigate_back()))


class StatisticsPage(Page):
    def __init__(self, master, app_controller):
        super().__init__(master, app_controller)
        header = ctk.CTkFrame(self, fg_color="transparent");
        header.pack(fill="x", padx=10, pady=(20, 10))
        ctk.CTkButton(header, text="Назад", fg_color="transparent", command=self.app.navigate_back).pack(side="left")
        ctk.CTkLabel(header, text="Сводка за день", font=("SF Pro Display", 18, "bold")).pack(side="left", expand=True)
        self.canvas_frame = ctk.CTkFrame(self, fg_color="transparent");
        self.canvas_frame.pack(fill="both", expand=True, side="top", padx=20, pady=10)
        self.legend_frame = ctk.CTkScrollableFrame(self, label_text="Легенда");
        self.legend_frame.pack(fill="x", side="bottom", padx=20, pady=10, ipady=10, expand=False, anchor="s")
        self.legend_frame.configure(label_font=("SF Pro Display", 14, "bold"))
        self.canvas = ctk.CTkCanvas(self.canvas_frame, highlightthickness=0);
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._update_content)

    def _update_content(self, event=None):
        bg_color = self._apply_appearance_mode(self.cget("fg_color"));
        self.canvas.configure(bg=bg_color)
        self.canvas.delete("all");
        [w.destroy() for w in self.legend_frame.winfo_children()]
        habits = [h for h in self.app.habits if h.get_progress_on(date.today()) > 0]
        if not habits: ctk.CTkLabel(self.canvas, text="Нет прогресса", text_color="gray").place(relx=0.5, rely=0.5,
                                                                                                anchor="center"); return
        total_percent_sum = sum(h.get_progress_percent() for h in habits)
        if total_percent_sum == 0: total_percent_sum = 1
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w <= 1 or h <= 1: return
        size = min(w, h) * 0.7;
        x0, y0 = (w - size) / 2, (h - size) / 2
        start_angle = 90
        for habit in habits:
            percent = habit.get_progress_percent()
            sweep_angle = -(percent / total_percent_sum) * 359.99
            self.canvas.create_arc(x0, y0, x0 + size, y0 + size, start=start_angle, extent=sweep_angle, style="arc",
                                   outline=habit.color, width=40)
            start_angle += sweep_angle
            item_frame = ctk.CTkFrame(self.legend_frame, fg_color="transparent");
            item_frame.pack(fill="x", pady=5)
            ctk.CTkFrame(item_frame, width=20, height=20, fg_color=habit.color, corner_radius=6).pack(side="left",
                                                                                                      padx=10)
            ctk.CTkLabel(item_frame, text=habit.text, font=("SF Pro Display", 16)).pack(side="left", expand=True,
                                                                                        anchor="w")
            ctk.CTkLabel(item_frame, text=f"{percent:.0f}%", font=("SF Pro Display", 16, "bold")).pack(side="right",
                                                                                                       padx=10)