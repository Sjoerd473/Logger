import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.constants import HORIZONTAL

import psycopg
from modules.db import LoggerDB
from modules.row_writer import Add_row
from modules.timer_window import TimerWindow

dsn = "dbname=logger user=postgres password=megablaat"

new_row = Add_row()
db = LoggerDB(dsn)


# layout sizing and positioning,
# get_subrpject_name should return s_name[0], reredo all the functions that depend on it
# return subrpojects without brackets
# make it impossible to add nameless projects
# hourly rate on logs not subproject
# window to mark things complete
# third column for subsubproject
#
# another class for a mark for complete window
#


class App:
    def __init__(self, root):
        self.root = root
        self.db = LoggerDB(dsn)
        self.new_row = Add_row()
        # these _ functions are automatically called when creating the class, thus creating the class creates the window
        self._init_state()
        self._build_ui()
        self._bind_events()

        self._initial_refresh()

    def _init_state(self):
        self.p_var = tk.StringVar()
        self.s_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.resultsContent = tk.StringVar()

    def _build_ui(self):
        self._build_project_column()
        self._build_subproject_column()
        self._build_payment_column()
        self._build_error_label()

    def _bind_events(self):
        self._bind_project_events()
        self._bind_subproject_events()

    def _initial_refresh(self):
        self.refresh_listbox("p")

    # -----------------------------
    # PROJECT COLUMN UI
    # -----------------------------

    def _build_project_column(self):
        # Frame
        self.p_col = ttk.Frame(self.root, padding=(12, 12, 12, 12))
        self.p_col.grid(column=0, row=0, sticky="nwes")

        # Label
        self.p_lbl = ttk.Label(self.p_col, text="Project:")
        self.p_lbl.grid(column=0, row=0)

        # Listbox
        self.p_list = tk.Listbox(
            self.p_col, listvariable=self.p_var, exportselection=False
        )
        self.p_list.grid(column=0, row=1, rowspan=5)

        # Add-project label
        self.pe_lbl = ttk.Label(self.p_col, text="Add a new project")
        self.pe_lbl.grid(column=0, row=6)

        # Entry
        self.pe_ety = ttk.Entry(self.p_col)
        self.pe_ety.grid(column=0, row=7)

        # Button
        self.pe_btn = ttk.Button(self.p_col, text="Add", command=self.add_project)
        self.pe_btn.grid(column=0, row=8)

    # -----------------------------
    # PROJECT COLUMN EVENTS
    # -----------------------------

    def _bind_project_events(self):
        self.p_list.bind("<<ListboxSelect>>", self.update_subprojects)

    # -----------------------------
    # PROJECT COLUMN LOGIC
    # -----------------------------

    def get_selected_project(self):
        selection = self.p_list.curselection()
        if selection:
            return self.p_list.get(selection[0])

    def add_project(self):
        p_name = self.pe_ety.get().strip()

        p_names = [item["name"] for item in self.db.get_projects()]

        if p_name in p_names:
            self.show_error(f"{p_name} already in database!")
            # this needs to fire on a typing event in the box
        else:
            try:
                self.db.post_project(p_name)
                self.pe_ety.delete(0, tk.END)
                self.refresh_listbox("p")
            except psycopg.IntegrityError as e:
                self.db.conn.rollback()
                # does messagebox need self?
                messagebox.showerror(
                    "Duplicate Project", f"Project '{p_name}' already exists."
                )
            except Exception as e:
                self.db.conn.rollback()
                messagebox.showerror("Database Error", str(e))

    def update_subprojects(self, event):
        p_name = self.get_project_name_from_list()

        if p_name:
            new_subs = [item["name"] for item in self.db.get_subs(p_name)]

            self.s_var.set(new_subs)

    # -----------------------------
    # SUBPROJECT COLUMN UI
    # -----------------------------
    def _build_subproject_column(self):
        # Frame
        self.s_col = ttk.Frame(self.root, padding=(12, 12, 12, 12))
        self.s_col.grid(column=1, row=0)
        # Label
        self.s_lbl = ttk.Label(self.s_col, text="Subproject:")
        self.s_lbl.grid(column=0, row=0)
        # Listbox
        self.s_list = tk.Listbox(
            self.s_col, listvariable=self.s_var, exportselection=False
        )
        self.s_list.grid(column=0, row=1, rowspan=5)

        # Add-sub label
        self.se_lbl = ttk.Label(self.s_col, text="Add a new subproject")
        self.se_lbl.grid(column=0, row=7)
        # Entry
        self.se_ety = ttk.Entry(self.s_col)
        self.se_ety.grid(column=0, row=8)
        # Button
        self.se_btn = ttk.Button(self.s_col, text="Add", command=self.add_subproject)
        self.se_btn.grid(column=0, row=9)

    # -----------------------------
    # SUBPROJECT COLUMN EVENTS
    # -----------------------------

    def _bind_subproject_events(self):
        self.s_list.bind("<<ListboxSelect>>", self.update_payment)

    # -----------------------------
    # SUBPROJECT COLUMN LOGIC
    # -----------------------------

    def add_subproject(self):
        p_name = self.get_project_name_from_list()
        p_subs = [item["name"] for item in self.db.get_subs(p_name)]
        if p_name:
            s_name = self.se_ety.get().strip()
            if any(tup[0] == s_name for tup in p_subs):
                self.show_error(f"{s_name} already in database!")
            else:
                try:
                    self.se_ety.delete(0, tk.END)
                    self.db.post_sub(s_name, p_name)

                    self.refresh_listbox("s", p_name)
                except psycopg.IntegrityError as e:
                    self.db.conn.rollback()
                    messagebox.showerror(
                        "Duplicate Subproject",
                        f"Project '{p_name}' already has a subproject named '{s_name}'.",
                    )
                except Exception as e:
                    self.db.conn.rollback()
                    messagebox.showerror("Database Error", str(e))

        else:
            self.show_error("Select a project first")

    def update_payment(self, event): ...

    # part of subproject

    # -----------------------------
    # BUTTON COLUMN UI
    # -----------------------------
    def _build_payment_column(self):
        # Frame
        self.b_col = ttk.Frame(self.root, padding=(12, 12, 12, 12))
        self.b_col.grid(column=2, row=0)
        # Label - text
        self.b_lbl = ttk.Label(self.b_col, text="Hourly rate:")
        self.b_lbl.grid(column=0, row=0)
        # Label - rate
        self.b_lbl_rate = ttk.Label(self.b_col, textvariable=self.resultsContent)
        self.b_lbl_rate.grid(column=1, row=0, sticky="n", pady=(0, 25))
        # Label - update rate
        self.b_lbl_ety = ttk.Label(self.b_col, text="Update hourly rate")
        self.b_lbl_ety.grid(column=0, row=1, columnspan=2, pady=5)
        # Entry - update rate
        self.b_ety = ttk.Entry(self.b_col)
        self.b_ety.grid(column=0, row=2, columnspan=2, pady=5)
        # Button - update rate
        self.b_ety_btn = ttk.Button(
            self.b_col, text="Update", command=self.alter_payment
        )
        self.b_ety_btn.grid(column=0, row=3, columnspan=2, pady=(0, 25))
        # Button - start timer
        self.b_start_btn = ttk.Button(
            self.b_col, text="Start timer", command=self.start_all
        )
        self.b_start_btn.grid(column=0, row=7, columnspan=2, rowspan=2, pady=(80, 0))

    # -----------------------------
    # BUTTON COLUMN EVENTS
    # -----------------------------

    # -----------------------------
    # BUTTON COLUMN LOGIC
    # -----------------------------

    def alter_payment(self):
        ...
        # part of column 3

    def start_all(self):
        try:
            project = self.get_project_name_from_list()
            subproject = self.get_subproject_name_from_list()
            project_id = self.db.get_project_id(project)["id"]

            subproject_id = self.db.get_subproject_id(subproject, project_id)["id"]
            new_row.start_logger(project_id, subproject_id)

            timer = TimerWindow(root, project, subproject, new_row, db)
        except TypeError:
            messagebox.showerror(
                "Missing Subproject",
                "Unable to start a timer without chosing both a project and a subproject",
            )

    # -----------------------------
    # ERROR FRAME UI
    # -----------------------------

    def _build_error_label(self):
        self.error_lbl = ttk.Label(
            self.root, textvariable=self.error_var, foreground="red"
        )
        self.error_lbl.grid(column=0, row=1, columnspan=3)

    # -----------------------------
    # HELPER METHODS
    # -----------------------------

    def remove_error(self):
        self.error_var.set("")

    def show_error(self, msg):
        self.error_var.set(msg)
        root.after(5000, self.remove_error)

    def refresh_listbox(self, cat, project=""):
        if cat == "p":
            projects = [item["name"] for item in self.db.get_projects()]
            self.p_var.set(projects)
        elif cat == "s":
            subs = [item["name"] for item in self.db.get_subs(project)]
            self.s_var.set(subs)

    def get_project_name_from_list(self):
        p_selection = self.p_list.curselection()

        if p_selection:
            p_name = self.p_list.get(p_selection[0])
            return p_name

    def get_subproject_name_from_list(self):
        selection = self.s_list.curselection()

        if selection:
            s_name = self.s_list.get([selection[0]])
            return s_name


# this goes in a different file


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
