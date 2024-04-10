import time
import threading
from pathlib import Path

import cv2

from home_alert import Config, Detector, Recorder, DiscordBot


def main():
    cwd = Path.cwd()
    config_path = cwd / "config.json"
    recording_path = cwd / "recordings"
    recording_path.mkdir(exist_ok=True)
    config = Config(config_path)
    detector = Detector(0, config)
    recorder = Recorder(0, config, recording_path)

    detector_thread = threading.Thread(target=detector.detect)
    recorder_thread = threading.Thread(target=recorder.record)
    detector_thread.start()
    recorder_thread.start()

    while True:
        try:
            time.sleep(100)
        except KeyboardInterrupt:
            config.kill = True
            break

if __name__ == "__main__":
    print("start")
    main()
    print("end")
