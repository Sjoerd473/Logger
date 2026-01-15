import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import re

from modules.file_writer import FileWriter
from ui.timer_window import TimerWindow
from modules.month_data import MONTHS


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
        show_update_button=False
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
        self.show_update_button= show_update_button
        self.file_writer = FileWriter()

        self.resultsContent = tk.StringVar()
        self.fixedVar = tk.StringVar()
        self.fixedVar.set("Hourly rate")
        self.fixedCheck = tk.IntVar()

        self.fixedVar_timer = tk.StringVar()
        self.fixedVar_timer.set("Hourly rate")
        self.fixedCheck_timer = tk.IntVar()

        self._build_side_column()

    # -----------------------------
    # SIDE COLUMN UI
    # -----------------------------
    def _build_side_column(self):
        self.grid(column=3, row=0)

        if self.show_timer_button:
            self.b_lbl_ety = ttk.Label(self, textvariable=self.fixedVar_timer)
            self.b_lbl_ety.grid(column=0, row=1, columnspan=2, pady=5)

            self.b_chk = ttk.Checkbutton(self, text='Fixed sum', variable=self.fixedCheck_timer, onvalue=1, offvalue=0, command=self.set_income_label_timer)
            self.b_chk.grid(column=3, row=1, padx=(5,0))

            self.b_ety = ttk.Entry(self)
            self.b_ety.grid(column=0, row=2, columnspan=2, pady=5)

            self.b_start_btn = ttk.Button(
                self, text="Start timer", command=self.start_all
            )
            self.b_start_btn.grid(
                column=0, row=7, columnspan=2, rowspan=2, pady=(80, 0)
            )

        elif self.show_update_button:
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

            self.b_refresh_csv_btn = tk.Button(
                self, text="Refresh CSV", command=self.refresh_csv, background="red3"
            )
            self.b_refresh_csv_btn.grid(column=0, row=3, rowspan=2, pady=(20, 20))
        else:
            ...
            # self.us_lbl_title = ttk.Label(self, text="<-- Select a project/subproject/activity")
            # self.us_lbl_title.grid(column=0, row=0, columnspan=3, pady=(20,20), sticky='we')

            self.us_lbl_date = ttk.Label(self, text="Date: YYYY/MM/DD ")
            self.us_lbl_date.grid(column=1, row=1)
            
            self.us_ety_date = ttk.Entry(self)
            self.us_ety_date.grid(column=1, row=2)

            self.us_lbl_start_time = ttk.Label(self, text="Start time: HH:MM:SS")
            self.us_lbl_start_time.grid(column=1, row = 3)

            self.us_ety_start_time = ttk.Entry(self)
            self.us_ety_start_time.grid(column=1, row=4)

            self.us_lbl_end_time = ttk.Label(self, text="End time: HH:MM:SS")
            self.us_lbl_end_time.grid(column=1, row = 5)

            self.us_ety_end_time = ttk.Entry(self)
            self.us_ety_end_time.grid(column=1, row=6)

            self.us_lbl_hourly_rate = ttk.Label(self, textvariable=self.fixedVar)
            self.us_lbl_hourly_rate.grid(column=1, row=7)


            self.us_ety_hourly_rate = ttk.Entry(self)
            self.us_ety_hourly_rate.grid(column=1, row=8)

            self.us_chk = ttk.Checkbutton(self, text='Fixed sum', variable=self.fixedCheck, onvalue=1, offvalue=0, command=self.set_income_label)
            self.us_chk.grid(column=2, row=8, padx=(5,0))

            self.us_btn_submit = ttk.Button(self, text="Insert into DB", command=self.insert_into_db)
            self.us_btn_submit.grid(column=1, row=9)
       

    # -----------------------------
    # SIDE COLUMN LOGIC
    # -----------------------------
    def set_income_label(self):
        if self.fixedCheck.get() == 0:
            self.fixedVar.set("Hourly rate")
        else:
            self.fixedVar.set("Fixed sum")

    def set_income_label_timer(self):
        if self.fixedCheck_timer.get() == 0:
            self.fixedVar_timer.set("Hourly rate")
        else:
            self.fixedVar_timer.set("Fixed sum")

    def get_hourly_rate(self):
        try:
            if self.show_timer_button:
                rate = int(self.b_ety.get().strip())
                fixed = self.fixedCheck_timer.get()
            else:
                rate = int(self.us_ety_hourly_rate.get().strip())
                fixed = self.fixedCheck.get()
                

        except ValueError:
            raise ValueError("Invalid hourly rate")
        if rate < 0:
            raise ValueError("Invalid hourly rate")
        return rate, fixed
    
    def get_date(self):
        date_str = self.us_ety_date.get().strip()

        if not re.match(r"^\d{4}/\d{2}/\d{2}$", date_str):
            raise ValueError("Date must be in YYYY/MM/DD format")

        try:
            dt = datetime.strptime(date_str, "%Y/%m/%d")
        except ValueError:
            raise ValueError("Invalid calendar date")

    # Extract components
        year = dt.year
        month = MONTHS[str(dt.month)]
        day = dt.day

        return date_str, day, month, year



    def get_time(self):
        start_time = self.us_ety_start_time.get().strip()
        end_time = self.us_ety_end_time.get().strip()

        time_pattern = r"^\d{2}:\d{2}:\d{2}$"

        if not re.match(time_pattern, start_time) or not re.match(time_pattern, end_time):
            raise ValueError("Time must be in HH:MM:SS format")

        try:
            datetime.strptime(start_time, "%H:%M:%S")
            datetime.strptime(end_time, "%H:%M:%S")
        except ValueError:
            raise ValueError("Invalid time value")

        return start_time, end_time



    def refresh_csv(self):
        self.file_writer.refresh_file(self.db.get_file_data())
        self.file_writer.backup_everything()

    def get_columns_data(self):
        project = self.project_col.get_selected_project()
        subproject = self.subproject_col.get_selected_subproject()
        activity = self.activity_col.get_selected_activity()
       


        project_id = self.db.get_project_id(project)
        subproject_id = self.db.get_subproject_id(subproject, project_id)
        activity_id = self.db.get_activity_id(project_id, subproject_id, activity)

        return project_id, subproject_id, activity_id
    
    def get_data_to_insert(self):
        date_str, day, month, year = self.get_date()
        start_time, end_time = self.get_time()
        hourly_rate, fixed = self.get_hourly_rate()

        return date_str, day, month, year, start_time, end_time, hourly_rate, fixed
            

    def insert_into_db(self):
        try:
            project_id, subproject_id, activity_id = self.get_columns_data()
            date_str, day, month, year, start_time, end_time, hourly_rate, fixed = self.get_data_to_insert()

        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        except TypeError:
            messagebox.showerror("Missing selection", "Please select a project, subproject, and activity")
            return
        self.us_ety_start_time.delete(0, tk.END)
        self.us_ety_end_time.delete(0, tk.END)
        self.us_ety_hourly_rate.delete(0, tk.END)
        self.db.post_log((project_id, subproject_id, activity_id, day, month, year, date_str, start_time, end_time, hourly_rate, fixed))
        self.file_writer.refresh_file(self.db.get_file_data())
        self.file_writer.backup_everything()
    

    def start_all(self):
        try:
            project = self.project_col.get_selected_project()
            subproject = self.subproject_col.get_selected_subproject()
            activity = self.activity_col.get_selected_activity()

            project_id = self.db.get_project_id(project)
            subproject_id = self.db.get_subproject_id(subproject, project_id)
            activity_id = self.db.get_activity_id(project_id, subproject_id, activity)
            hourly_rate, fixed = self.get_hourly_rate()
            self.b_ety.delete(0, tk.END)

            self.new_row.start_logger(
                project_id, subproject_id, activity_id, hourly_rate, fixed
            )

            TimerWindow(
                self.master,
                project,
                subproject,
                activity,
                hourly_rate,
                fixed,
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
                "Unable to start a timer without choosing a project, subproject, and activity",
            )
    # -----------------------------
    # SIDE COLUMN HELPER FUNCTIONS
    # -----------------------------
