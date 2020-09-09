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
                connection.send("[SERVER MESSAGE] You're already in there".encode("utf-8"))
            else:
                group_dict[group_id].append(user)
                connection.send("[SERVER MESSAGE] Joined successfully".encode("utf-8"))
        else:
            group_dict[group_id] = [user]
            connection.send("[SERVER MESSAGE] Joined successfully".encode("utf-8"))

    if message.startswith("MESSAGE:"):
        client_name = message.split(" ")[1]
        group_id = message.split(" ")[2]
        if group_id in group_dict and group_dict[group_id].__contains__(client_name):
            client_message = ""
            for word in message.split(" ")[3:]:
                client_message += word + " "
            client_message = client_message.strip()  # removing space at the end of it
            send_message_to_group("{}: {}".format(client_name, client_message), group_id, client_name)
            connection.send("[SERVER MESSAGE] Message sent successfully".encode("utf-8"))
        else:
            connection.send("[SERVER MESSAGE] You're not joined in this group. please join first".encode("utf-8"))
    if message.startswith("LEAVE:"):
        group_id = message.split(" ")[1]
        user = message.split(" ")[2]
        if group_id in group_dict:
            if group_dict[group_id].__contains__(user):
                group_dict[group_id].remove(user)
                connection.send("[SERVER MESSAGE] left successfully".encode("utf-8"))
            else:
                connection.send("[SERVER MESSAGE] You're not in this group".encode("utf-8"))
        else:
            connection.send("[SERVER MESSAGE] This group doesn't exist".encode("utf-8"))
    if message.startswith("QUIT:"):
        client_name = message.split(" ")[1]
        del current_users_dict[client_name]
        for group in group_dict:
            if group_dict[group].__contains__(client_name):
                group_dict[group].remove(client_name)


def send_message_to_group(message_to_send, group_id, sender):
    for user in group_dict[group_id]:
        if user == sender:
            continue
        user_info = current_users_dict[user]
        user_socket = make_connection(user_info)
        send_tcp_message(user_socket, "\nMessage from group {}:\n".format(group_id))
        send_tcp_message(user_socket, message_to_send)
        user_socket.close()


def make_connection(user_info):
    user_ip = user_info.split(":")[0]
    user_port = int(user_info.split(":")[1])
    try:
        user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        user_socket.connect((user_ip, user_port))
        return user_socket
    except Exception:
        print("Connection failed")
        exit(1)


def send_tcp_message(source_socket, msg):
    message = msg.encode("utf-8")
    source_socket.send(message)


if __name__ == "__main__":
    start_tcp_server()
