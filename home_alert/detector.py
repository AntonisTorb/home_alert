import time

import cv2
import numpy as np

from .configuration import Config

class Detector():
    def __init__(self, cam: int, config: Config) -> None:
        self.cam = cam
        self.config = config
        self.alerts = 0

    
    def detect(self):
        cap = cv2.VideoCapture(self.cam)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.detector_frame_width) 
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.detector_frame_height)
        cap.set(cv2.CAP_PROP_FPS, self.config.detector_frame_rate)
        if self.config.debug:
            print(f'Detector Framerate: {cap.get(cv2.CAP_PROP_FPS)}')
            print(f'Detector Frame Width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}')
            print(f'Detector Frame Height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}')

        previous_frame = None
        while True and not self.config.recording:
            if self.config.kill:
                break
            _, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.GaussianBlur(frame, (21,21), 0)

            if type(previous_frame) != np.ndarray:
                previous_frame = frame
                continue
                
            difference = cv2.absdiff(frame, previous_frame)
            threshold = cv2.threshold(difference, self.config.detector_threshold, 255, cv2.THRESH_BINARY)[1]
            if threshold.mean() > self.config.alert_threshold:
                self.alerts += 1
            else:
                if self.alerts > 0:
                    self.alerts -= 1
            if self.alerts > 20:
                self.config.recording = True
                break

            if self.config.debug:
                print(threshold.mean())
                cv2.imshow(f'cam-{self.cam}', threshold)
                cv2.waitKey(self.config.detector_frame_rate)
            
            previous_frame = frame

        cap.release()
        if self.config.debug:
            cv2.destroyWindow(f'cam-{self.cam}')


