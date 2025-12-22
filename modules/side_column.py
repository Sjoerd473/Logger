import tkinter as tk
from tkinter import messagebox, ttk

from modules.timer_window import TimerWindow


class SideColumn(ttk.Frame):
    def __init__(self, master, parent, db, new_row, show_error, show_add_controls=True):
        super().__init__(master, padding=(12, 12, 12, 12))
        self.parent = parent
        self.db = db
        self.new_row = new_row
        self.show_error = show_error

        self.resultsContent = tk.StringVar()

        self._build_payment_column()

    # -----------------------------
    # PAYMENT COLUMN UI
    # -----------------------------
    def _build_payment_column(self):
        self.grid(column=3, row=0)

        self.b_lbl_rate = ttk.Label(self, textvariable=self.resultsContent)
        self.b_lbl_rate.grid(column=1, row=0, sticky="n", pady=(0, 25))

        self.b_lbl_ety = ttk.Label(self, text="Set hourly rate")
        self.b_lbl_ety.grid(column=0, row=1, columnspan=2, pady=5)

        self.b_ety = ttk.Entry(self)
        self.b_ety.grid(column=0, row=2, columnspan=2, pady=5)

        self.b_start_btn = ttk.Button(self, text="Start timer", command=self.start_all)
        self.b_start_btn.grid(column=0, row=7, columnspan=2, rowspan=2, pady=(80, 0))

    # -----------------------------
    # PAYMENT COLUMN LOGIC
    # -----------------------------
    def get_hourly_rate(self):
        try:
            rate = int(self.b_ety.get().strip())
        except ValueError:
            raise ValueError("Invalid hourly rate")
        if rate < 0:
            raise ValueError("Invalid hourly rate")
        return rate

    def start_all(self):
        try:
            project = self.parent.project_col.get_selected_project()
            subproject = self.parent.subproject_col.get_selected_subproject()
            activity = self.parent.activity_col.get_selected_activity()

            project_id = self.db.get_project_id(project)
            hourly_rate = self.get_hourly_rate()
            subproject_id = self.db.get_subproject_id(subproject, project_id)
            activity_id = self.db.get_activity_id(project_id, subproject_id, activity)

            self.new_row.start_logger(
                project_id, subproject_id, activity_id, hourly_rate
            )

            TimerWindow(
                self.master,
                project,
                subproject,
                activity,
                hourly_rate,
                self.new_row,
                self.db,
            )

        except ValueError:
            messagebox.showerror(
                "Invalid hourly rate",
                "Unable to start a timer with an invalid hourly rate",
            )
        except TypeError:
            messagebox.showerror(
                "Missing Subproject",
                "Unable to start a timer without choosing both a project and a subproject",
            )
