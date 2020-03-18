import cv2
import numpy as np
from controllers import ThreadedController

WINDOW_NAME = "DISPLAY"

class OpencvImageController(ThreadedController):

    def __init__(self):
        super().__init__()

        # cv2.namedWindow(WINDOW_NAME)
        self.blank_image = np.zeros((480, 640, 3), np.uint8)
        self._image_to_show = self.blank_image
        self._running = True

    def notify_frame_data(self, image):
        self._image_to_show = image

    def run(self):
        print("run opencv controller")
        while self._running:

            if self._image_to_show is not None:
                cv2.imshow(WINDOW_NAME, self._image_to_show)
                self._image_to_show = None  # todo:

            k = cv2.waitKey(1)

            # Mask out all but the equivalent ASCII key code in the low byte
            k = k & 0xFF
            if k == 32:  # SPACE to start stream
                print("space from opencv controller")
                self.signal_start_stream()
            elif k == ord('s'):  # stop
                self.signal_stop_stream()
            elif k == ord('r'):  # record
                self.signal_start_record()
            elif k == ord('e'):  # end
                self.signal_stop_record()

            elif k == ord('q'):
                self.signal_shutdown()
                self._running = False

def __del__(self):
        super().__del__()
        cv2.destroyAllWindows()
