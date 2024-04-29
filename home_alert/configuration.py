import json
from pathlib import Path

class Config():

    def __init__(self, config_path: Path, cam: int = 0) -> None:
        '''Configuration class for the application.'''

        # Default configuration values.
        self.detecting: bool = False
        self.debug: bool = True
        self.max_file_size_mb: int = 25
        self.detector_frame_width: int = 640
        self.detector_frame_height: int = 480
        self.detector_frame_rate: int = 10
        self.detector_threshold: int = 5
        self.frames_for_alert: int = 5
        self.alert_threshold: int = 50
        self.recorder_frame_width: int = 1280
        self.recorder_frame_height: int = 720
        self.recorder_frame_rate: int = 30

        try:
            with open(config_path, 'r') as f:
                self.__dict__ = json.load(f)[str(cam)]
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("Configuration file not found or corrupted. Creating with default values...")
            self._dump_config(config_path)

        self.cam: int = cam
        self.recording: bool = False
        self.kill: bool = False


    def _dump_config(self, config_path: Path) -> None:
        '''Creates the `config.json` configuration file if it does not exist or is corrupted.'''

        with open(config_path, 'w') as f:
            config = {"0": self.__dict__}
            json.dump(config, f, indent=4)

    def __repr__(self) -> str:
        return f'self.__dict'
