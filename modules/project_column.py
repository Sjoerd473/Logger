import tkinter as tk
from tkinter import messagebox, ttk

import psycopg


class ProjectColumn(ttk.Frame):
    def __init__(self, master, parent, db, on_project_selected, show_error):
        super().__init__(master, padding=(12, 12, 12, 12))
        self.parent = parent
        self.db = db
        self.on_project_selected = on_project_selected
        self.show_error = show_error

        self._build_project_column()
        self._bind_project_events()

    # -----------------------------
    # PROJECT COLUMN UI
    # -----------------------------
    def _build_project_column(self):
        self.grid(column=0, row=0, sticky="nwes")

        self.p_var = tk.StringVar()

        self.p_lbl = ttk.Label(self, text="Project:")
        self.p_lbl.grid(column=0, row=0)

        self.p_list = tk.Listbox(self, listvariable=self.p_var, exportselection=False)
        self.p_list.grid(column=0, row=1, rowspan=5)

        self.pe_lbl = ttk.Label(self, text="Add a new project")
        self.pe_lbl.grid(column=0, row=6)

        self.pe_ety = ttk.Entry(self)
        self.pe_ety.grid(column=0, row=7)

        self.pe_btn = ttk.Button(self, text="Add", command=self.add_project)
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
        else:
            try:
                self.db.post_project(p_name)
                self.pe_ety.delete(0, tk.END)
                self.refresh()
            except psycopg.IntegrityError:
                self.db.conn.rollback()
                messagebox.showerror(
                    "Duplicate Project", f"Project '{p_name}' already exists."
                )
            except Exception as e:
                self.db.conn.rollback()
                messagebox.showerror("Database Error", str(e))

    def update_subprojects(self, event):
        p_name = self.get_selected_project()
        if p_name:
            # new_subs = [item["name"] for item in self.db.get_subs(p_name)]
            # print(new_subs)
            self.on_project_selected(p_name)

    def refresh(self):
        projects = [item["name"] for item in self.db.get_projects()]
        self.p_var.set(projects)
