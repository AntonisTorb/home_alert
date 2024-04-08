import json
from pathlib import Path

class Config():
    '''Configuration class for the application.'''

    def __init__(self) -> None:
        self.recording = False
        self.kill = False

    def dump_config(self, config_path: Path):
        with open(config_path, 'w') as f:
            json.dump(self.__dict__, f)