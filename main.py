import time
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.constants import HORIZONTAL

import psycopg
from modules.db import LoggerDB
from modules.file_writer import print_to_file, refresh_file
from modules.row_writer import Add_row

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


# modify for dicts?
def refresh_listbox(cat, project=""):
    if cat == "p":
        projects = [item["name"] for item in db.get_projects()]
        p_var.set(projects)
    elif cat == "s":
        subs = [item["name"] for item in db.get_subs(project)]
        s_var.set(subs)


def get_project_name_from_list():
    p_selection = p_list.curselection()

    if p_selection:
        p_name = p_list.get(p_selection[0])
        return p_name


def get_subproject_name_from_list():
    selection = s_list.curselection()

    if selection:
        s_name = s_list.get([selection[0]])
        return s_name


def remove_error():
    error_var.set("")


def show_error(msg):
    error_var.set(msg)
    root.after(5000, remove_error)


# def validate_name(p_name):
#     if p_name in projects:
#         show_error(f"{p_name} already in database!")


# def schedule_check(event):
#     root.after_cancel(schedule_check.job) if hasattr(schedule_check, "job") else None
#     schedule_check.job = root.after(300, lambda: validate_name(pe_ety.get().strip()))


# pe_ety.bind("<KeyRelease>", schedule_check)


def add_project():
    p_name = pe_ety.get().strip()

    p_names = [item["name"] for item in db.get_projects()]

    if p_name in p_names:
        show_error(f"{p_name} already in database!")
        # this needs to fire on a typing event in the box
    else:
        try:
            db.post_project(p_name)
            pe_ety.delete(0, tk.END)
            refresh_listbox("p")
        except psycopg.IntegrityError as e:
            db.conn.rollback()
            messagebox.showerror(
                "Duplicate Project", f"Project '{p_name}' already exists."
            )
        except Exception as e:
            db.conn.rollback()
            messagebox.showerror("Database Error", str(e))


def add_subproject():
    p_name = get_project_name_from_list()
    p_subs = [item["name"] for item in db.get_subs(p_name)]
    if p_name:
        s_name = se_ety.get().strip()
        if any(tup[0] == s_name for tup in p_subs):
            show_error(f"{s_name} already in database!")
        else:
            try:
                se_ety.delete(0, tk.END)
                db.post_sub(s_name, p_name)

                refresh_listbox("s", p_name)
            except psycopg.IntegrityError as e:
                db.conn.rollback()
                messagebox.showerror(
                    "Duplicate Subproject",
                    f"Project '{p_name}' already has a subproject named '{s_name}'.",
                )
            except Exception as e:
                db.conn.rollback()
                messagebox.showerror("Database Error", str(e))

    else:
        show_error("Select a project first")


def update_subprojects(event):
    p_name = get_project_name_from_list()

    if p_name:
        new_subs = [item["name"] for item in db.get_subs(p_name)]

        s_var.set(new_subs)


# change for payment from logs
def update_payment(event):
    s_name = get_subproject_name_from_list()

    if s_name:
        hourly_rate = db.get_hourly(s_name)["retribuizione"]

        resultsContent.set(f"{hourly_rate}€")


# change for payment from logs
def alter_payment():
    s_name = get_subproject_name_from_list()

    if s_name:
        n = b_ety.get().strip()
        try:
            hourly = int(n)

            if hourly <= 0:
                raise ValueError
            b_ety.delete(0, tk.END)
            db.update_hourly(n, s_name[0])
            refresh_file(db.get_file_data())
            update_payment("")
        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "The hourly rate you entered must be a whole, positive, number.",
            )
        except Exception as e:
            messagebox.showerror("Database Error", str(e))


def open_timer(project, subproject):
    timer_window = tk.Toplevel(root)
    running = True
    start_time = time.time()

    def update_timer_txt():
        if running:
            elapsed = int(time.time() - start_time)
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_txt.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
            timer_window.after(1000, update_timer_txt)

    def stop_timer():
        try:
            timer_window.destroy()
            new_row.end_logger()
            db.post_log(new_row.post_data())
            print_to_file(db.get_file_data())
        except IndexError:
            messagebox.showerror(
                "Database Error",
                "Something went wrong trying to write the data to a file.",
            )

    timer_content = ttk.Frame(timer_window, padding=(12, 12, 12, 12))

    # timer = StringVar()
    timer_lbl = ttk.Label(timer_window, text="You have been working for")
    timer_txt = ttk.Label(timer_window, text="00:00:00")
    project_txt = ttk.Label(
        timer_window, text=f"The project you are working on is {project}"
    )
    subproject_txt = ttk.Label(
        timer_window, text=f"The subproject you working on is {subproject}"
    )
    stop_timer_btn = ttk.Button(timer_window, text="Stop Timer", command=stop_timer)

    timer_content.grid(column=0, row=0, padx=15, pady=15)
    timer_lbl.grid(column=0, row=0)
    timer_txt.grid(column=1, row=0, columnspan=2, sticky="we")
    project_txt.grid(column=0, row=1, pady=10, padx=(5, 5))
    subproject_txt.grid(column=1, row=1, pady=10, padx=(5, 5))
    stop_timer_btn.grid(column=0, row=2, columnspan=2, sticky="we", pady=(10, 0))

    update_timer_txt()


