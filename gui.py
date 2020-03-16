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

        self.footer_frame = ttk.Frame(master,style='new.TFrame')
        self.footer_frame.pack(fill=BOTH)

        load = Image.open("img.jpg")
        load = load.resize((250, 250), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        self.img = ttk.Label(self.content_frame, image=render)
        self.img.image = render
        self.img.place(x=500, y=0)


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


