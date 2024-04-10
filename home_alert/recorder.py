import datetime
from pathlib import Path
import time


import cv2

from .configuration import Config

class Recorder():
    def __init__(self, cam: int, config: Config, recording_path: Path) -> None:
        '''Recorder Class that represents the video recording component of the application.'''

        self.cam = cam
        self.config = config
        self.recording_path = recording_path


    def _get_rec_capture(self) -> cv2.VideoCapture:
        '''Creates and returns a Video Capture object for the recorder component.'''

        cap = cv2.VideoCapture(self.cam)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.recorder_frame_width) 
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.recorder_frame_height)
        cap.set(cv2.CAP_PROP_FPS, self.config.recorder_frame_rate)
        return cap


    def _get_recorder(self, filepath) -> cv2.VideoWriter:
        '''Creates and returns a Video Writer object for the recorder component.'''

        rec = cv2.VideoWriter(str(filepath), 
                            fourcc=cv2.VideoWriter_fourcc(*'mp4v'),
                            fps=self.config.recorder_frame_rate, 
                            frameSize=(int(self.config.recorder_frame_width), int(self.config.recorder_frame_height))
        )
        return rec

    def record(self) -> None:
        '''Main loop for the recording component.'''

        count = 0
        cap = self._get_rec_capture()
        filepath = None

        rec = None
        if self.config.debug:
            print(f'Recorder Framerate: {cap.get(cv2.CAP_PROP_FPS)}')
            print(f'Recorder Frame Width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}')
            print(f'Recorder Frame Height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}')

        while True:
            if self.config.kill:
                break
            if not self.config.recording:
                time.sleep(0.1)
                continue
            if not cap.isOpened():
                cap = self._get_rec_capture()
            
            _, frame = cap.read()
            
            cur_date = datetime.datetime.now()
            cur_timestamp = cur_date.timestamp()
            cur_date = cur_date = cur_date.strftime("%Y/%m/%d %H:%M:%S.%f")
            cv2.putText(frame, cur_date, (20, 20), cv2.FONT_HERSHEY_PLAIN, 1.5, (255,255,255), 1, cv2.LINE_AA)
            
            if rec is None:
                filename = f'{int(cur_timestamp)}.mp4'
                filepath = self.recording_path / filename
                rec = self._get_recorder(filepath)

            #  Checking macx filesize for uploading restrictions. not exact convertion to bytes to leave some margin.
            if filepath.stat().st_size > (self.config.max_file_size_mb * 1000000):
                filename = f'{int(cur_timestamp)}.mp4'
                filepath = self.recording_path / filename
                rec.release()
                rec = self._get_recorder(filepath)
            
            rec.write(frame)
            count += 1

            if self.config.debug:
                cv2.imshow(f'cap-{self.cam}', frame)
                cv2.waitKey(self.config.recorder_frame_rate)

            if count >= 20 * int(self.config.recorder_frame_rate):
                cap.release()
                rec.release()
                rec = None
                count = 0
                self.config.recording = False
                self.config.detecting = True
                
                
                if self.config.debug:
                    cv2.destroyWindow(f'cap-{self.cam}')
        
        cap.release()
        cv2.destroyWindow(f'cap-{self.cam}')
        rec.release()
