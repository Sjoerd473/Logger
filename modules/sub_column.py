import tkinter as tk
from tkinter import messagebox, ttk

import psycopg


class SubprojectColumn(ttk.Frame):
    def __init__(
        self,
        master,
        parent,
        db,
        project_col,
        on_subproject_selected,
        error_row,
        show_add_controls=True,
        show_all=False,
    ):
        super().__init__(master, padding=(12, 12, 12, 12))
        self.parent = parent
        self.db = db
        self.project_col = project_col
        self.on_subproject_selected = on_subproject_selected
        self.error_row = error_row
        self.show_add_controls = show_add_controls
        self.show_all = show_all

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

        if self.show_add_controls:
            self.se_lbl = ttk.Label(self, text="Add a new subproject")
            self.se_lbl.grid(column=0, row=7)

            self.se_ety = ttk.Entry(self)
            self.se_ety.grid(column=0, row=8)

            self.se_btn = ttk.Button(self, text="Add", command=self.add_subproject)
            self.se_btn.grid(column=0, row=9)
        else:
            self.su_lbl = ttk.Label(self, text="Toggle subproject")
            self.su_lbl.grid(column=0, row=7)

            self.su_btn = ttk.Button(
                self, text="Update", command=self.update_subproject
            )
            self.su_btn.grid(column=0, row=9)

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
        p_name = self.project_col.get_selected_project()

        if p_name:
            p_subs = [item["name"] for item in self.db.get_subs(p_name)]
            s_name = self.se_ety.get().strip()
            if s_name in p_subs:
                self.error_row.show_error(f"{s_name} already in database!")
            elif len(s_name) == 0:
                self.error_row.show_error("Invalid name")
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
            self.error_row.show_error("Select a project first")

    def update_activities(self, event):
        p_name = self.project_col.get_selected_project()
        s_name = self.get_selected_subproject()

        if s_name:
            self.on_subproject_selected(p_name, s_name)

    def update_subproject(self):
        p_name = self.project_col.get_selected_project()
        s_name = self.get_selected_subproject()

        if s_name:
            try:
                self.db.update_subproject(p_name, s_name)
                # self.refresh(p_name, s_name) this needs to do something else, update the side window???
            except psycopg.IntegrityError:
                self.db.conn.rollback()
                messagebox.showerror(
                    "Duplicate Activity",
                    f"Subproject '{s_name}' already has an activity named.",
                )
            except Exception as e:
                self.db.conn.rollback()
                messagebox.showerror("Database Error", str(e))
        else:
            self.error_row.show_error("Select a subproject first")

    def get_selected_subproject(self):
        selection = self.s_list.curselection()
        if selection:
            return self.s_list.get(selection[0])

    def refresh(self, project):
        if self.show_all:
            subs = [item["name"] for item in self.db.get_all_subs(project)]
        else:
            subs = [item["name"] for item in self.db.get_subs(project)]
        self.s_var.set(subs)

    def reset(self):
        self.s_var.set([])
