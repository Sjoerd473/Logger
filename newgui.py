from tkinter import *
from tkinter import ttk

from modules.db import LoggerDB
from modules.row_writer import Add_row

dsn = "dbname=logger user=postgres password=megablaat"

new_row = Add_row()
db = LoggerDB(dsn)


# niente frutta secca/nocciole
#


def update_projects():
    return db.get_projects()


def update_subprojects(event):
    selected_project = pick_a_project.get()

    subs = db.get_subs(selected_project)

    pick_a_subproject["values"] = subs


def open_timer():
    timer_window = Toplevel(content)

    def stop_timer():
        timer_window.destroy()
        new_row.end_logger()
        db.post_log(new_row.post_data())

    timer_content = ttk.Frame(timer_window)

    # timer = StringVar()
    timer_txt = ttk.Label(timer_window, text="This is where the timer goes")
    project_txt = ttk.Label(timer_window, text="The project")
    subproject_txt = ttk.Label(timer_window, text="The subproject")
    stop_timer_btn = ttk.Button(timer_window, text="Stop Timer", command=stop_timer)

    timer_content.grid(column=0, row=0)
    timer_txt.grid(column=0, row=0, columnspan=2, sticky="we")
    project_txt.grid(column=0, row=1)
    subproject_txt.grid(column=1, row=1)
    stop_timer_btn.grid(column=0, row=2, columnspan=2, sticky="we")


def start_all():
    project = pick_a_project.get()
    subproject = pick_a_subproject.get()
    project_id = db.get_project_id(project)
    subproject_id = db.get_subproject_id(subproject)
    new_row.start_logger(project_id[0], subproject_id[0])
    open_timer()


def add_new():
    t = Toplevel(content)

    def add_to_list():
        # t.destroy()
        project = add_a_project.get()
        sub = add_a_subproject.get()
        if len(sub) > 0:
            db.post_sub(sub, project)
        else:
            db.post_project(project)

    adder_content = ttk.Frame(t)
    project = StringVar()
    project_txt = ttk.Label(adder_content, text="Add a new project")
    subproject_txt = ttk.Label(adder_content, text="Add a new sub-project")
    add_a_project = ttk.Combobox(
        adder_content, textvariable=project, values=update_projects()
    )
    add_a_subproject = ttk.Entry(adder_content)
    add_new_btn = ttk.Button(
        adder_content, text="Add new (sub)Project", command=add_to_list
    )

    adder_content.grid(column=0, row=0)
    project_txt.grid(column=0, row=0)
    subproject_txt.grid(column=1, row=0)
    add_a_project.grid(column=0, row=1)
    add_a_subproject.grid(column=1, row=1)
    add_new_btn.grid(column=0, row=2, columnspan=2, sticky="ew")


def start_timer(): ...


root = Tk()

content = ttk.Frame(root)
add_new_btn = ttk.Button(content, text="Add New", command=add_new)

project = StringVar()
subproject = StringVar()
project_txt = ttk.Label(content, text="Pick a project")
subproject_txt = ttk.Label(content, text="Pick a sub-project")
pick_a_project = ttk.Combobox(
    content, textvariable=project, values=update_projects(), state="readonly"
)

pick_a_project.bind("<<ComboboxSelected>>", update_subprojects)


pick_a_subproject = ttk.Combobox(content, textvariable=subproject, state="readonly")

start_timer_btn = ttk.Button(content, text="Start the Timer!", command=start_all)

content.grid(column=0, row=0)
add_new_btn.grid(column=0, row=0, columnspan=2, sticky="ew")
project_txt.grid(column=0, row=1)
subproject_txt.grid(column=1, row=1)
pick_a_project.grid(column=0, row=2)
pick_a_subproject.grid(column=1, row=2)
start_timer_btn.grid(column=0, row=3, columnspan=2, rowspan=2, sticky="ew")

root.mainloop()
