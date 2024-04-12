from abc import ABC
import datetime
import logging
from pathlib import Path

class Component(ABC):
    pass

def write_log_exception(logger:logging.Logger, content: Exception):
    '''Utility function to write exceptions to the log file.'''

    now = datetime.datetime.now()
    timestamp = now.timestamp()
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    logger.exception(f'|{timestamp}|{date}|{content}')

def write_log_info(logger:logging.Logger, content: str):
    '''Utility function to write information to the log file.'''
    
    now = datetime.datetime.now()
    timestamp = now.timestamp()
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f'|{timestamp}|{date}|{content}')


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
        if line.startswith("INFO:") or line.startswith("ERROR:"):
            timestamp = float(line.split("|")[1])
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