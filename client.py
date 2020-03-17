import socket
import cv2
import time

# client
IP_SERVER = "0.0.0.0"
PORT_SERVER = 953
TIMEOUT_SOCKET = 10
DEVICE_NUMBER = 0


if __name__ == '__main__':
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_client.settimeout(TIMEOUT_SOCKET)
    socket_client.connect((IP_SERVER, PORT_SERVER))

    conn = socket_client.makefile('wb')

    camera = cv2.VideoCapture(DEVICE_NUMBER)
    count = 0

    while(camera.isOpened()):
        try:
            ret, frame = camera.read()
            # print("shape", frame.shape)  # frame is numpy array: (480, 640, 3)
            byteImage = frame.tobytes()
            conn.write(byteImage)

            count += 1
            print('Frame: ', count, 'Size:', len(byteImage))
            time.sleep(0.5)  # for easy debug

        except Exception as e:
            print("[Error] " + str(e))

    socket_client.close()