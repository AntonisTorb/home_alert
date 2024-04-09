import time
import threading
from pathlib import Path

from home_alert import Config, Detector, Recorder, DiscordBot


def main():
    cwd = Path.cwd()
    config_path = cwd / "config.json"
    config = Config(config_path)
    detector = Detector(0, config)
    recorder = Recorder(config)

    detector_thread = threading.Thread(target=detector.detect)
    recorder_thread = threading.Thread(target=recorder.recording_status)
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
