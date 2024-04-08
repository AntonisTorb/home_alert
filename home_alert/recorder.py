import time

from .configuration import Config

class Recorder():
    def __init__(self, config:Config) -> None:
        
        self.config = config

    def recording_status(self):
        while True:
            if self.config.kill:
                break
            if self.config.recording:
                print("Recording...")
            else:
                print("Not Recording...")

            time.sleep(1)