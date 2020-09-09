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
current_users_dict = {}
group_dict = {}


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
    if message.startswith("checkuser:"):
        user = message.split("checkuser:")[1].split(" ")[0]
        user_host_info = message.split(" ")[1]

        if user in current_users_dict:
            connection.send("CHANGE NAME".encode("utf-8"))
        else:
            current_users_dict[user] = user_host_info
            connection.send("OK NAME".encode("utf-8"))
            print(current_users_dict)

    if message.startswith("join"):
        group_id = message.split(" ")[1]
        user = message.split(" ")[2]
        if group_id in group_dict:
            if group_dict[group_id].__contains__(user):
                connection.send("ALREADY THERE".encode("utf-8"))
            else:
                group_dict[group_id].append(user)
                connection.send("JOINED".encode("utf-8"))
        else:
            group_dict[group_id] = [user]
            connection.send("JOINED".encode("utf-8"))


if __name__ == "__main__":
    start_tcp_server()
