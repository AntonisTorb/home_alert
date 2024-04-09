from copy import deepcopy
import json
from pathlib import Path

class Config():
    '''Configuration class for the application.'''

    def __init__(self, config_path: Path) -> None:

        self._default_config = {
            "debug": True,
            "detector_frame_width": 640,
            "detector_frame_height": 480,
            "detector_frame_rate": 10,
            "detector_threshold": 5,
            "alert_threshold": 10,
            "recorder_frame_width": 1280,
            "recorder_frame_height": 720,
            "recorder_frame_rate": 30,

        }

        try:
            with open(config_path, 'r') as f:
                self.__dict__ = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("Configuration file not found or corrupted. Creating with default values...")
            self.__dict__ = deepcopy(self._default_config)
            self.dump_config(config_path)

        self.recording = False
        self.kill = False


    def dump_config(self, config_path: Path):
        with open(config_path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)
