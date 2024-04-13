import logging
from pathlib import Path
import threading
import time

from home_alert import Config, Detector, Recorder, DiscordBot, utils


def main():

    
    cwd = Path.cwd()
    config_path = cwd / "config.json"
    recording_dir_path = cwd / "recordings"
    recording_dir_path.mkdir(exist_ok=True)
    log_path = cwd / "home_alert.log"
    cameras = 1
    app_close = False

    utils.maintain_log(log_path, 30)

    main_logger = logging.getLogger(__name__)
    logging.basicConfig(filename=log_path.name, level=logging.INFO)
    
    utils.write_log_info(main_logger, "Starting application.")

    configs = []
    detectors = []
    recorders = []
    discord_bots = []
    threads = []

    for cam in range(cameras):
        config = Config(config_path, cam)
        configs.append(config)
        detector = Detector(cam, config)
        detectors.append(detector)
        detector_thread = threading.Thread(target=detector.detect)
        threads.append(detector_thread)
        recorder = Recorder(cam, config, recording_dir_path)
        recorders.append(recorder)
        recorder_thread = threading.Thread(target=recorder.record)
        threads.append(recorder_thread)

    for thread in threads:

        thread.start()

    while True:
        for config in configs:
            if config.kill:
                utils.write_log_info(main_logger, "Closing application.")
                app_close = True
        if app_close:
            for config in configs:
                config.kill = True
            break
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            config.kill = True


if __name__ == "__main__":
    main()
