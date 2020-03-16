import os
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import sys

class StreamServerGui:
    def __init__(self, master):
        self.content_frame = ttk.Frame(master, style='new.TFrame')
        self.content_frame.pack(fill=BOTH, expand=True)

        self.label1 = ttk.Label(self.content_frame, text="Please press the buttons to Stat or Stop recording.",font=("helvetica", 20),
                                style='L1.TLabel').grid(row=0, column=0, columnspan=2, padx=5, pady=10,sticky='sw')

        self.startButton = ttk.Button(self.content_frame, text="Start", style='B1.TButton',command=self.start_recording)
        self.startButton.grid(row=2, column=0,  padx=5, pady=25, sticky='se')


        self.stopButton = ttk.Button(self.content_frame, text="Stop", style='B1.TButton',command=self.stop_recording)
        self.stopButton.grid(row=2, column=1,  padx=200, pady=25,sticky='se')

        load = Image.open("img.jpg")
        load = load.resize((250, 250), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        self.img = ttk.Label(self.content_frame, image=render)
        self.img.image = render
        self.img.place(x=500, y=0)


    def start_recording(self):
        print("start button pressed")

    def stop_recording(self):
        print("stop button pressed")


def gui_config(self):
    self.geometry('800x600')
    self.resizable(False, False)
    self.title("Stream Server System")
    self.columnconfigure(0, weight=1)
    self.rowconfigure(0, weight=1)
    bhs = StreamServerGui(self)
    return bhs


def test_GUI():
    gui_root = Tk()
    gui_config(gui_root)

    while True:
        gui_root.update()



if __name__ == "__main__":
    test_GUI()


