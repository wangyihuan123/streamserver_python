import sys
import os
import signal
import time
from functools import partial
from stream_engine import StreamEngine
from opencv_image_controller import OpencvImageController

def run_main_loop():
    try:
        while True:
            # currently nothing to do here but spin
            time.sleep(0.05)
            continue
    except KeyboardInterrupt:
        pass


def main():
    engine = StreamEngine()

    opencv_image_controller = OpencvImageController()
    if opencv_image_controller is not None:
        engine.register_controller(opencv_image_controller)

    engine.start()

    # blocking call
    run_main_loop()

    # Wait until engine (and by extension all registered controllers) have shut down in an orderly manner.
    engine.join(10.0)

if __name__ == "__main__":
    main()
