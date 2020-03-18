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
import traceback

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
        self.record_dir = "../record_data/"
        self._running = True

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

        date_time = now.strftime("%d_%b_%H_%M_%S")
        print("date_time", datetime)
        # Define the codec and create VideoWriter object
        record_name_ = self.record_dir + self.session_id + "_video_" + date_time + ".avi"
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


    def _notify_controllers_of_shutdown(self):

        for c in self._controllers[:]:
            try:
                c.notify_shutdown()
            except ReferenceError:
                # Shouldn't happen as controllers deregister themselves upon destruction
                self._controllers.remove(c)

    # ==================================================================================================================
    # State machine state functions

    def state_func__idle(self):
        """ Ready for streaming images, but not running capture
            Checking input to start from either terminal(keyboard) or gui
        """
        print("stream engine state -> idle")
        while True:
            if not self._running:
                return None

            while not self._command_queue.empty():
                cmd_obj = self._command_queue.get(block=False)
                cmd = cmd_obj['cmd']

                if cmd == Controller.CMD_START_STREAM:
                    print("get cmd: start_stream")
                    return self.state_func__run
                elif cmd == Controller.CMD_SHUTDOWN:
                    print("get cmd: shutdown")
                    # todo: ensure the video is complete
                    self._running = False
                    self._notify_controllers_of_shutdown()

            time.sleep(0.2)


    def state_func__run(self):
        print("stream engine state -> run")

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

        # while True:
        #     time.sleep(0.05)
        stream_bytes = b''

        try:
            while self._running:

                stream_bytes += self.rfile.read(1024)
                if len(stream_bytes) < IMAGE_SIZE:
                    continue  # keep receiving until receive a whole image

                image = np.frombuffer(stream_bytes[:IMAGE_SIZE], dtype="B")
                stream_bytes = stream_bytes[IMAGE_SIZE:]  # todo: the rest should be moved to another engine

                image_num += 1
                print(image_num, image.shape, len(stream_bytes))
                frame = np.frombuffer(
                    image, dtype=np.uint8).reshape(IMAGE_HEIGHT, IMAGE_WIDTH, 3)

                self._notify_controllers_of_update_framedata(frame)

                # write the frame to video
                if self.recording:
                    self.out.write(frame)  # todo: should be moved to another thread
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
                    elif cmd == Controller.CMD_SHUTDOWN:
                        print("get cmd: shutdown")
                        # todo: ensure the video is complete
                        self._running = False
                        self._notify_controllers_of_shutdown()

        except:
            print("Unexpected error:", sys.exc_info()[0])
            self.exit_code = 1

        return None

    def run(self):
        try:

            # Run state machine.
            state_func = self.state_func__idle()
            self.exit_code = 0

            while state_func is not None:

                state_func = state_func()

        except Exception as e:
            print("ImageCaptureEngine.run() - unexpected exception \n %s \n %s" % (str(e), traceback.format_exc()))
            self.exit_code = 1

        except:
            print("ImageCaptureEngine.run() - unexpected exception \n %s" % traceback.format_exc())
            self.exit_code = 1
        finally:
            self._notify_controllers_of_shutdown()
            # os.kill(os.getpid(), signal.SIGINT)
            print("shutting down")
