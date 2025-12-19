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
    "Payment",
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
                        "Id": row[0],
                        "Project": row[1],
                        "Subproject": row[2],
                        "Day": row[3],
                        "Month": row[4],
                        "Year": row[5],
                        "Start time": row[6].strftime("%H:%M:%S"),
                        "End time": row[7].strftime("%H:%M:%S"),
                        "Total time spent": str(row[8]),
                        "Time spent in minutes": row[9],
                        "Payment": round(row[10] * (row[9] / 60)),
                    }
                )
        else:
            row = data[-1]

            writer.writerow(
                {
                    "Id": row[0],
                    "Project": row[1],
                    "Subproject": row[2],
                    "Day": row[3],
                    "Month": row[4],
                    "Year": row[5],
                    "Start time": row[6].strftime("%H:%M:%S"),
                    "End time": row[7].strftime("%H:%M:%S"),
                    "Total time spent": str(row[8]),
                    "Time spent in minutes": row[9],
                    "Payment": round(row[10] * (row[9] / 60)),
                }
            )


def refresh_file(data):
    if destination_file.exists():
        destination_file.unlink()
    print_to_file(data)
