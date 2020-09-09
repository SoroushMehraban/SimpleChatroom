import socket
import threading
import sys

SERVER_ADDRESS = 'localhost'
try:
    SERVER_PORT = int(sys.argv[1])
except (ValueError, IndexError):
    while True:
        try:
            print("Enter server port number:")
            SERVER_PORT_NUMBER = int(input("> "))
            break
        except ValueError:
            print("Your input should be an integer")

MESSAGE_LENGTH = 1024 * 1024 * 2  # 2MB is maximum length


def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_ADDRESS, SERVER_PORT))

    print("-----------------------------------------")
    print("[TCP SERVER LISTENS] address:{} | port:{}".format(SERVER_ADDRESS, SERVER_PORT))
    print("-----------------------------------------")

    server.listen()
    while True:
        connection, socket_address = server.accept()
        threading.Thread(target=handle_request, args=[connection]).start()


def handle_request(connection):
    message = connection.recv(MESSAGE_LENGTH).decode("utf-8")
    print("Message Received: {}".format(message))


if __name__ == "__main__":
    start_tcp_server()