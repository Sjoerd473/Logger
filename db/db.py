import sqlite3


class LoggerDB:
    def __init__(self, path="logger.db"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._create_tables_if_missing()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    # ---------------------------------------------------------
    # TABLE CREATION
    # ---------------------------------------------------------
    def _create_tables_if_missing(self):
        cur = self.conn.cursor()

        cur.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            status INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS subprojects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            project_id INTEGER NOT NULL,
            status INTEGER NOT NULL DEFAULT 0,
            UNIQUE(name, project_id),
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sub_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            status INTEGER NOT NULL DEFAULT 0,
            UNIQUE(name, sub_id, project_id),
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY(sub_id) REFERENCES subprojects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            subproject_id INTEGER,
            activity_id INTEGER,
            day TEXT NOT NULL,
            month TEXT NOT NULL,
            year TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            hourly_rate INTEGER DEFAULT 0,
            FOREIGN KEY(project_id) REFERENCES projects(id),
            FOREIGN KEY(subproject_id) REFERENCES subprojects(id),
            FOREIGN KEY(activity_id) REFERENCES activities(id)
        );
        """)

        self.conn.commit()

    # ---------------------------------------------------------
    # PROJECTS
    # ---------------------------------------------------------
    def get_projects(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM projects WHERE status = 0 ORDER BY name ASC")
        return cur.fetchall()

    def get_all_projects(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM projects ORDER BY name ASC")
        return cur.fetchall()

    def get_project_id(self, project):
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM projects WHERE name = ?", (project,))
        row = cur.fetchone()
        return row["id"] if row else None

    def get_project_status(self, project):
        cur = self.conn.cursor()
        cur.execute("SELECT status FROM projects WHERE name = ?", (project,))
        return cur.fetchone()["status"]

    # ---------------------------------------------------------
    # SUBPROJECTS
    # ---------------------------------------------------------
    def get_subs(self, project):
        project_id = self.get_project_id(project)
        cur = self.conn.cursor()
        cur.execute(
            "SELECT name FROM subprojects WHERE project_id = ? AND status = 0 ORDER BY name ASC",
            (project_id,),
        )
        return cur.fetchall()

    def get_all_subs(self, project):
        project_id = self.get_project_id(project)
        cur = self.conn.cursor()
        cur.execute(
            "SELECT name FROM subprojects WHERE project_id = ? ORDER BY name ASC",
            (project_id,),
        )
        return cur.fetchall()

    def get_subproject_id(self, subproject, project_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id FROM subprojects WHERE name = ? AND project_id = ?",
            (subproject, project_id),
        )
        return cur.fetchone()["id"]

    def get_subproject_status(self, project_id, subproject):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT status FROM subprojects WHERE project_id = ? AND name = ?",
            (project_id, subproject),
        )
        return cur.fetchone()["status"]

    # ---------------------------------------------------------
    # ACTIVITIES
    # ---------------------------------------------------------
    def get_acts(self, project, subproject):
        project_id = self.get_project_id(project)
        sub_id = self.get_subproject_id(subproject, project_id)

        cur = self.conn.cursor()
        cur.execute(
            "SELECT name FROM activities WHERE sub_id = ? AND project_id = ? AND status = 0 ORDER BY name ASC",
            (sub_id, project_id),
        )
        return cur.fetchall()

    def get_all_acts(self, project, subproject):
        project_id = self.get_project_id(project)
        sub_id = self.get_subproject_id(subproject, project_id)

        cur = self.conn.cursor()
        cur.execute(
            "SELECT name FROM activities WHERE sub_id = ? AND project_id = ? ORDER BY name ASC",
            (sub_id, project_id),
        )
        return cur.fetchall()

    def get_activity_id(self, project_id, subproject_id, activity):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id FROM activities WHERE project_id = ? AND sub_id = ? AND name = ?",
            (project_id, subproject_id, activity),
        )
        return cur.fetchone()["id"]

    def get_activity_status(self, project_id, subproject_id, activity):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT status FROM activities WHERE project_id = ? AND sub_id = ? AND name = ?",
            (project_id, subproject_id, activity),
        )
        return cur.fetchone()["status"]

    # ---------------------------------------------------------
    # LOGS
    # ---------------------------------------------------------
    def get_file_data(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT logs.id, p.name AS project_name, s.name AS subproject_name,
                   a.name AS activity_name, day, month, year,
                   start_time, end_time, hourly_rate
            FROM logs
            JOIN projects p ON logs.project_id = p.id
            JOIN subprojects s ON logs.subproject_id = s.id
            JOIN activities a ON logs.activity_id = a.id
        """)

        return cur.fetchall()

    def get_last_log(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT logs.id, p.name AS project_name, s.name AS subproject_name,
                   a.name AS activity_name, day, month, year,
                   start_time, end_time, hourly_rate
            FROM logs
            JOIN projects p ON logs.project_id = p.id
            JOIN subprojects s ON logs.subproject_id = s.id
            JOIN activities a ON logs.activity_id = a.id
            ORDER BY logs.id DESC
            LIMIT 1
        """)

        return cur.fetchone()

    # ---------------------------------------------------------
    # INSERTS
    # ---------------------------------------------------------
    def post_project(self, project):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO projects (name) VALUES (?)", (project,))
        self.conn.commit()

    def post_sub(self, sub, project):
        project_id = self.get_project_id(project)
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO subprojects (name, project_id) VALUES (?, ?)",
            (sub, project_id),
        )
        self.conn.commit()

    def post_act(self, activity, project, sub):
        project_id = self.get_project_id(project)
        sub_id = self.get_subproject_id(sub, project_id)

        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO activities (name, sub_id, project_id) VALUES (?, ?, ?)",
            (activity, sub_id, project_id),
        )
        self.conn.commit()

    def post_log(self, data):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO logs (project_id, subproject_id, activity_id, day, month, year,
                              start_time, end_time, hourly_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            tuple(data),
        )
        self.conn.commit()

    # ---------------------------------------------------------
    # UPDATES
    # ---------------------------------------------------------
    def update_project(self, project):
        status = 1 - self.get_project_status(project)
        cur = self.conn.cursor()
        cur.execute("UPDATE projects SET status = ? WHERE name = ?", (status, project))
        self.conn.commit()

    def update_subproject(self, project, subproject):
        project_id = self.get_project_id(project)
        status = 1 - self.get_subproject_status(project_id, subproject)

        cur = self.conn.cursor()
        cur.execute(
            "UPDATE subprojects SET status = ? WHERE project_id = ? AND name = ?",
            (status, project_id, subproject),
        )
        self.conn.commit()

    def update_activity(self, project, subproject, activity):
        project_id = self.get_project_id(project)
        sub_id = self.get_subproject_id(subproject, project_id)
        status = 1 - self.get_activity_status(project_id, sub_id, activity)

        cur = self.conn.cursor()
        cur.execute(
            "UPDATE activities SET status = ? WHERE project_id = ? AND sub_id = ? AND name = ?",
            (status, project_id, sub_id, activity),
        )
        self.conn.commit()
