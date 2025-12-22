from __future__ import print_function

import csv
from datetime import datetime
from pathlib import Path

destination_file = Path.home() / "work_log.csv"

HEADERS = [
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


def _compute_time_fields(row):
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


def print_to_file(data):
    if not destination_file.is_file():
        destination_file.touch()

    with destination_file.open(mode="a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)

        # Write header if file is empty
        if file.tell() == 0:
            writer.writeheader()

        # If writing all rows (first run)
        if isinstance(data, list):
            for row in data:
                _write_row(writer, row)
        else:
            # If writing only the last row
            _write_row(writer, data)


def _write_row(writer, row):
    computed = _compute_time_fields(row)

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


def refresh_file(data):
    if destination_file.exists():
        destination_file.unlink()
    print_to_file(data)
