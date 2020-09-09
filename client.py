import socket
import sys
import threading

SERVER_HOST_NAME = ""
SERVER_PORT_NUMBER = 0
CLIENT_NAME = ""
TCP_port = 0
MESSAGE_LENGTH = 1024 * 1024 * 2  # 2MB is maximum length


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

    connected_successfully = check_client_name()
    while connected_successfully != 0:
        print("Enter your name")
        CLIENT_NAME = input("> ")
        connected_successfully = check_client_name()


def check_client_name():
    client = make_connection(SERVER_HOST_NAME, SERVER_PORT_NUMBER)
    send_tcp_message(client, "checkuser:{} {}:{}".format(CLIENT_NAME, 'localhost', TCP_port))
    response = client.recv(MESSAGE_LENGTH).decode("utf-8")
    if response == "OK NAME":
        print("Connected to server successfully")
        return 0
    if response == "CHANGE NAME":
        print("There's someone with your name in the server, please pick another one")
        return -1


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


def start_tcp_server():
    global TCP_port

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 0))
    TCP_port = server.getsockname()[1]

    server.listen()
    while True:
        connection, socket_address = server.accept()
        threading.Thread(target=handle_received_message, args=[connection]).start()


def handle_received_message(connection):
    message = connection.recv(MESSAGE_LENGTH).decode("utf-8")
    print("Message Received: {}".format(message))


def show_guidance():
    print("Guidance:")
    print("join GROUP_ID  -> joins to group with GROUP_ID in server, if there isn't creates one")


def send_join_request(given_command):
    if len(given_command.split(" ")) == 2:
        client = make_connection(SERVER_HOST_NAME, SERVER_PORT_NUMBER)
        group_id = given_command.split(" ")[1]
        send_tcp_message(client, "join {} {}".format(group_id, CLIENT_NAME))
        response = client.recv(MESSAGE_LENGTH).decode("utf-8")
        if response == "JOINED":
            print("Joined successfully")


if __name__ == "__main__":
    threading.Thread(target=start_tcp_server).start()
    get_server_host_name()
    get_server_port_number()
    get_client_name()

    show_guidance()

    while True:
        command = input("> ")
        if command.startswith("join"):
            send_join_request(command)
