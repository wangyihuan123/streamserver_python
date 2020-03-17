import socket
from threading import Thread
import uuid
import numpy as np
import cv2
from datetime import datetime


# server
SERVER_IP = "0.0.0.0"
SERVER_PORT = 953
MAX_NUM_CONNECTIONS = 20
# image
IMAGE_HEIGHT = 480
IMAGE_WIDTH = 640
COLOR_PIXEL = 3  # RGB
IMAGE_SIZE = IMAGE_WIDTH * IMAGE_HEIGHT * COLOR_PIXEL


class ConnectionPool(Thread):

    def __init__(self, ip_, port_, conn_):
        Thread.__init__(self)
        self.ip = ip_
        self.port = port_
        self.conn = conn_
        self.rfile = self.conn.makefile('rb')
        self.recording = False
        self.displaying = False
        self.blank_image = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3), np.uint8)
        self.session_id = str(uuid.uuid4())
        print("[+] New server socket thread started for " + self.ip + ":" + str(self.port))

    def generateRecord(self):

        now = datetime.now() # current date and time
        date_time = now.strftime("%m_%b_%H_%M_%S")

        # Define the codec and create VideoWriter object
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        record_name_ = self.session_id + "_video_" + date_time + ".avi"
        self.out = cv2.VideoWriter(record_name_, self.fourcc, 20.0, (640, 480))  # 20 frame/per second

    def run(self):
        count = 0
        stream_bytes = b''

        try:
            while True:
                image_compelet_ = False

                # https://stackoverflow.com/questions/51921631/how-to-send-and-receive-webcam-stream-using-tcp-sockets-in-python
                stream_bytes += self.rfile.read(1024)
                while len(stream_bytes) >= IMAGE_SIZE:
                    image = np.frombuffer(stream_bytes[:IMAGE_SIZE], dtype="B")
                    stream_bytes = stream_bytes[IMAGE_SIZE:]
                    # print(image.shape, len(stream_bytes))
                    frame = np.frombuffer(
                        image, dtype=np.uint8).reshape(IMAGE_HEIGHT, IMAGE_WIDTH, 3)

                    image_compelet_ = True

                    if image_compelet_:
                        if self.displaying:
                            cv2.imshow('VideoFrame', frame)
                            print("displaying")

                        # write the frame to video
                        if self.recording:
                            self.out.write(frame)
                            print("recording")

                    if not image_compelet_ or not self.displaying:
                        # print("blank")
                        cv2.imshow('image', self.blank_image)

                    key = cv2.waitKey(1)
                    key = key & 0xFF  # Mask out all but the equivalent ASCII key code in the low byte
                    if key == ord('q'):
                        break
                    elif key == 32:  # space to control recording
                        if self.recording:
                            self.recording = False
                        else:
                            self.generateRecord()
                            self.recording = True

                    elif key == ord('p'):  # p for play and pause
                        if self.displaying:
                            self.displaying = False
                            print("stop")
                        else:
                            self.displaying = True
                            print("start")

                    # print(count)
                    # count += 1
        except Exception, e:
            print("Connection lost with " + self.ip + ":" + str(self.port) + "\r\n[Error] " + str(e.message))

        self.conn.close()

if __name__ == '__main__':
    print("Waiting connections...")
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_server.bind((SERVER_IP, SERVER_PORT))
    socket_server.listen(MAX_NUM_CONNECTIONS)
    while True:
        (conn, (ip, port)) = socket_server.accept()
        thread = ConnectionPool(ip, port, conn)
        thread.start()
    socket_server.close()
    camera.release()
