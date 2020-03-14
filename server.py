import socket
from threading import Thread
import base64
import numpy as np
import cv2

# server
SERVER_IP = "0.0.0.0"
SERVER_PORT = 953
MAX_NUM_CONNECTIONS = 20
# image
IMAGE_HEIGHT = 480
IMAGE_WIDTH = 640
COLOR_PIXEL = 3  # RGB
IMAGE_SIZE =  IMAGE_WIDTH * IMAGE_HEIGHT * COLOR_PIXEL

class ConnectionPool(Thread):

    def __init__(self, ip_, port_, conn_):
        Thread.__init__(self)
        self.ip = ip_
        self.port = port_
        self.conn = conn_
        self.rfile = self.conn.makefile('rb')
        print("[+] New server socket thread started for " + self.ip + ":" + str(self.port))

    def run(self):
        count = 0
        stream_bytes = b''

        try:
            while True:
                # https://stackoverflow.com/questions/51921631/how-to-send-and-receive-webcam-stream-using-tcp-sockets-in-python
                stream_bytes += self.rfile.read(1024)
                while len(stream_bytes) >= IMAGE_SIZE:
                    image = np.frombuffer(stream_bytes[:IMAGE_SIZE], dtype="B")
                    stream_bytes = stream_bytes[IMAGE_SIZE:]
                    print(image.shape, len(stream_bytes))
                    frame = np.frombuffer(
                        image, dtype=np.uint8).reshape(IMAGE_HEIGHT, IMAGE_WIDTH, 3)

                    print("frame", frame.shape)
                    cv2.imwrite("test.jpg", frame)


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
