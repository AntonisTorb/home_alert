import time
import threading

from home_alert import Config, Detector, Recorder, DiscordBot


def main():
    config = Config()
    config.dump_config()
    detector = Detector(config)
    recorder = Recorder(config)

    detector_thread = threading.Thread(target=detector.manage)
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
