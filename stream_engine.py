import socket
import numpy as np
import os
import sys
import threading
import time
import signal
import termios

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
                        print("space -> start to run")
                        return self.state_func__run


            except KeyboardInterrupt:
                pass

        finally:
            if orig_settings is not None:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)



    def state_func__run(self):
        print("start run")

        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_server.bind((SERVER_IP, SERVER_PORT))
        socket_server.listen(MAX_NUM_CONNECTIONS)

        # currently, just focus on one client with one tcp connection
        (conn, (ip, port)) = socket_server.accept()
        self.rfile = conn.makefile('rb')


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
                        print(image_num, image.shape, len(stream_bytes))
                        frame = np.frombuffer(
                            image, dtype=np.uint8).reshape(IMAGE_HEIGHT, IMAGE_WIDTH, 3)

                        image_num += 1
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
