import datetime
import logging
from pathlib import Path
import time


import cv2

from .configuration import Config
from .utils import write_log_exception, write_log_info, write_log_error


class Recorder:


    def __init__(self, cam: int, config: Config, recording_dir_path: Path) -> None:
        '''Recorder Class that represents the video recording component of the application.'''

        self.cam = cam
        self.config = config
        self.recording_dir_path = recording_dir_path
        self.rec_filepath = None
        self.rec = None
        self.logger = logging.getLogger(__name__)
        self.bad_frames_counter = 5

        self.count = 0


    def _make_rec_capture(self) -> None:
        '''Creates a Video Capture object for the recorder component.'''

        self.cap = cv2.VideoCapture(self.cam)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.recorder_frame_width) 
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.recorder_frame_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.config.recorder_frame_rate)


    def _make_recorder(self) -> None:
        '''Creates and returns a Video Writer object for the recorder component.'''

        self.rec = cv2.VideoWriter(
            str(self.rec_filepath), 
            fourcc=cv2.VideoWriter_fourcc(*'mp4v'),
            fps=self.cap.get(cv2.CAP_PROP_FPS), 
            frameSize=(int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        )


    def _recorder_loop(self) -> None:
        '''Recorder component logic loop.'''

        while True:
            if self.config.kill:
                break
            if not self.config.recording:
                time.sleep(0.1)
                continue
            if not self.cap.isOpened():
                self._make_rec_capture()
            
            ret, frame = self.cap.read()
            if not ret:
                if self.config.debug:
                    print("Recorder: No frame received!")
                if self.bad_frames_counter <= 0:
                    write_log_error(self.logger, "Recorder: No frames received.")
                    self.config.kill = True
                else:
                    self.bad_frames_counter -= 1
                continue
            elif ret and self.bad_frames_counter < 5:
                self.bad_frames_counter += 1
            
            cur_date = datetime.datetime.now()
            cur_timestamp = cur_date.timestamp()
            cur_date = cur_date = cur_date.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
            cv2.putText(frame, cur_date, (20, 20), cv2.FONT_HERSHEY_PLAIN, 1.5, (255,255,255), 1, cv2.LINE_AA)
            
            if self.rec is None:
                filename = f'{self.cam}-{int(cur_timestamp)}.mp4'
                self.rec_filepath = self.recording_dir_path / filename
                self._make_recorder()

            #  Checking max filesize for uploading restrictions. Not exact convertion to bytes to leave some margin.
            if self.rec_filepath.stat().st_size > (self.config.max_file_size_mb * 1000000):
                filename = f'{self.cam}-{int(cur_timestamp)}.mp4'
                self.rec_filepath = self.recording_dir_path / filename
                self.rec.release()
                self._make_recorder()
            
            self.rec.write(frame)
            self.count += 1

            if self.config.debug:
                cv2.imshow(f'cap-{self.cam}', frame)
                cv2.waitKey(1)

            if self.count >= 10 * int(self.config.recorder_frame_rate):
                self.cap.release()
                self.rec.release()
                self.rec = None
                self.count = 0
                self.config.recording = False
                self.config.detecting = True
                if self.config.debug:
                    cv2.destroyWindow(f'cap-{self.cam}')
                    print("Stopping recording. Detecting active.")
                write_log_info(self.logger, "Stopping recording. Detecting active.")


    def record(self) -> None:
        '''Main loop for the recording component.'''

        try:
            self._make_rec_capture()

            if self.config.debug:
                print(f'Recorder Framerate: {self.cap.get(cv2.CAP_PROP_FPS)}')
                print(f'Recorder Frame Width: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}')
                print(f'Recorder Frame Height: {self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}')
                write_log_info(self.logger, f'Recorder Framerate: {self.cap.get(cv2.CAP_PROP_FPS)}')
                write_log_info(self.logger, f'Recorder Frame Width: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}')
                write_log_info(self.logger, f'Recorder Frame Height: {self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}')

            self._recorder_loop()
            
            if self.config.recording:
                self.cap.release()
                if self.rec is not None:
                    self.rec.release()
                if self.config.debug:
                    cv2.destroyWindow(f'cap-{self.cam}')
        except Exception as e:
            write_log_exception(self.logger, e)
            self.config.kill = True
