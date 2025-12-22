import tkinter as tk
from tkinter import messagebox, ttk

import psycopg


class ActivityColumn(ttk.Frame):
    def __init__(self, master, parent, db, show_error):
        super().__init__(master, padding=(12, 12, 12, 12))
        self.parent = parent
        self.db = db
        self.show_error = show_error

        self.a_var = tk.StringVar()

        self._build_activity_column()
        # self._bind_activity_events()

    # -----------------------------
    # ACTIVITY COLUMN UI
    # -----------------------------

    def _build_activity_column(self):
        self.grid(column=2, row=0)

        self.a_lbl = ttk.Label(self, text="Activity:")
        self.a_lbl.grid(column=0, row=0)

        self.a_list = tk.Listbox(self, listvariable=self.a_var, exportselection=False)
        self.a_list.grid(column=0, row=1, rowspan=5)

        self.ae_lbl = ttk.Label(self, text="Add a new activity")
        self.ae_lbl.grid(column=0, row=7)

        self.ae_ety = ttk.Entry(self)
        self.ae_ety.grid(column=0, row=8)

        self.ae_btn = ttk.Button(self, text="Add", command=self.add_activity)
        self.ae_btn.grid(column=0, row=9)

    # -----------------------------
    # ACTIVITY COLUMN EVENTS
    # -----------------------------
    #

    # -----------------------------
    # ACTIVITY COLUMN LOGIC
    # -----------------------------

    def add_activity(self):
        s_name = self.parent.subproject_col.get_selected_subproject()
        p_name = self.parent.project_col.get_selected_project()
        s_acts = [item["name"] for item in self.db.get_acts(p_name, s_name)]

        if s_name:
            a_name = self.ae_ety.get().strip()
            if a_name in s_acts:
                self.show_error(f"{a_name} already in database!")
            else:
                try:
                    self.ae_ety.delete(0, tk.END)
                    self.db.post_act(a_name, p_name, s_name)
                    self.refresh(p_name, s_name)
                except psycopg.IntegrityError:
                    self.db.conn.rollback()
                    messagebox.showerror(
                        "Duplicate Activity",
                        f"Subproject '{s_name}' already has an activity named '{a_name}'.",
                    )
                except Exception as e:
                    self.db.conn.rollback()
                    messagebox.showerror("Database Error", str(e))
        else:
            self.show_error("Select a subproject first")

    def get_selected_activity(self):
        selection = self.a_list.curselection()
        if selection:
            return self.a_list.get(selection[0])

    def refresh(self, project, subproject):
        acts = [item["name"] for item in self.db.get_acts(project, subproject)]
        self.a_var.set(acts)
