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

    CMD_SHUTDOWN = 0
    CMD_START_CAPTURE = 1

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

        self.label1 = ttk.Label(self.content_frame, text="Please press the buttons to Stat or Stop recording.",font=("helvetica", 20),
                                style='L1.TLabel').grid(row=0, column=0, columnspan=2, padx=5, pady=10,sticky='sw')

        self.startButton = ttk.Button(self.content_frame, text="Start", style='B1.TButton',command=self.start_recording)
        self.startButton.grid(row=2, column=0,  padx=5, pady=25, sticky='se')


        self.stopButton = ttk.Button(self.content_frame, text="Stop", style='B1.TButton',command=self.stop_recording)
        self.stopButton.grid(row=2, column=1,  padx=200, pady=25,sticky='se')


    def start_recording(self):
        print("start button pressed")

    def stop_recording(self):
        print("stop button pressed")

    def notify_frame_data(self, image):
        pass


    def run(self):
        pass

    def main_thread_run(self):
        print("run tkinter gui controller")
        while True:
            self.gui_root.update()

    def __del__(self):
        super().__del__()
        # todo: tkinter deconstructor
