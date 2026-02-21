# Backup Manager

An automated backup system that schedules and performs directory backups via a CLI and a background service.

## Installation

1. Ensure Python 3 is installed.
2. Clone or download the project files.

## Usage

### backup_manager.py

The CLI tool to manage schedules and the service.

- `python3 backup_manager.py create "path;HH:MM;name"`: Add a new schedule.
- `python3 backup_manager.py list`: List all schedules.
- `python3 backup_manager.py delete [index]`: Delete a schedule by index.
- `python3 backup_manager.py start`: Start the background backup service.
- `python3 backup_manager.py stop`: Stop the background backup service.
- `python3 backup_manager.py backups`: List existing backup files.

### backup_service.py

The background service that monitors schedules and performs backups. It is normally started via `backup_manager.py start`.

## Logging

- Manager logs: `logs/backup_manager.log`
- Service logs: `logs/backup_service.log`

## File Structure

- `backup_manager.py`: CLI orchestration script.
- `backup_service.py`: Background worker script.
- `backup_schedules.txt`: Stores the scheduled tasks.
- `backups/`: Directory where `.tar` archives are stored.
- `logs/`: Directory for action and error logs.
