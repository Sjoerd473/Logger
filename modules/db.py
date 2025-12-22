import psycopg
from psycopg.rows import dict_row


class LoggerDB:
    def __init__(self, dsn):
        # Open a single connection
        self.conn = psycopg.connect(dsn, row_factory=dict_row)

    def __enter__(self):
        # Return the instance so you can call methods on it
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure the connection is closed when leaving the context
        self.conn.close()

    def get_projects(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT name FROM projects ORDER BY name ASC")

            return cur.fetchall()

    def get_project_id(self, project):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM projects WHERE name = %s", ((project,)))
            return cur.fetchone()["id"]

    def get_subproject_id(self, subproject, project_id):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM subprojects WHERE name = %s AND project_id = %s",
                ((subproject, project_id)),
            )

            return cur.fetchone()["id"]

    def get_activity_id(self, project_id, subproject_id, activity):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM activities WHERE sub_id = %s AND project_id = %s AND name = %s",
                ((subproject_id, project_id, activity)),
            )
            return cur.fetchone()["id"]

    def get_subs(self, project):
        project_id = self.get_project_id(project)
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM subprojects WHERE project_id = %s ORDER BY name ASC",
                ((project_id,)),
            )
            return cur.fetchall()

    def get_acts(self, project, subproject):
        project_id = self.get_project_id(project)
        sub_id = self.get_subproject_id(subproject, project_id)
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM activities WHERE  sub_id = %s AND project_id = %s",
                ((sub_id, project_id)),
            )

            return cur.fetchall()

    def get_file_data(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """SELECT logs.id, p.name AS project_name, s.name AS subproject_name,
                a.name AS activity_name, day, month, year, start_time, end_time, time_spent,
                time_in_minutes, hourly_rate, earnings, time_in_hours FROM logs
                JOIN projects AS p on logs.project_id = p.id
                JOIN subprojects AS s ON logs.subproject_id = s.id
                JOIN activities AS a ON logs.activity_id = a.id
                """
            )

            return cur.fetchall()

    def get_hourly(self, sub):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT retribuizione FROM subprojects WHERE name = %s", ((sub,))
            )
            return cur.fetchone()

    def post_project(self, project):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO projects (name) VALUES (%s)", ((project,)))
            self.conn.commit()

    def post_sub(self, sub, project):
        project_id = self.get_project_id(project)
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO subprojects (name, project_id) VALUES (%s, %s)",
                (sub, project_id),
            )
            self.conn.commit()

    def post_act(self, activity, project, sub):
        project_id = self.get_project_id(project)
        sub_id = self.get_subproject_id(sub, project_id)
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO activities (name, sub_id, project_id) VALUES (%s, %s, %s)",
                ((activity, sub_id, project_id)),
            )
        self.conn.commit()

    def post_log(self, data):
        print(data)
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO logs (project_id, subproject_id, activity_id, day, month, year, start_time, end_time,hourly_rate) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    (
                        data[0],
                        data[1],
                        data[2],
                        data[3],
                        data[4],
                        data[5],
                        data[6],
                        data[7],
                        data[8],
                    )
                ),
            )
            self.conn.commit()

    def update_hourly(self, n, sub):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE subprojects SET retribuizione = %s WHERE name = %s", ((n, sub))
            )

            self.conn.commit()
