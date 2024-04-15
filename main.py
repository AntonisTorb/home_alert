from collections import deque
import logging
from pathlib import Path
import threading
import time

from home_alert import Config, Detector, Recorder, DiscordBot, utils


def main():

    cwd: Path = Path.cwd()
    config_path: Path = cwd / "config.json"
    recording_dir_path: Path = cwd / "recordings"
    recording_dir_path.mkdir(exist_ok=True)
    recordings_queue: deque[str] = deque()
    log_path: Path = cwd / "home_alert.log"
    cameras: int = 1
    app_close: bool = False

    utils.maintain_log(log_path, 30)

    main_logger: logging.Logger = logging.getLogger(__name__)
    logging.basicConfig(filename=log_path.name, 
                        level=logging.INFO,
                        format="%(asctime)s|%(levelname)8s|%(name)s|%(message)s")

    main_logger.info("Starting application.")

    configs: list[Config] = []
    detectors: list[Detector] = []
    recorders: list[Recorder] = []
    threads: list[threading.Thread] = []

    for cam in range(cameras):
        config: Config = Config(config_path, cam)
        configs.append(config)
        detector: Detector = Detector(cam, config)
        detectors.append(detector)
        detector_thread: threading.Thread = threading.Thread(target=detector.detect)
        threads.append(detector_thread)
        recorder: Recorder = Recorder(cam, config, recording_dir_path, recordings_queue)
        recorders.append(recorder)
        recorder_thread: threading.Thread = threading.Thread(target=recorder.record)
        threads.append(recorder_thread)

    discord_bot: DiscordBot = DiscordBot(recording_dir_path, cameras, configs, recordings_queue)
    bot_thread: threading.Thread = threading.Thread(target=discord_bot.run_bot)
    
    threads.append(bot_thread)

    for thread in threads:
        thread.start()

    while True:
        if discord_bot.kill:
            app_close = True

        for config in configs:
            if config.kill:
                app_close = True

        if app_close:
            for config in configs:
                config.kill = True
            discord_bot.kill = True

            while True:
                finished_threads  = 0
                for thread in threads:
                    if not thread.is_alive():
                        finished_threads += 1
                if finished_threads == len(threads):
                    break
                time.sleep(1)
                        
            main_logger.info("Closing application.")
            break
        
        try:
            time.sleep(1)
        except KeyboardInterrupt:  # Manual shutdown.
            app_close = True


if __name__ == "__main__":
    main()
