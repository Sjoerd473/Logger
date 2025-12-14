import csv
import time as time
from datetime import datetime
from pathlib import Path

import easygui as gui


def time_logger(type):
    now = datetime.now()
    if type == "start":
        day = now.strftime("%d")
        month = now.strftime("%B")
        year = now.strftime("%Y")
        start_time = now.strftime("%X")

        return day, month, year, start_time, now
    else:
        return now.strftime("%X"), now


def log_to_csv(log):
    destination_file = Path.home() / "work_log.csv"

    if not destination_file.is_file():
        destination_file.touch()

    with destination_file.open(mode="a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "project",
                "day",
                "month",
                "year",
                "start_time",
                "end_time",
                "time_spent",
            ],
        )
        if file.tell() == 0:
            writer.writeheader()

        writer.writerow(log)


def main():
    line = {}
    line["project"] = gui.enterbox(
        msg="What are you working on today:", title="New project"
    )
    line["day"], line["month"], line["year"], line["start_time"], start = time_logger(
        "start"
    )

    gui.msgbox(
        msg="Close me to stop the timer", title="End logging", ok_button="Stop timer"
    )
    line["end_time"], end = time_logger("end")

    total_time = end - start
    line["time_spent"] = round(total_time.total_seconds() / 60)

    log_to_csv(line)


main()
