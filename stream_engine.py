import socket
import numpy as np
import os
import sys
import threading
import time
import signal
import termios
import queue
import weakref
from datetime import datetime
import cv2
import uuid
from controllers import Controller

# Socket server configuration
SERVER_IP = "0.0.0.0"
SERVER_PORT = 953
MAX_NUM_CONNECTIONS = 20


# image
IMAGE_HEIGHT = 480
IMAGE_WIDTH = 640
COLOR_PIXEL = 3  # RGB
IMAGE_SIZE = IMAGE_WIDTH * IMAGE_HEIGHT * COLOR_PIXEL


class StreamEngine(threading.Thread):
    """Stream Engine."""

    def __init__(self):
        threading.Thread.__init__(self)
        self._controllers = []
        self._command_queue = queue.Queue(10)
        self.session_id = str(uuid.uuid4())
        self.recording = False
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

    def __del__(self):
        # Unplug any registered controllers
        for c in self._controllers:
            try:
                c._set_engine(None)
            except ReferenceError:
                pass

    # ========================================================================================
    # Interface used by associated controllers
    def register_controller(self, controller):

        # Use weakref proxies between engine and controllers to avoid circular reference leading to undead objects
        p = weakref.proxy(controller)
        if p not in self._controllers:
            self._controllers.append(p)
            controller._set_engine(self)

    def deregister_controller(self, controller):

        p = weakref.proxy(controller)
        if p in self._controllers:
            self._controllers.remove(p)


    def post_command(self, command, args=None):
        # If queue full discard oldest command
        if self._command_queue.full():
            self._command_queue.get(block=False)

        self._command_queue.put({'cmd': command, 'args': args})

    def generateRecord(self):
        print("start generateRecord")
        now = datetime.now()  # current date and time

        date_time = now.strftime("%m_%b_%H_%M_%S")
        print("date_time", datetime)
        # Define the codec and create VideoWriter object
        record_name_ = self.session_id + "_video_" + date_time + ".avi"
        print("video name {}".format(record_name_))
        self.out = cv2.VideoWriter(record_name_, self.fourcc, 20.0, (640, 480))  # 20 frame/per second
        print("generated video")

    # ========================================================================================
    # In each of the following notify methods iterate over copy of <_controllers> so in case
    # of encountering expired reference can remove it without invalidating iterator.
    def _notify_controllers_of_start(self):

        for c in self._controllers[:]:
            try:
                c.notify_start_controller_threads()
            except ReferenceError:
                # Shouldn't happen as controllers deregister themselves upon destruction
                self._controllers.remove(c)


    def _notify_controllers_of_update_framedata(self, image):

        for c in self._controllers[:]:
            try:
                c.notify_frame_data(image)
            except ReferenceError:
                # Shouldn't happen as controllers deregister themselves upon destruction
                self._controllers.remove(c)

    # ==================================================================================================================
    # State machine state functions

    def state_func__idle(self):
        """ Ready for streaming images, but not running capture
            Checking keyborad input to start
        """
        print("start idle")

        # Modify terminal settings to
        # a)not buffer input characters till RETURN key recieved
        # b) not echo input characters.
        # Linux specific code, use msvcrt on Windows
        try:
            orig_settings = termios.tcgetattr(sys.stdin)
            new_settings = list(orig_settings)
            new_settings[3] = new_settings[3] & ~(termios.ICANON | termios.ECHO)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)
        except termios.error:
            # Modification not available in particular terminal/terminal emulator we're currently running in.
            orig_settings = None

        try:
            try:
                while True:

                    k = sys.stdin.read(1)[0]  # Blocking call

                    # Mask out all but the equivalent ASCII key code in the low byte
                    k = ord(k) & 0xFF

                    if k == 32:  # SPACE
                        print("space -> start to run stream engine")
                        return self.state_func__run


            except KeyboardInterrupt:
                pass

        finally:
            if orig_settings is not None:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)



    def state_func__run(self):
        print("start stream engine")

        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_server.bind((SERVER_IP, SERVER_PORT))
        socket_server.listen(MAX_NUM_CONNECTIONS)

        # currently, just focus on one client with one tcp connection
        (conn, (ip, port)) = socket_server.accept()
        self.rfile = conn.makefile('rb')


        # start the threads of controller here
        # you can actually change the start places as you like
        self._notify_controllers_of_start()

        image_num = 0

        while True:

            time.sleep(0.05)
            stream_bytes = b''

            try:
                while True:

                    stream_bytes += self.rfile.read(1024)
                    while len(stream_bytes) >= IMAGE_SIZE:

                        image = np.frombuffer(stream_bytes[:IMAGE_SIZE], dtype="B")
                        stream_bytes = stream_bytes[IMAGE_SIZE:]

                        image_num += 1
                        print(image_num, image.shape, len(stream_bytes))
                        frame = np.frombuffer(
                            image, dtype=np.uint8).reshape(IMAGE_HEIGHT, IMAGE_WIDTH, 3)

                        self._notify_controllers_of_update_framedata(frame)

                        # write the frame to video
                        if self.recording:
                            self.out.write(frame)
                            print("recording")


                    while not self._command_queue.empty():
                        cmd_obj = self._command_queue.get(block=False)
                        cmd = cmd_obj['cmd']

                        if cmd == Controller.CMD_START_STREAM:
                            print("get cmd: start_stream")
                            print("Stream engine already started")
                        elif cmd == Controller.CMD_STOP_STREAM:
                            print("get cmd: stop_stream")
                            socket_server.close()
                            return self.state_func__idle
                        elif cmd == Controller.CMD_START_RECORD:
                            print("get cmd: start_record")
                            self.generateRecord()
                            self.recording = True
                        elif cmd == Controller.CMD_STOP_RECORD:
                            print("get cmd: stop_record")
                            self.recording = False

            except:
                print("Unexpected error:", sys.exc_info()[0])


    def run(self):
        try:

            # Run state machine.
            state_func = self.state_func__idle()

            while state_func is not None:

                state_func = state_func()

        finally:
            os.kill(os.getpid(), signal.SIGINT)
            print("shutting down")
