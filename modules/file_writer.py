from __future__ import print_function

import csv
import time as time
from pathlib import Path

destination_file = Path.home() / "work_log.csv"

HEADERS = [
    "Id",
    "Project",
    "Subproject",
    "Day",
    "Month",
    "Year",
    "Start time",
    "End time",
    "Total time spent",
    "Time spent in minutes",
    "Time spend in hours",
    "Hourly rate",
    "Total payment by minute",
    "Total payment by hour",
]


def print_to_file(data):
    if not destination_file.is_file():
        destination_file.touch()

    with destination_file.open(mode="a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        if file.tell() == 0:
            writer.writeheader()

            for row in data:
                writer.writerow(
                    {
                        "Id": row["id"],
                        "Project": row["project_name"],
                        "Subproject": row["subproject_name"],
                        "Day": row["day"],
                        "Month": row["month"],
                        "Year": row["year"],
                        "Start time": row["start_time"].strftime("%H:%M:%S"),
                        "End time": row["end_time"].strftime("%H:%M:%S"),
                        "Total time spent": str(row["time_spent"]),
                        "Time spent in minutes": row["time_in_minutes"],
                        "Time spend in hours": row["time_in_hours"],
                        "Hourly rate": row["retribuizione"],
                        "Total payment by minute": round(
                            row["retribuizione"] * (row["time_in_minutes"] / 60)
                        ),
                        "Total payment by hour": round(
                            row["retribuizione"] * row["time_in_hours"]
                        ),
                    }
                )
        else:
            row = data[-1]

            writer.writerow(
                {
                    "Id": row["id"],
                    "Project": row["project_name"],
                    "Subproject": row["subproject_name"],
                    "Day": row["day"],
                    "Month": row["month"],
                    "Year": row["year"],
                    "Start time": row["start_time"].strftime("%H:%M:%S"),
                    "End time": row["end_time"].strftime("%H:%M:%S"),
                    "Total time spent": str(row["time_spent"]),
                    "Time spent in minutes": row["time_in_minutes"],
                    "Time spend in hours": row["time_in_hours"],
                    "Hourly rate": row["retribuizione"],
                    "Total payment by minute": round(
                        row["retribuizione"] * (row["time_in_minutes"] / 60)
                    ),
                    "Total payment by hour": round(
                        row["retribuizione"] * row["time_in_hours"]
                    ),
                }
            )


def refresh_file(data):
    if destination_file.exists():
        destination_file.unlink()
    print_to_file(data)
