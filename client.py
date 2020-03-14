import socket

IP_SERVER = "0.0.0.0"
PORT_SERVER = 953
TIMEOUT_SOCKET = 10
SIZE_PACKAGE = 4096


if __name__ == '__main__':
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.settimeout(TIMEOUT_SOCKET)
    connection.connect((IP_SERVER, PORT_SERVER))

    count = 0
    while True:
        try:
            connection.sendall(b'Hello, world ' + str(count))
            data = connection.recv(1024)
            print('Received', repr(data))
            count += 1
        except Exception as e:
            print("[Error] " + str(e))

    connection.close()