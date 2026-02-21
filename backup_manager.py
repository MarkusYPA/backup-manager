"""
Backup Manager CLI

This script provides a command-line interface for managing backup schedules
and controlling the background backup service.
"""

import sys
import os
import datetime
import subprocess

LOG_FILE = "logs/backup_manager.log"
SCHEDULES_FILE = "backup_schedules.txt"
BACKUPS_DIR = "backups"
SERVICE_SCRIPT = "backup_service.py"


def log_message(message):
    """
    Logs a message with a timestamp to the manager log file.

    Args:
        message (str): The message to log.
    """
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    timestamp = datetime.datetime.now().strftime("[%d/%m/%Y %H:%M]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")


def create_schedule(schedule_str):
    """
    Parses and adds a new backup schedule to the schedules file.

    Args:
        schedule_str (str): The schedule in format "path;HH:MM;name".
    """
    try:
        parts = schedule_str.split(";")
        if len(parts) != 3 or not parts[0] or not parts[1] or not parts[2]:
            raise ValueError(f"malformed schedule: {schedule_str}")

        # Basic time validation
        time_parts = parts[1].split(":")
        if len(time_parts) != 2:
            raise ValueError(f"malformed schedule: {schedule_str}")
        hour, minute = int(time_parts[0]), int(time_parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(f"malformed schedule: {schedule_str}")

        with open(SCHEDULES_FILE, "a", encoding="utf-8") as f:
            f.write(f"{schedule_str}\n")
        log_message(f"New schedule added: {schedule_str}")
    except (ValueError, OSError) as e:
        log_message(f"Error: {str(e)}")


def list_schedules():
    """
    Lists all scheduled backups from the schedules file.
    """
    try:
        if not os.path.exists(SCHEDULES_FILE):
            raise FileNotFoundError("can't find backup_schedules.txt")

        with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
            schedules = f.readlines()

        for i, schedule in enumerate(schedules):
            print(f"{i}: {schedule.strip()}")
        log_message("Show schedules list")
    except (FileNotFoundError, OSError) as e:
        log_message(f"Error: {str(e)}")


def delete_schedule(index):
    """
    Deletes a backup schedule at the specified index.

    Args:
        index (int/str): The index of the schedule to delete.
    """
    try:
        if not os.path.exists(SCHEDULES_FILE):
            raise FileNotFoundError("can't find backup_schedules.txt")

        with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
            schedules = f.readlines()

        idx = int(index)
        if 0 <= idx < len(schedules):
            removed = schedules.pop(idx)
            with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
                f.writelines(schedules)
            log_message(f"Schedule at index {idx} deleted: {removed.strip()}")
        else:
            raise IndexError(f"can't find schedule at index {idx}")
    except (ValueError, IndexError, FileNotFoundError, OSError) as e:
        log_message(f"Error: {str(e)}")


def start_service():
    """
    Starts the backup service as a background process.
    """
    try:
        # Verify if the service is already running to avoid duplicate instances
        check_cmd = f"ps -A -f | grep {SERVICE_SCRIPT} | grep -v grep"
        result = subprocess.run(
            check_cmd, shell=True, capture_output=True, text=True, check=False
        )
        if result.stdout.strip():
            log_message("Error: backup_service already running")
            return

        # No 'with' statement used because the service must continue running as a daemon
        # pylint: disable=consider-using-with
        subprocess.Popen([sys.executable, SERVICE_SCRIPT], start_new_session=True)
        log_message("backup_service started")
    except (OSError, subprocess.SubprocessError) as e:
        log_message(f"Error: backup_service failed to start: {str(e)}")


def stop_service():
    """
    Stops the background backup service by terminating its process.
    """
    try:
        # Find PID
        check_cmd = f"ps -A -f | grep {SERVICE_SCRIPT} | grep -v grep"
        result = subprocess.run(
            check_cmd, shell=True, capture_output=True, text=True, check=False
        )
        if not result.stdout.strip():
            raise RuntimeError("can't stop backup_service")

        # Extract PID from the process list output (typically the second column)
        for line in result.stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) > 1:
                pid = int(parts[1])
                os.kill(pid, 15)  # SIGTERM

        log_message("backup_service stopped")
    except (OSError, ValueError, RuntimeError) as e:
        log_message(f"Error: {str(e)}")


def list_backups():
    """
    Lists all created backup files in the backups directory.
    """
    try:
        if not os.path.exists(BACKUPS_DIR):
            os.makedirs(BACKUPS_DIR, exist_ok=True)

        files = [
            f
            for f in os.listdir(BACKUPS_DIR)
            if os.path.isfile(os.path.join(BACKUPS_DIR, f))
        ]
        for f in files:
            print(f)
        log_message("Show backups list")
    except OSError:
        log_message("Error: can't find backups directory")


def main():
    """
    Main entry point for the CLI. Parses command-line arguments and
    executes the corresponding backup management commands.
    """
    if len(sys.argv) < 2:
        log_message("Error: no command provided")
        return

    cmd = sys.argv[1]

    if cmd == "create" and len(sys.argv) == 3:
        create_schedule(sys.argv[2])
    elif cmd == "list":
        list_schedules()
    elif cmd == "delete" and len(sys.argv) == 3:
        delete_schedule(sys.argv[2])
    elif cmd == "start":
        start_service()
    elif cmd == "stop":
        stop_service()
    elif cmd == "backups":
        list_backups()
    else:
        log_message(f"Error: unknown command or missing arguments: {cmd}")


if __name__ == "__main__":
    main()
