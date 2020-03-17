import cv2
import numpy as np
from controllers import ThreadedController

WINDOW_NAME = "DISPLAY"

class OpencvImageController(ThreadedController):

    CMD_SHUTDOWN = 0
    CMD_START_CAPTURE = 1

    def __init__(self):
        super().__init__()

        # cv2.namedWindow(WINDOW_NAME)
        self._image_to_show = np.zeros((480, 640, 3), np.uint8)  # blank image

    def notify_frame_data(self, image):
        self._image_to_show = image

    def run(self):
        print("run opencv controller")
        while True:

            if self._image_to_show is not None:
                cv2.imshow(WINDOW_NAME, self._image_to_show)
                # self._image_to_show = None

            k = cv2.waitKey(1)

            # Mask out all but the equivalent ASCII key code in the low byte
            k = k & 0xFF
            if k == 32:  # SPACE
                print("space from opencv controller")

