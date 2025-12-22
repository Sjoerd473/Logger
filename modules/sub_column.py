import tkinter as tk
from tkinter import messagebox, ttk

import psycopg


class SubprojectColumn(ttk.Frame):
    def __init__(
        self,
        master,
        parent,
        db,
        on_subproject_selected,
        show_error,
    ):
        super().__init__(master, padding=(12, 12, 12, 12))
        self.parent = parent
        self.db = db
        self.on_subproject_selected = on_subproject_selected
        self.show_error = show_error

        self.s_var = tk.StringVar()

        self._build_subproject_column()
        self._bind_subproject_events()

    # -----------------------------
    # SUBPROJECT COLUMN UI
    # -----------------------------
    def _build_subproject_column(self):
        self.grid(column=1, row=0)

        self.s_lbl = ttk.Label(self, text="Subproject:")
        self.s_lbl.grid(column=0, row=0)

        self.s_list = tk.Listbox(self, listvariable=self.s_var, exportselection=False)
        self.s_list.grid(column=0, row=1, rowspan=5)

        self.se_lbl = ttk.Label(self, text="Add a new subproject")
        self.se_lbl.grid(column=0, row=7)

        self.se_ety = ttk.Entry(self)
        self.se_ety.grid(column=0, row=8)

        self.se_btn = ttk.Button(self, text="Add", command=self.add_subproject)
        self.se_btn.grid(column=0, row=9)

    # -----------------------------
    # SUBPROJECT COLUMN EVENTS
    # -----------------------------
    def _bind_subproject_events(self):
        self.s_list.bind("<<ListboxSelect>>", self.update_activities)
        # needs to update activties

    # -----------------------------
    # SUBPROJECT COLUMN LOGIC
    # -----------------------------
    def add_subproject(self):
        p_name = self.parent.project_col.get_selected_project()
        p_subs = [item["name"] for item in self.db.get_subs(p_name)]

        if p_name:
            s_name = self.se_ety.get().strip()
            if s_name in p_subs:
                self.show_error(f"{s_name} already in database!")
            else:
                try:
                    self.se_ety.delete(0, tk.END)
                    self.db.post_sub(s_name, p_name)
                    self.refresh(p_name)
                except psycopg.IntegrityError:
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

    def update_activities(self, event):
        p_name = self.parent.project_col.get_selected_project()
        s_name = self.get_selected_subproject()

        if s_name:
            self.on_subproject_selected(p_name, s_name)
        pass  # unchanged

    def get_selected_subproject(self):
        selection = self.s_list.curselection()
        if selection:
            return self.s_list.get(selection[0])

    def refresh(self, project):
        subs = [item["name"] for item in self.db.get_subs(project)]
        self.s_var.set(subs)
