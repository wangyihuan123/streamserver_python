import socket
from threading import Thread

SERVER_IP = "0.0.0.0"
SERVER_PORT = 953
MAX_NUM_CONNECTIONS = 20
DEVICE_NUMBER = 0

class ConnectionPool(Thread):

    def __init__(self, ip_, port_, conn_):
        Thread.__init__(self)
        self.ip = ip_
        self.port = port_
        self.conn = conn_
        print("[+] New server socket thread started for " + self.ip + ":" + str(self.port))

    def run(self):
        try:
            while True:
                data = self.conn.recv(1024)
                if not data:
                    break
                self.conn.sendall(data)
        except Exception, e:
            print "Connection lost with " + self.ip + ":" + str(self.port) + "\r\n[Error] " + str(e.message)
        self.conn.close()


if __name__ == '__main__':
    print("Waiting connections...")
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind((SERVER_IP, SERVER_PORT))
    connection.listen(MAX_NUM_CONNECTIONS)
    while True:
        (conn, (ip, port)) = connection.accept()
        thread = ConnectionPool(ip, port, conn)
        thread.start()
    connection.close()
    camera.release()