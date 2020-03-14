import socket
from threading import Thread

# server
SERVER_IP = "0.0.0.0"
SERVER_PORT = 953
MAX_NUM_CONNECTIONS = 20
# image
IMAGE_HEIGHT = 480
IMAGE_WIDTH = 640
COLOR_PIXEL = 3  # RGB

class ConnectionPool(Thread):

    def __init__(self, ip_, port_, conn_):
        Thread.__init__(self)
        self.ip = ip_
        self.port = port_
        self.conn = conn_
        print("[+] New server socket thread started for " + self.ip + ":" + str(self.port))

    def run(self):
        count = 0
        try:
            while True:
                data = self.conn.recv(IMAGE_HEIGHT * IMAGE_WIDTH * COLOR_PIXEL)
                if not data:
                    break
                print(count, len(data))
                count += 1
        except Exception, e:
            print "Connection lost with " + self.ip + ":" + str(self.port) + "\r\n[Error] " + str(e.message)
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