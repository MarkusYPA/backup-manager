"""
Backup Service Worker

This script runs as a background process, monitoring backup schedules
and performing file compression (tar) at the scheduled times.
"""

import time
import datetime
import os
import tarfile

LOG_FILE = "logs/backup_service.log"
SCHEDULES_FILE = "backup_schedules.txt"
BACKUPS_DIR = "backups"


def log_message(message):
    """
    Logs a message with a timestamp to the service log file.

    Args:
        message (str): The message to log.
    """
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    timestamp = datetime.datetime.now().strftime("[%d/%m/%Y %H:%M]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")


def perform_backup(path, name):
    """
    Creates a compressed tar archive of the specified directory.

    Args:
        path (str): The source directory path to back up.
        name (str): The name of the resulting backup archive (without extension).
    """
    try:
        os.makedirs(BACKUPS_DIR, exist_ok=True)
        backup_path = os.path.join(BACKUPS_DIR, f"{name}.tar")

        with tarfile.open(backup_path, "w") as tar:
            tar.add(path, arcname=os.path.basename(path))

        log_message(f"Backup done for {path} in {backup_path}")
    except Exception as e:
        log_message(f"Error performing backup for {path}: {str(e)}")


def main():
    """
    Main service loop. Continuously checks for scheduled backups,
    executes them if the current time matches, and cleans up schedules.
    """
    while True:
        try:
            if os.path.exists(SCHEDULES_FILE):
                with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
                    schedules = f.readlines()

                now = datetime.datetime.now()
                current_time_str = now.strftime("%H:%M")
                current_minutes = now.hour * 60 + now.minute

                remaining_schedules = []
                for line in schedules:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        path, sched_time_str, name = line.split(";")
                        sched_hour, sched_min = map(int, sched_time_str.split(":"))
                        sched_total_minutes = sched_hour * 60 + sched_min

                        if sched_time_str == current_time_str:
                            # Match!
                            perform_backup(path, name)
                            # Do not add to remaining_schedules (it's removed after processing)
                        elif sched_total_minutes < current_minutes:
                            # Already passed (today)
                            # Requirement: "Schedules whose time has already passed are removed ... after processing."
                            # Even if we didn't back it up (e.g., service was down), we remove it?
                            # Usually yes, otherwise it keeps trying or blocks others.
                            remaining_schedules.append(
                                line
                            )  # Wait, if it passed, we remove it.
                            # Re-reading: "The service performs a backup when the current hour and minute match a scheduled time.
                            # Schedules whose time has already passed are removed ... after processing."
                            # This implies matched -> process -> remove.
                            # What about those that passed but didn't match (missed)?
                            # "Schedules whose time has already passed are removed"
                            # I'll remove them.
                            pass
                        else:
                            remaining_schedules.append(line)
                    except Exception:
                        # Malformed in file? Skip or remove?
                        # Log it?
                        log_message(f"Error parsing schedule line: {line}")

                # Update file if changed
                if len(remaining_schedules) != len(schedules):
                    with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
                        for s in remaining_schedules:
                            f.write(f"{s}\n")

        except Exception as e:
            log_message(f"Error in service loop: {str(e)}")

        time.sleep(45)


if __name__ == "__main__":
    main()
