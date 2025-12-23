from __future__ import print_function

import csv
import shutil
from datetime import datetime
from pathlib import Path


class FileWriter:
    def __init__(self):
        self.dest_folder = Path.home() / "logger_logs"
        self.backup_folder = self.dest_folder / "backups"
        self.dest_file = self.dest_folder / "work_log.csv"
        self.HEADERS = [
            "Id",
            "Project",
            "Subproject",
            "Activity",
            "Day",
            "Month",
            "Year",
            "Start time",
            "End time",
            "Total time spent",
            "Time spent in minutes",
            "Time spend in hours",
            "Hourly rate",
            "Earnings",
        ]
        self.MAX_BACKUPS = 5
        self._create_files_if_missing()

    def _create_files_if_missing(self):
        self.dest_folder.mkdir(exist_ok=True)
        self.backup_folder.mkdir(exist_ok=True)

        if not self.dest_file.is_file():
            self.dest_file.touch()

    def _compute_time_fields(self, row):
        start = datetime.strptime(row["start_time"], "%H:%M:%S")
        end = datetime.strptime(row["end_time"], "%H:%M:%S")

        delta = end - start
        minutes = int(delta.total_seconds() / 60)
        hours = round(minutes / 60, 2)

        earnings = round(hours * row["hourly_rate"], 2)

        return {
            "total_time": str(delta),
            "minutes": minutes,
            "hours": hours,
            "earnings": earnings,
        }

    def print_to_file(self, data):
        with self.dest_file.open(mode="a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.HEADERS)

            # Write header if file is empty
            if file.tell() == 0:
                writer.writeheader()

            # If writing all rows (first run)
            if isinstance(data, list):
                for row in data:
                    self._write_row(writer, row)
            else:
                # If writing only the last row
                self._write_row(writer, data)

    def _write_row(self, writer, row):
        computed = self._compute_time_fields(row)

        writer.writerow(
            {
                "Id": row["id"],
                "Project": row["project_name"],
                "Subproject": row["subproject_name"],
                "Activity": row["activity_name"],
                "Day": row["day"],
                "Month": row["month"],
                "Year": row["year"],
                "Start time": row["start_time"],
                "End time": row["end_time"],
                "Total time spent": computed["total_time"],
                "Time spent in minutes": computed["minutes"],
                "Time spend in hours": computed["hours"],
                "Hourly rate": row["hourly_rate"],
                "Earnings": computed["earnings"],
            }
        )

    def refresh_file(self, data):
        if self.dest_file.exists():
            self.dest_file.unlink()
        self.print_to_file(data)

    def backup_db(self, dst, timestamp):
        src = Path("logger.db")
        file_dst = dst / f"logger_backup_{timestamp}.db"
        shutil.copy(src, file_dst)

    def backup_csv(self, dst, timestamp):
        file_dst = dst / f"work_log_backup_{timestamp}.csv"
        shutil.copy(self.dest_file, file_dst)

    def backup_everything(self):
        self._prune_old_backups()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dst = self.backup_folder / f"logger_backup_{timestamp}"
        dst.mkdir(exist_ok=True)
        self.backup_db(dst, timestamp)
        self.backup_csv(dst, timestamp)

    def _prune_old_backups(self):
        backups = sorted(
            [p for p in self.backup_folder.iterdir() if p.is_dir()],
            key=lambda p: p.stat().st_mtime,
        )
        while len(backups) > self.MAX_BACKUPS:
            oldest = backups.pop(0)
            shutil.rmtree(oldest)
