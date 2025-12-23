# Logger App
A simple, portable time‑tracking application built with Python, Tkinter, and SQLite.  
It lets you track work across projects, subprojects, and activities, then exports everything to a clean CSV file for reporting or invoicing.

The app is designed to be easy to run, easy to back up, and easy to share with others — no database server, no Docker, no external dependencies.

---

## Features

### ✔ Track work sessions
- Start and stop a timer for any activity  
- Automatically logs:
  - project  
  - subproject  
  - activity  
  - date  
  - start time  
  - end time  
  - hourly rate  

### ✔ SQLite database (portable & self‑contained)
- All data stored in `logger.db`  
- No installation or server required  
- Safe to copy, move, or back up  

### ✔ CSV export
- Automatically writes each completed log entry to `work_log.csv`  
- Includes:
  - total time spent  
  - minutes  
  - hours  
  - earnings  

### ✔ Backup system
- Creates timestamped backup folders  
- Saves both:
  - `logger.db`  
  - `work_log.csv`  
- Automatically prunes old backups (configurable limit)

### ✔ Clean UI
- Tkinter interface  
- Dropdowns for project, subproject, and activity  
- Buttons to start/stop timer and manage data  

---

## Installation

### Requirements
- Python 3.10+  
- Tkinter (included with most Python installations)

### Run the app
bash
python main.py
The app will automatically create:
- logger.db (SQLite database)
- work_log.csv (CSV export file)
- a backup folder when needed


### Database structure
The app uses SQLite with four tables:
- projects
- subprojects
- activities
- logs
All tables are created automatically on startup if missing.


### Backups
The app creates timestamped backup folders like:
backups/
    logger_backup_2025-01-12_14-33-10/
        logger_backup_2025-01-12_14-33-10.db
        work_log_backup_2025-01-12_14-33-10.csv


You can configure how many backup folders to keep (default: 5).
Older backups are automatically deleted.


### CSV export
Every time you stop the timer, the app writes only the latest log entry to:
~/work_log.csv


### If the file doesn’t exist, it is created with headers.
The CSV includes:
- Id
- Project
- Subproject
- Activity
- Day
- Month
- Year
- Start time
- End time
- Total time spent
- Time spent in minutes
- Time spend in hours
- Hourly rate
- Earnings


### Viewing the database

You can inspect logger.db using:
DB Browser for SQLite (recommended)
https://sqlitebrowser.org/

Or the command line

sqlite3 logger.db
.tables
SELECT * FROM logs;


### Project structure
app/
│
├── main.py
├── db/
│   └── loggerdb.py
├── modules/
│   ├── file_writer.py
│   └── backup_manager.py
├── ui/
│   ├── main_window.py
│   └── timer_window.py
└── logger.db (auto-created)