def start_all():
    try:
        project = get_project_name_from_list()
        subproject = get_subproject_name_from_list()
        project_id = db.get_project_id(project)["id"]

        subproject_id = db.get_subproject_id(subproject, project_id)["id"]
        new_row.start_logger(project_id, subproject_id)
        open_timer(project, subproject)
    except TypeError:
        messagebox.showerror(
            "Missing Subproject",
            "Unable to start a timer without chosing both a project and a subproject",
        )


root = tk.Tk()
root.title("Am I working too much?")

p_col = ttk.Frame(root, padding=(12, 12, 12, 12))
s_col = ttk.Frame(root, padding=(12, 12, 12, 12))
b_col = ttk.Frame(root, padding=(12, 12, 12, 12))


p_var = tk.StringVar(value=[item["name"] for item in db.get_projects()])
s_var = tk.StringVar(value=[])

p_lbl = ttk.Label(p_col, text="Project:")
p_list = tk.Listbox(p_col, listvariable=p_var, exportselection=False)
p_bar = ttk.Separator(p_col, orient=HORIZONTAL)
pe_lbl = ttk.Label(p_col, text="Add a new project")
pe_ety = ttk.Entry(p_col)
pe_btn = ttk.Button(p_col, text="Add", command=add_project)

p_list.bind("<<ListboxSelect>>", update_subprojects)

s_lbl = ttk.Label(s_col, text="Subproject:")
s_list = tk.Listbox(s_col, listvariable=s_var, exportselection=False)
s_bar = ttk.Separator(s_col, orient=HORIZONTAL)
se_lbl = ttk.Label(s_col, text="Add a new subproject")
se_ety = ttk.Entry(s_col)
se_btn = ttk.Button(s_col, text="Add", command=add_subproject)

s_list.bind("<<ListboxSelect>>", update_payment)

resultsContent = tk.StringVar()
b_lbl = ttk.Label(b_col, text="Hourly rate:")
b_lbl_rate = ttk.Label(b_col, textvariable=resultsContent)
b_lbl_ety = ttk.Label(b_col, text="Update hourly rate")
b_ety = ttk.Entry(b_col)
b_ety_btn = ttk.Button(b_col, text="Update", command=alter_payment)
b_start_btn = ttk.Button(b_col, text="Start timer", command=start_all)

error_var = tk.StringVar()

error_lbl = ttk.Label(root, textvariable=error_var, foreground="red")


p_col.grid(column=0, row=0, sticky="nwes")
p_lbl.grid(column=0, row=0)
p_list.grid(column=0, row=1, rowspan=5)
p_bar.grid(column=0, row=6, pady=5)
pe_lbl.grid(column=0, row=7)
pe_ety.grid(column=0, row=8)
pe_btn.grid(column=0, row=9)

s_col.grid(column=1, row=0)
s_lbl.grid(column=0, row=0)
s_list.grid(column=0, row=1, rowspan=5)
s_bar.grid(column=0, row=6, pady=5)
se_lbl.grid(column=0, row=7)
se_ety.grid(column=0, row=8)
se_btn.grid(column=0, row=9)

b_col.grid(column=2, row=0)
b_lbl.grid(column=0, row=0, sticky="n", pady=(0, 25))
b_lbl_rate.grid(column=1, row=0, sticky="n", pady=(0, 25))
b_lbl_ety.grid(column=0, row=1, columnspan=2, pady=5)
b_ety.grid(column=0, row=2, columnspan=2, pady=5)
b_ety_btn.grid(column=0, row=3, columnspan=2, pady=(0, 25))
b_start_btn.grid(column=0, row=7, columnspan=2, rowspan=2, pady=(80, 0))

error_lbl.grid(column=0, row=1, columnspan=3)

root.mainloop()
