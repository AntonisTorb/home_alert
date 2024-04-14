import datetime
import logging
from pathlib import Path


def maintain_log(log_path: Path|str, days: int) -> None:
    '''Function to maintain the log file by removing entries older than `days` days.'''

    if not log_path.exists():
        return
    
    new_log = ""
    add_rest = False
    first_timestamp = True

    with open(log_path, "r") as f:
        log_lines = f.readlines()

    for index, line in enumerate(log_lines):
        parts = line.split("|")
        if not len(parts) == 4:
            continue
        date = parts[0][:-4]
        timestamp = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp()

        cutoff = days * 24 * 60 * 60  # Remove logs older than `days` days.
        
        if datetime.datetime.now().timestamp() - timestamp > cutoff:
            first_timestamp = False
            continue
        if first_timestamp:  # First timestamp is not older than 30 days, no need to continue.
            return
        if not add_rest:
            add_rest = True
        
        if add_rest:
            rest = "".join(log_lines[index:])
            new_log = f'{new_log}{rest}'
            break

    with open(log_path, "w") as f:
        f.write(new_log)