import time

from .configuration import Config

class Detector():
    def __init__(self, config:Config) -> None:
        self.config = config
    
    def manage(self):
        while True:
            if self.config.kill:
                break

            if self.config.recording:
                self.config.recording = False
            else:
                self.config.recording = True
            time.sleep(5)