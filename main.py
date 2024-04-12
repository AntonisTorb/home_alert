import logging
from pathlib import Path
import threading
import time

from home_alert import Config, Detector, Recorder, DiscordBot, utils


def main():
    cwd = Path.cwd()
    config_path = cwd / "config.json"
    recording_path = cwd / "recordings"
    recording_path.mkdir(exist_ok=True)
    log_path = cwd / "home_alert.log"

    utils.maintain_log(log_path, 30)

    main_logger = logging.getLogger("Main")
    logging.basicConfig(filename=log_path.name, level=logging.INFO)

    config = Config(config_path)
    if config.debug:
        utils.write_log_info(main_logger, "Starting application.")

    detector = Detector(0, config)
    recorder = Recorder(0, config, recording_path)

    detector_thread = threading.Thread(target=detector.detect)
    recorder_thread = threading.Thread(target=recorder.record)
    detector_thread.start()
    recorder_thread.start()

    while True:
        if config.kill:
            break
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            config.kill = True
            if config.debug:
                utils.write_log_info(main_logger, "Closing application.")


if __name__ == "__main__":
    main()
