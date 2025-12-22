import tkinter as tk
from tkinter import messagebox, ttk

from ui.timer_window import TimerWindow


# needs to get:
# project name + status
# sub name + status
# activity name + status
class SideColumn(ttk.Frame):
    def __init__(
        self,
        master,
        parent,
        db,
        project_col,
        sub_col,
        activity_col,
        new_row,
        error_row,
        show_timer_button=True,
    ):
        super().__init__(master, padding=(12, 12, 12, 12))
        self.parent = parent
        self.db = db
        self.new_row = new_row
        self.project_col = project_col
        self.subproject_col = sub_col
        self.activity_col = activity_col
        self.error_row = error_row
        self.show_timer_button = show_timer_button

        self.resultsContent = tk.StringVar()

        self._build_side_column()

    # -----------------------------
    # SIDE COLUMN UI
    # -----------------------------
    def _build_side_column(self):
        self.grid(column=3, row=0)

        if self.show_timer_button:
            self.b_lbl_ety = ttk.Label(self, text="Set hourly rate")
            self.b_lbl_ety.grid(column=0, row=1, columnspan=2, pady=5)

            self.b_ety = ttk.Entry(self)
            self.b_ety.grid(column=0, row=2, columnspan=2, pady=5)

            self.b_start_btn = ttk.Button(
                self, text="Start timer", command=self.start_all
            )
            self.b_start_btn.grid(
                column=0, row=7, columnspan=2, rowspan=2, pady=(80, 0)
            )
        else:
            self.ps_lbl = ttk.Label(self, text="Project status: ")
            self.ps_lbl.grid(column=0, row=0)

            self.ps_lbl_status = ttk.Label(self, textvariable=self.project_col.ps_var)
            self.ps_lbl_status.grid(column=1, row=0)

            self.ss_lbl = ttk.Label(self, text="Subproject status: ")
            self.ss_lbl.grid(column=0, row=1)

            self.ss_lbl_status = ttk.Label(
                self, textvariable=self.subproject_col.ss_var
            )
            self.ss_lbl_status.grid(column=1, row=1)

            self.as_lbl = ttk.Label(self, text="Activity status: ")
            self.as_lbl.grid(column=0, row=2)

            self.as_lbl_status = ttk.Label(self, textvariable=self.activity_col.as_var)
            self.as_lbl_status.grid(column=1, row=2)

    # -----------------------------
    # SIDE COLUMN LOGIC
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
            project = self.project_col.get_selected_project()
            subproject = self.subproject_col.get_selected_subproject()
            activity = self.activity_col.get_selected_activity()

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
