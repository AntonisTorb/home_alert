import datetime
import logging
import time

import cv2
import numpy as np

from .configuration import Config
from .utils import write_log_exception, write_log_info, write_log_error


class Detector:

    def __init__(self, cam: int, config: Config) -> None:
        '''Detector Class that represents the movement detector component of the application.'''

        self.cam = cam
        self.config = config
        self.alerts = 0
        self.logger = logging.getLogger(__name__)
        self.bad_frames_counter = 5
        self.previous_frame = None

    def _make_detector(self) -> None:
        '''Creates a Video Capture object for the detector component.'''

        self.det = cv2.VideoCapture(self.cam)
        self.det.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.detector_frame_width) 
        self.det.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.detector_frame_height)
        self.det.set(cv2.CAP_PROP_FPS, self.config.detector_frame_rate)


    def _detector_loop(self) -> None:
        '''Detector component logic loop.'''

        while True:
            if self.config.kill:
                break
            if self.config.recording and not self.config.detecting:
                time.sleep(0.5)
                continue

            if not self.det.isOpened():
                self._make_detector()
            ret, frame = self.det.read()

            if not ret:
                if self.config.debug:
                    print("Detector: No frame received!")
                if self.bad_frames_counter <= 0:
                    write_log_error(self.logger, "Detector: No frames received.")
                    self.config.kill = True
                else:
                    self.bad_frames_counter -= 1
                continue
            elif ret and self.bad_frames_counter < 5:
                self.bad_frames_counter += 1

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.GaussianBlur(frame, (21,21), 0)

            if type(self.previous_frame) != np.ndarray:
                self.previous_frame = frame
                continue
                
            difference = cv2.absdiff(frame, self.previous_frame)
            threshold = cv2.threshold(difference, self.config.detector_threshold, 255, cv2.THRESH_BINARY)[1]
            if (threshold_mean := round(threshold.mean(), 2)) > self.config.alert_threshold:
                self.alerts += 1
            else:
                if self.alerts > 0:
                    self.alerts -= 1

            if self.config.debug:
                if threshold_mean > 0:
                    print(f'{threshold_mean = }')
                cur_date = datetime.datetime.now()
                cur_date = cur_date.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                cv2.putText(threshold, cur_date, (20, 20), cv2.FONT_HERSHEY_PLAIN, 1.5, (255,0,0), 1, cv2.LINE_AA)
                cv2.imshow(f'det-{self.cam}', threshold)
                cv2.waitKey(1)

            
            self.previous_frame = frame

            if self.alerts > self.config.alerts_to_trigger_recording:
                self.det.release()
                self.previous_frame = None
                self.alerts = 0
                self.config.recording = True
                self.config.detecting = False
                if self.config.debug:
                    try:
                        cv2.destroyWindow(f'det-{self.cam}')
                    except cv2.error:
                        pass
                    print("Alarm triggered, starting recording.")
                write_log_info(self.logger, "Alarm triggered, starting recording.")

    def detect(self) -> None:
        '''Main loop for the movement detector component.'''

        try:
            self._make_detector()

            if self.config.debug:
                print(f'Detector {self.cam} Framerate: {self.det.get(cv2.CAP_PROP_FPS)}')
                print(f'Detector {self.cam} Frame Width: {self.det.get(cv2.CAP_PROP_FRAME_WIDTH)}')
                print(f'Detector {self.cam} Frame Height: {self.det.get(cv2.CAP_PROP_FRAME_HEIGHT)}')
                write_log_info(self.logger, f'Detector {self.cam} Framerate: {self.det.get(cv2.CAP_PROP_FPS)}')
                write_log_info(self.logger, f'Detector {self.cam} Frame Width: {self.det.get(cv2.CAP_PROP_FRAME_WIDTH)}')
                write_log_info(self.logger, f'Detector {self.cam} Frame Height: {self.det.get(cv2.CAP_PROP_FRAME_HEIGHT)}')

            self._detector_loop()
            
            if self.config.detecting:
                self.det.release()
                if self.config.debug:
                    try:
                        cv2.destroyWindow(f'det-{self.cam}')
                    except cv2.error as e:
                        pass
        except Exception as e:
            write_log_exception(self.logger, e)
            self.config.kill = True
