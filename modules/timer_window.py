import time
import tkinter as tk
from tkinter import messagebox, ttk

from modules.file_writer import print_to_file, refresh_file


class TimerWindow:
    def __init__(self, parent, project, subproject, hourly_rate, new_row, db):
        self.parent = parent
        self.project = project
        self.subproject = subproject
        self.hourly_rate = hourly_rate
        self.new_row = new_row
        self.db = db

        self.timer_window = tk.Toplevel(parent)
        self.running = True
        self.start_time = time.time()

        self._build_ui()
        self._update_timer()

    def _update_timer(self):
        if self.running:
            elapsed = int(time.time() - self.start_time)
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_txt.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
            self.timer_window.after(1000, self._update_timer)

    def _build_ui(self):
        self._build_timer_frame()

    def _build_timer_frame(self):
        # Frame

        self.timer_content = ttk.Frame(self.timer_window, padding=(12, 2, 12, 2))
        self.timer_content.grid(column=0, row=0, padx=15, pady=15)

        # Label - timer
        self.timer_lbl = ttk.Label(self.timer_content, text="You have been working for")
        self.timer_lbl.grid(column=0, row=0)

        # Label - clock
        self.timer_txt = ttk.Label(self.timer_content, text="00:00:00")
        self.timer_txt.grid(column=1, row=0, sticky="we")

        # Label - rate text
        self.rate_txt = ttk.Label(self.timer_content, text="With an hourly rate of: ")
        self.rate_txt.grid(column=2, row=0)
        # Label - rate number
        self.rate_num = ttk.Label(self.timer_content, text=f"{self.hourly_rate}€")
        self.rate_num.grid(column=3, row=0)

        # Label - project
        self.project_txt = ttk.Label(
            self.timer_content, text=f"The project you are working on is {self.project}"
        )
        self.project_txt.grid(column=0, row=1, pady=10, padx=(5, 5))

        # Label - sub
        self.subproject_txt = ttk.Label(
            self.timer_content,
            text=f"The subproject you working on is {self.subproject}",
        )
        self.subproject_txt.grid(column=2, row=1, pady=10, padx=(5, 5))

        # Button - stop timer
        self.stop_timer_btn = ttk.Button(
            self.timer_content, text="Stop Timer", command=self.stop_timer
        )
        self.stop_timer_btn.grid(
            column=0, row=2, columnspan=3, sticky="we", pady=(10, 0)
        )

    # -----------------------------
    # BUTTON COLUMN LOGIC

    # -----------------------------
    def stop_timer(self):
        try:
            self.timer_window.destroy()
            self.new_row.end_logger()
            self.db.post_log(self.new_row.post_data())
            print_to_file(self.db.get_file_data())
        except IndexError:
            messagebox.showerror(
                "Database Error",
                "Something went wrong trying to write the data to a file.",
            )
