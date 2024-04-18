import argparse
from collections import deque
import logging
from pathlib import Path
import threading
import time

from home_alert import Config, Detector, Recorder, DiscordBot, utils


def component_maker(cameras: int, config_path: Path, recording_dir_path: Path, 
                    recordings_queue: deque) -> tuple[list[Config], list[Detector], list[Recorder], DiscordBot]:
    '''Creates and returns the components and configuration objects required for the application.'''

    configs: list[Config] = []
    detectors: list[Detector] = []
    recorders: list[Recorder] = []

    for cam in range(cameras):
        config: Config = Config(config_path, cam)
        configs.append(config)

        detector: Detector = Detector(cam, config)
        detectors.append(detector)
        
        recorder: Recorder = Recorder(cam, config, recording_dir_path, recordings_queue)
        recorders.append(recorder)

    discord_bot: DiscordBot = DiscordBot(recording_dir_path, cameras, configs, recordings_queue)

    return configs, detectors, recorders, discord_bot


def thread_maker(detectors: list[Detector], recorders: list[Recorder], discord_bot: DiscordBot) -> list[threading.Thread]:
    '''Creates and returns a lsit containing the threads for each application component.'''
    
    threads: list[threading.Thread] = []

    for detector, recorder in zip(detectors, recorders):

        detector_thread: threading.Thread = threading.Thread(target=detector.detect)
        threads.append(detector_thread)
        
        recorder_thread: threading.Thread = threading.Thread(target=recorder.record)
        threads.append(recorder_thread)

    bot_thread: threading.Thread = threading.Thread(target=discord_bot.run_bot)
    
    threads.append(bot_thread)

    return threads


def exit_loop(main_logger: logging.Logger, configs: list[Config], 
              discord_bot: DiscordBot, threads: list[threading.Thread]):
    '''Loop used to check app exit conditions and ensure all components are terminated in a safe manner.'''

    app_close: bool = False
    while True:
        #  Check if any component signaled to exit.
        if discord_bot.kill:
            app_close = True

        for config in configs:
            if config.kill:
                app_close = True

        if app_close:
            #  Signal all components to close.
            for config in configs:
                config.kill = True
            discord_bot.kill = True

            # wait for all threads to safely finish.
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


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cameras", type=int, help="Amount of webcams.", required=False)
    args = parser.parse_args()

    if args.cameras is not None or type(args.cameras) != type(int):
        cameras: int = args.cameras
    else:
        cameras: int = 1

    cwd: Path = Path.cwd()
    config_path: Path = cwd / "config.json"
    recording_dir_path: Path = cwd / "recordings"
    recording_dir_path.mkdir(exist_ok=True)
    recordings_queue: deque[str] = deque()
    log_path: Path = cwd / "home_alert.log"

    utils.maintain_log(log_path, days=30)

    main_logger: logging.Logger = logging.getLogger(__name__)
    logging.basicConfig(filename=log_path.name, 
                        level=logging.INFO,
                        format="%(asctime)s|%(levelname)8s|%(name)s|%(message)s")

    main_logger.info("Starting application.")

    configs, detectors, recorders, discord_bot = component_maker(cameras, config_path, recording_dir_path, recordings_queue)
    threads = thread_maker(detectors, recorders, discord_bot)

    for thread in threads:
        thread.start()

    exit_loop(main_logger, configs, discord_bot, threads)


if __name__ == "__main__":
    main()
