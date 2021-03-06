import socket
import sys
import threading
import os

SERVER_HOST_NAME = ""
SERVER_PORT_NUMBER = 0
CLIENT_NAME = ""
TCP_port = 0
MESSAGE_LENGTH = 1024 * 1024 * 2  # 2MB is maximum length


# gets server host name from the first argument of the program. if there isn't then gets it manually
def get_server_host_name():
    global SERVER_HOST_NAME
    try:
        SERVER_HOST_NAME = sys.argv[1]
    except IndexError:  # if there isn't any argument
        print("Enter server you want to connect:")
        SERVER_HOST_NAME = input("> ")


# gets server port number from the second argument of the program. if there isn't any or its invalid then gets it
# manually
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


# gets client name from the third argument of program. if there isn't then gets it manually
# after getting client name. sends a request to server to make sure it's unique. if it's not then tells user to pick
# another one
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


# this function connects to the server and sends it a checkuser message (explained in server.py)
# it make sures that client name is unique
# if its unique it returns 0 otherwise it returns 1
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
    client.close()


# this function tries to make a connection to the server. if server rejected it exits the program
def make_connection(address, port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((address, port))
        return client
    except Exception:
        print("Connection failed")
        os._exit(1)


# this function decode the message into a binary format and sends it via socket like a stream
def send_tcp_message(source_socket, msg):
    message = msg.encode("utf-8")
    source_socket.send(message)


# this is a client server side function which just receives messages from others in the group
# for better understanding you have to look start_tcp_server in server.py
def start_tcp_server():
    global TCP_port

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 0))
    TCP_port = server.getsockname()[1]

    server.listen()
    while True:
        connection, socket_address = server.accept()
        threading.Thread(target=handle_received_message, args=[connection]).start()


# this function handles every message given by server by just printing it
def handle_received_message(connection):
    message = connection.recv(MESSAGE_LENGTH).decode("utf-8")
    print(message)
    print("-------")
    print(">", end=" ")
    sys.stdout.flush()


# shows guidance to the user at the first
def show_guidance():
    print("Guidance:")
    print("join GROUP_ID  -> Join to group with GROUP_ID in server, if there isn't creates one")
    print("send GROUP_ID MESSAGE -> Send MESSAGE to everyone joined in group with GROUP_ID")
    print("leave GROUP_ID -> Leave from a group with GROUP_ID")
    print("quit -> Quit from chatroom")
    print("----------------------------------------------------------------------------------")


# this function is called when user tries to join a group in chatroom
# it does his job whenever the given format is "join [group_id]" so the length is 2
# it makes a connection to server, sends a tcp message to it and waits for response
# after receiving response, it prints it and then closes the connection
def send_join_request(given_command):
    if len(given_command.split(" ")) == 2:
        client = make_connection(SERVER_HOST_NAME, SERVER_PORT_NUMBER)
        group_id = given_command.split(" ")[1]
        send_tcp_message(client, "join {} {}".format(group_id, CLIENT_NAME))
        response = client.recv(MESSAGE_LENGTH).decode("utf-8")
        print(response)
        client.close()


# this function is called when user tries to send a message to a group
# it does his job whenever the given format is "send [group id] [message]" so the length is more than 2
# if makes a connection to server, sends the message to it and waits for response
# after receiving response it prints it then closes the connection
def send_message_request(given_command):
    if len(given_command.split(" ")) >= 3:
        client = make_connection(SERVER_HOST_NAME, SERVER_PORT_NUMBER)
        group_id = given_command.split(" ")[1]
        user_message = ""
        for word in given_command.split(" ")[2:]:
            user_message += word + " "
        send_tcp_message(client, "MESSAGE: {} {} {}".format(CLIENT_NAME, group_id, user_message))
        response = client.recv(MESSAGE_LENGTH).decode("utf-8")
        print(response)
        client.close()


# this function is called when user tries to leave a group in chatroom
# it does his job whenever the given format is "leave [group id]" so the length is equal to 2
# if makes a connection to server, sends the message to it and waits for response
# after receiving response it prints it then closes the connection
def send_leave_request(given_command):
    if len(given_command.split(" ")) == 2:
        client = make_connection(SERVER_HOST_NAME, SERVER_PORT_NUMBER)
        group_id = given_command.split(" ")[1]
        send_tcp_message(client, "LEAVE: {} {}".format(group_id, CLIENT_NAME))
        response = client.recv(MESSAGE_LENGTH).decode("utf-8")
        print(response)


# this function is called whenever user types quit and wants to quit the program
# it makes a connection to server and let him know that by sending "QUIT: [client name]"
# so by doing this server will know and delete users record so someone else can login with this client name again
def send_quit_request():
    client = make_connection(SERVER_HOST_NAME, SERVER_PORT_NUMBER)
    send_tcp_message(client, "QUIT: {}".format(CLIENT_NAME))


# this function gets command from user. so it's basically the program user interface
def get_commands():
    while True:
        command = input("> ")
        if command.startswith("join"):
            send_join_request(command)
        if command.startswith("send"):
            send_message_request(command)
        if command.startswith('leave'):
            send_leave_request(command)
        if command == 'quit':
            send_quit_request()
            os._exit(0)  # exiting the entire threads


if __name__ == "__main__":
    threading.Thread(target=start_tcp_server).start()
    get_server_host_name()
    get_server_port_number()
    get_client_name()

    show_guidance()
    get_commands()
