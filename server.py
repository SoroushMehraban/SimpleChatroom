import socket
import threading
import sys

SERVER_ADDRESS = 'localhost'
try:
    SERVER_PORT = int(sys.argv[1])  # getting server port from first argument
except (ValueError, IndexError):  # if argument is empty or port is not an integer:
    while True:
        try:
            print("Enter server port number:")
            SERVER_PORT_NUMBER = int(input("> "))
            break
        except ValueError:
            print("Your input should be an integer")

MESSAGE_LENGTH = 1024 * 1024 * 2  # 2MB is maximum length
current_users_dict = {}  # holds users which are currently connected to this server as a key and their host info as a value
group_dict = {}  # holds group id as a key and list of users inside a group as a value


# This function starts our TCP server
# at first it creates a socket. socket.AF_INET means  to user IPv4 and socket.SOCK_STREAM means to use TCP as a transport layer
# then it binds to our host info which is localhost:[given_port_by_user]
# after creating socket it listens and after receiving a request it gives it to another function in separate thread
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


# function to handle requests given to server
# it first decode received binary message as a utf-8 and then do its job based on given message
def handle_request(connection):
    message = connection.recv(MESSAGE_LENGTH).decode("utf-8")
    print("Message Received: {}".format(message))

    # if someone try to login client gives its name and we have to decide if his name is unique or not
    # the format of the message is "checkuser:[client name] [client host info]"
    if message.startswith("checkuser:"):
        user = message.split("checkuser:")[1].split(" ")[0]
        user_host_info = message.split(" ")[1]

        if user in current_users_dict:
            connection.send("CHANGE NAME".encode("utf-8"))
        else:
            current_users_dict[user] = user_host_info
            connection.send("OK NAME".encode("utf-8"))
            print("Current users:")
            print(current_users_dict)
            print("-------------------")

    # if someone tries to join a group chat client sends a join request
    # the format of the message is "join [group id] [client name]"
    # if there isn't any group with a group id given after join request then we create one
    # if we have we join that user into that group
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

    # if someone tries to send a message into a group client sends a MESSAGE requests
    # the format of the message is "MESSAGE: [client name] [group id] [message to send]"
    # we check if user is in group or not. if he is we send the message to the group otherwise we show him an error
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

    # if someone tries to leave a group client sends a LEAVE request
    # the format of the message is "LEAVE: [group id] [client name]"
    # if he is in group we remove him and let him know that otherwise we show him an error
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

    # when user wants to quit a program. before quiting client sends a QUIT request
    # the format of the message is "QUIT: [client name]"
    # we remove the user on both dictionary so that someone can login with his client name after that
    if message.startswith("QUIT:"):
        client_name = message.split(" ")[1]
        del current_users_dict[client_name]
        for group in group_dict:
            if group_dict[group].__contains__(client_name):
                group_dict[group].remove(client_name)


# this function sends @message_to_send to everyone in group with @group_id except @sender
def send_message_to_group(message_to_send, group_id, sender):
    for user in group_dict[group_id]:
        if user == sender:
            continue
        user_info = current_users_dict[user]
        user_socket = make_connection(user_info)
        send_tcp_message(user_socket, "\nMessage from group {}:\n".format(group_id))
        send_tcp_message(user_socket, message_to_send)
        user_socket.close()


# this function tries to make a connection to a user with @user_info which is a string like "IP_address:port"
def make_connection(user_info):
    user_ip = user_info.split(":")[0]
    user_port = int(user_info.split(":")[1])
    try:
        user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        user_socket.connect((user_ip, user_port))
        return user_socket
    except Exception:
        print("Connection failed to user {}".format(user_info))


# this function encode the string in binary format and sends the message via given socket
def send_tcp_message(source_socket, msg):
    message = msg.encode("utf-8")
    source_socket.send(message)


if __name__ == "__main__":
    start_tcp_server()
