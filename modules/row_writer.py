import time as time
from datetime import datetime


class Add_row:
    def __init__(self): ...

    def start_logger(self, project, subproject):
        now = datetime.now()

        self.day = now.strftime("%d")
        self.month = now.strftime("%B")
        self.year = now.strftime("%Y")
        self.start_time = now.strftime("%X")
        self.project = project
        if subproject > 0:
            self.subproject = subproject
        else:
            self.subproject = 0

    def end_logger(self):
        now = datetime.now()
        self.end_time = now.strftime("%X")

    def post_data(self):
        return [
            self.project,
            self.subproject,
            self.day,
            self.month,
            self.year,
            self.start_time,
            self.end_time,
        ]
