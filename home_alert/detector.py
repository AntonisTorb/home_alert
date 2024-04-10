import datetime
import time

import cv2
import numpy as np

from .configuration import Config

class Detector():

    def __init__(self, cam: int, config: Config) -> None:
        '''Detector Class that represents the movement detector component of the application.'''

        self.cam = cam
        self.config = config
        self.alerts = 0

    def _get_detector(self) -> cv2.VideoCapture:
        '''Creates and returns a Video Capture object for the detector component.'''

        det = cv2.VideoCapture(self.cam)
        det.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.detector_frame_width) 
        det.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.detector_frame_height)
        det.set(cv2.CAP_PROP_FPS, self.config.detector_frame_rate)
        return det


    def detect(self) -> None:
        '''Main loop for the movement detector component.'''

        det = self._get_detector()
        if self.config.debug:
            print(f'Detector Framerate: {det.get(cv2.CAP_PROP_FPS)}')
            print(f'Detector Frame Width: {det.get(cv2.CAP_PROP_FRAME_WIDTH)}')
            print(f'Detector Frame Height: {det.get(cv2.CAP_PROP_FRAME_HEIGHT)}')

        previous_frame = None
        while True:
            if self.config.kill:
                break
            if self.config.recording and not self.config.detecting:
                time.sleep(0.5)
                continue

            if not det.isOpened():
                det = self._get_detector()
            ret, frame = det.read()
            if not ret:
                print(ret)
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.GaussianBlur(frame, (21,21), 0)

            if type(previous_frame) != np.ndarray:
                previous_frame = frame
                continue
                
            difference = cv2.absdiff(frame, previous_frame)
            threshold = cv2.threshold(difference, self.config.detector_threshold, 255, cv2.THRESH_BINARY)[1]
            if (threshold_mean := round(threshold.mean(), 2)) > self.config.alert_threshold:
                self.alerts += 1
            else:
                if self.alerts > 0:
                    self.alerts -= 1
            

            if self.config.debug:
                if threshold_mean > 0:
                    print(threshold_mean)
                cur_date = datetime.datetime.now()
                # print(int(cur_date.timestamp()))
                cur_date = cur_date.strftime("%Y/%m/%d %H:%M:%S.%f")
                cv2.putText(threshold, cur_date, (20, 20), cv2.FONT_HERSHEY_PLAIN, 1.5, (255,0,0), 1, cv2.LINE_AA)
                cv2.imshow(f'det-{self.cam}', threshold)
                cv2.waitKey(self.config.detector_frame_rate)
            
            previous_frame = frame

            if self.alerts > self.config.alerts_to_trigger_recording:
                det.release()
                cv2.destroyWindow(f'det-{self.cam}')
                self.config.recording = True
                self.config.detecting = False
                previous_frame = None
                self.alerts = 0

        if self.config.detecting:
            det.release()
            if self.config.debug:
                cv2.destroyWindow(f'det-{self.cam}')
