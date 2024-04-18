import datetime
from pathlib import Path


def maintain_log(log_path: Path|str, days: int) -> None:
    '''Function to maintain the log file by removing entries older than `days` days.'''

    if not log_path.exists():
        return
    
    new_log: str = ""
    add_rest: bool = False
    first_timestamp: bool = True

    with open(log_path, "r") as f:
        log_lines: list[str] = f.readlines()

    for index, line in enumerate(log_lines):
        parts: list[str] = line.split("|")
        if not len(parts) == 4:
            continue
        date: str = parts[0][:-4]
        timestamp: float = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp()

        cutoff: int = days * 24 * 60 * 60  # Remove logs older than `days` days.
        
        if datetime.datetime.now().timestamp() - timestamp > cutoff:
            first_timestamp = False
            continue
        if first_timestamp:  # First timestamp is not older than 30 days, no need to continue.
            return
        if not add_rest:
            add_rest = True
        
        if add_rest:
            rest: str = "".join(log_lines[index:])
            new_log = f'{new_log}{rest}'
            break

    with open(log_path, "w") as f:
        f.write(new_log)

DISCORD_HELP = '''# Help:
`!status`           :     Returns the status of each Detector and Recorder component.
`!detect`           :     Start detecting.
`!close`            :     Close application.
`!stoprecording`    :     Stop recording and start detecting if alarm has been triggered.
`!checklog lines`   :     Replace `lines` with the amount of lines you need from the end of the `log file`.
`!clear`            :     Deletes all messages in the `status-control` Discord channel.
'''