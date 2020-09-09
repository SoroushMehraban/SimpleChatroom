import socket
import sys

SERVER_HOST_NAME = ""
SERVER_PORT_NUMBER = 0
CLIENT_NAME = ""


def get_server_host_name():
    global SERVER_HOST_NAME
    try:
        SERVER_HOST_NAME = sys.argv[1]
    except IndexError:  # if there isn't any argument
        print("Enter server you want to connect:")
        SERVER_HOST_NAME = input("> ")


def get_server_port_number():
    global SERVER_PORT_NUMBER
    try:
        SERVER_PORT_NUMBER = int(sys.argv[2])
    except (IndexError, ValueError):  # if there isn't any argument or invalid argument
        while True:
            try:
                print("Enter server port number:")
                SERVER_PORT_NUMBER = int(input("> "))
                break
            except ValueError:
                print("Your input should be an integer")


def get_client_name():
    global CLIENT_NAME
    try:
        CLIENT_NAME = sys.argv[3]
    except IndexError:  # if there isn't any argument
        print("Enter your name")
        CLIENT_NAME = input("> ")


def make_connection(address, port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((address, port))
        return client
    except Exception:
        print("Connection failed")
        exit(1)


def send_tcp_message(source_socket, msg):
    message = msg.encode("utf-8")
    source_socket.send(message)


def send_message_to_server(message):
    client = make_connection(SERVER_HOST_NAME, SERVER_PORT_NUMBER)
    send_tcp_message(client, message)
    client.close()


if __name__ == "__main__":
    get_server_host_name()
    get_server_port_number()
    get_client_name()

    send_message_to_server("Hello from client")
    send_message_to_server("Another message from client")
