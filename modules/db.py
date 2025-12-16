import psycopg


class LoggerDB:
    def __init__(self, dsn):
        # Open a single connection
        self.conn = psycopg.connect(dsn)

    def __enter__(self):
        # Return the instance so you can call methods on it
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure the connection is closed when leaving the context
        self.conn.close()

    def get_projects(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT name FROM projects")
            return cur.fetchall()

    def get_project_id(self, project):
        print(project)
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM projects WHERE name = %s", ((project,)))
            return cur.fetchone()

    def get_subproject_id(self, subproject):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM subprojects WHERE name = %s", ((subproject,)))
            return cur.fetchone()

    def get_subs(self, project):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM projects WHERE name = %s", ((project,)))
            result = cur.fetchone()
            cur.execute(
                "SELECT name FROM subprojects WHERE project_id = %s", ((result[0],))
            )
            return cur.fetchall()

    def post_project(self, project):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO projects (name) VALUES (%s)", ((project,)))
            self.conn.commit()

    def post_sub(self, sub, project):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM projects WHERE name = %s", ((project,)))
            result = cur.fetchone()
            cur.execute(
                "INSERT INTO subprojects (name, project_id) VALUES (%s, %s)",
                (sub, result[0]),
            )
            self.conn.commit()

    def post_log(self, data):
        print(data)
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO logs (project, subproject, day, month, year, start_time, end_time) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                ((data[0], data[1], data[2], data[3], data[4], data[5], data[6])),
            )
            self.conn.commit()


# with psycopg.connect("dbname=logger user=postgres password=megablaat") as conn:
#     with conn.cursor() as cur:
#         cur.execute("SELECT * FROM logs")
#         for record in cur:
#             print(record)

#         conn.commit()


# def get_subs(project): ...
# def get_projects():
#     return ["oen", "two"]
