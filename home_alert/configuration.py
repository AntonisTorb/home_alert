from copy import deepcopy
import json
from pathlib import Path

class Config():

    def __init__(self, config_path: Path, cam: int = 0) -> None:
        '''Configuration class for the application.'''

        self._default_config = {
            "detecting": True,
            "recording": False,
            "debug": True,
            "max_file_size_mb": 25,
            "detector_frame_width": 640,
            "detector_frame_height": 480,
            "detector_frame_rate": 10,
            "detector_threshold": 5,
            "alert_threshold": 10,
            "alerts_to_trigger_recording": 5,
            "recorder_frame_width": 1280,
            "recorder_frame_height": 720,
            "recorder_frame_rate": 30,
        }

        try:
            with open(config_path, 'r') as f:
                self.__dict__ = json.load(f)[str(cam)]
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("Configuration file not found or corrupted. Creating with default values...")
            self.__dict__ = deepcopy(self._default_config)
            self._dump_config(config_path)

        self.recording = False
        self.kill = False


    def _dump_config(self, config_path: Path) -> None:
        '''Creates the `config.json` configuration file if it does not exist or is corrupted.'''

        with open(config_path, 'w') as f:
            config = {"0": self.__dict__}
            json.dump(config, f, indent=4)
