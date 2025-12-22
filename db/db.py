import os

import psycopg
from psycopg.rows import dict_row


class LoggerDB:
    def __init__(self, dsn):
        # Open a single connection
        self.conn = psycopg.connect(
            os.getenv("postgresql://postgres:postgres@db:5432/loggerdb"),
            row_factory=dict_row,
        )
        self.conn.autocommit = True
        self._create_tables_if_missing()

    def __enter__(self):
        # Return the instance so you can call methods on it
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure the connection is closed when leaving the context
        self.conn.close()

    def get_projects(self):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM projects WHERE status = false ORDER BY name ASC"
            )

            return cur.fetchall()

    def get_all_projects(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT name FROM projects ORDER BY name ASC")

            return cur.fetchall()

    def get_project_id(self, project):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM projects WHERE name = %s", ((project,)))
            return cur.fetchone()["id"]

    def get_project_status(self, project):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT status FROM projects WHERE name = %s",
                ((project,)),
            )

            return cur.fetchone()["status"]

    def get_subs(self, project):
        project_id = self.get_project_id(project)
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM subprojects WHERE project_id = %s AND status = false ORDER BY name ASC",
                ((project_id,)),
            )
            return cur.fetchall()

    def get_all_subs(self, project):
        project_id = self.get_project_id(project)
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM subprojects WHERE project_id = %s ORDER BY name ASC",
                ((project_id,)),
            )
            return cur.fetchall()

    def get_subproject_id(self, subproject, project_id):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM subprojects WHERE name = %s AND project_id = %s",
                ((subproject, project_id)),
            )

            return cur.fetchone()["id"]

    def get_subproject_status(self, project_id, subproject):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT status FROM subprojects WHERE project_id = %s AND name =%s",
                ((project_id, subproject)),
            )

            return cur.fetchone()["status"]

    def get_acts(self, project, subproject):
        project_id = self.get_project_id(project)
        sub_id = self.get_subproject_id(subproject, project_id)
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM activities WHERE  sub_id = %s AND project_id = %s AND status = false ORDER BY name ASC",
                ((sub_id, project_id)),
            )

            return cur.fetchall()

    def get_all_acts(self, project, subproject):
        project_id = self.get_project_id(project)
        sub_id = self.get_subproject_id(subproject, project_id)
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM activities WHERE  sub_id = %s AND project_id = %s ORDER BY name",
                ((sub_id, project_id)),
            )

            return cur.fetchall()

    def get_activity_id(self, project_id, subproject_id, activity):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM activities WHERE project_id = %s AND sub_id = %s AND name = %s",
                ((project_id, subproject_id, activity)),
            )
            return cur.fetchone()["id"]

    def get_activity_status(self, project_id, subproject_id, activity):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT status FROM activities WHERE project_id = %s AND sub_id = %s AND name =%s",
                ((project_id, subproject_id, activity)),
            )

            return cur.fetchone()["status"]

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

    def update_project(self, project):
        project_status = not self.get_project_status(project)

        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE projects SET status = %s WHERE name = %s",
                ((project_status, project)),
            )

        self.conn.commit()

    def update_subproject(self, project, subproject):
        project_id = self.get_project_id(project)
        sub_status = not self.get_subproject_status(project_id, subproject)

        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE subprojects SET status = %s WHERE project_id = %s AND name = %s",
                ((sub_status, project_id, subproject)),
            )
        self.conn.commit()

    def update_activity(self, project, subproject, activity):
        project_id = self.get_project_id(project)
        sub_id = self.get_subproject_id(subproject, project_id)
        act_status = not self.get_activity_status(project_id, sub_id, activity)

        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE activities SET status = %s WHERE project_id = %s AND sub_id = %s AND name = %s",
                ((act_status, project_id, sub_id, activity)),
            )
        self.conn.commit()

    def _create_tables_if_missing(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.logs
                (
                    id integer NOT NULL DEFAULT nextval('logs_id_seq'::regclass),
                    project_id integer NOT NULL,
                    subproject_id integer,
                    day character varying(2) COLLATE pg_catalog."default" NOT NULL,
                    month character varying(50) COLLATE pg_catalog."default" NOT NULL,
                    year character varying(4) COLLATE pg_catalog."default",
                    start_time time without time zone NOT NULL,
                    end_time time without time zone NOT NULL,
                    time_spent interval GENERATED ALWAYS AS ((end_time - start_time)) STORED,
                    time_in_minutes integer GENERATED ALWAYS AS (((EXTRACT(epoch FROM (end_time - start_time)) / (60)::numeric))::integer) STORED,
                    time_in_hours numeric GENERATED ALWAYS AS ((round(((EXTRACT(epoch FROM (end_time - start_time)) / 3600.0) / 0.25)) * 0.25)) STORED,
                    hourly_rate integer DEFAULT 0,
                    earnings integer GENERATED ALWAYS AS (((EXTRACT(epoch FROM (end_time - start_time)) / 3600.0) * (hourly_rate)::numeric)) STORED,
                    activity_id integer,
                    CONSTRAINT logs_pkey PRIMARY KEY (id),
                    CONSTRAINT logs_activity_id_fkey FOREIGN KEY (activity_id)
                        REFERENCES public.activities (id) MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION,
                    CONSTRAINT logs_project_fkey FOREIGN KEY (project_id)
                        REFERENCES public.projects (id) MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION,
                    CONSTRAINT logs_subproject_fkey FOREIGN KEY (subproject_id)
                        REFERENCES public.subprojects (id) MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION
                )

                TABLESPACE pg_default;

                ALTER TABLE IF EXISTS public.logs
                    OWNER to postgres;

                """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.projects
                (
                    id integer NOT NULL DEFAULT nextval('projects_id_seq'::regclass),
                    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
                    status boolean NOT NULL DEFAULT false,
                    CONSTRAINT projects_pkey PRIMARY KEY (id),
                    CONSTRAINT unique_project_name UNIQUE (name)
                )

                TABLESPACE pg_default;

                ALTER TABLE IF EXISTS public.projects
                    OWNER to postgres;
                """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.subprojects
                (
                    id integer NOT NULL DEFAULT nextval('subprojects_id_seq'::regclass),
                    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
                    project_id integer,
                    status boolean NOT NULL DEFAULT false,
                    CONSTRAINT subprojects_pkey PRIMARY KEY (id),
                    CONSTRAINT unique_name_and_project UNIQUE (name, project_id),
                    CONSTRAINT subprojects_project_fkey FOREIGN KEY (project_id)
                        REFERENCES public.projects (id) MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION
                )

                TABLESPACE pg_default;

                ALTER TABLE IF EXISTS public.subprojects
                    OWNER to postgres;
                """)
            cur.execute("""

                """)
