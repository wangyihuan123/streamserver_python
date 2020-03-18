import sys
import os
import signal
import time
from functools import partial
from stream_engine import StreamEngine
from opencv_image_controller import OpencvImageController
from tkinter_gui_controller import TkinterGuiController
from terminal_controller import TerminalController


def main():
    engine = StreamEngine()

    terminal_controller = TerminalController()
    if terminal_controller is not None:
        engine.register_controller(terminal_controller)

    opencv_image_controller = OpencvImageController()
    if opencv_image_controller is not None:
        engine.register_controller(opencv_image_controller)

    tkinter_gui_controller = TkinterGuiController()
    if tkinter_gui_controller is not None:
        engine.register_controller(tkinter_gui_controller)

    engine.start()

    # https://stackoverflow.com/questions/14694408/runtimeerror-main-thread-is-not-in-main-loop
    tkinter_gui_controller.main_thread_run()

    # Wait until engine (and by extension all registered controllers) have shut down in an orderly manner.
    engine.join(10.0)

    sys.exit(engine.exit_code)

if __name__ == "__main__":
    main()
