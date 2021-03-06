import numpy as np
from controllers import ThreadedController
import os
from tkinter import *
from tkinter import ttk
from PIL import Image
from PIL import ImageTk
import cv2
import sys


WINDOW_NAME = "DISPLAY"

class TkinterGuiController(ThreadedController):

    def __init__(self):
        super().__init__()

        self.gui_root = Tk()
        self.gui_root.geometry('800x600')
        self.gui_root.resizable(False, False)
        self.gui_root.title("Tkinter GUI")
        self.gui_root.columnconfigure(0, weight=1)
        self.gui_root.rowconfigure(0, weight=1)


        self.content_frame = ttk.Frame(self.gui_root, style='new.TFrame')
        self.content_frame.pack(fill=BOTH, expand=True)

        self.label1 = ttk.Label(self.content_frame,
                                text="Please press the buttons to Stat/Stop and Recording.",
                                font=("helvetica", 20),
                                style='L1.TLabel').grid(row=0, column=0, columnspan=2, padx=5, pady=10,sticky='sw')

        # buttons for
        self.startButton = ttk.Button(self.content_frame, text="Start Recording", style='B1.TButton',
                                      command=self.start_recording)
        self.startButton.grid(row=2, column=0,  padx=5, pady=25, sticky='se')

        self.stopButton = ttk.Button(self.content_frame, text="Stop Recording", style='B1.TButton',
                                     command=self.stop_recording)
        self.stopButton.grid(row=2, column=1,  padx=200, pady=25,sticky='se')


        self.startButton = ttk.Button(self.content_frame, text="Start Stream Engine", style='B1.TButton',
                                      command=self.start_stream)
        self.startButton.grid(row=4, column=0,  padx=5, pady=25, sticky='se')

        self.stopButton = ttk.Button(self.content_frame, text="Stop Stream Engine", style='B1.TButton',
                                     command=self.stop_stream)
        self.stopButton.grid(row=4, column=1,  padx=200, pady=25,sticky='se')

        self.startButton = ttk.Button(self.content_frame, text="Shutdown", style='B1.TButton',
                                      command=self.shutdown)
        self.startButton.grid(row=6, column=0,  padx=5, pady=25, sticky='se')

        self._running = True

    def start_recording(self):
        self.signal_start_record()
        print("start recording button pressed")

    def stop_recording(self):
        self.signal_stop_record()
        print("stop recording button pressed")

    def start_stream(self):
        self.signal_start_stream()
        print("start stream button pressed")

    def stop_stream(self):
        self.signal_stop_stream()
        print("stop stream button pressed")

    def shutdown(self):
        self.signal_shutdown()
        print("shutdown button pressed")
        self._running = False

    def notify_frame_data(self, image):
        pass


    def run(self):
        pass

    def main_thread_run(self):
        print("run tkinter gui controller")
        while self._running:
            self.gui_root.update()

    def __del__(self):
        super().__del__()
        # todo: tkinter deconstructor
