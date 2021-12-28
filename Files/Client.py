import socket
import UDPMessage
import threading
import KeyListen
import ANSI
# Constant variables
TEAM_NAME = "Rocket\n"
BUFF_SIZE = 1024
MAX_TIMEOUT = 10


def client_listen(broadcast_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # udp socket creation
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # broadcast on
    client.bind(("", broadcast_port)) # binding broadcast with the socket to allow receiving invitations
    while True:
        data, addr = client.recvfrom(BUFF_SIZE) # wait for game invitations from servers broadcast
        invitation_port = UDPMessage.unpack_offer(data)
        if invitation_port is None:  # corrupted message
            continue
        host_name = addr[0]  # gets the senders ip
        msg = ANSI.get_cyan() + "Received offer from " + ANSI.get_end()+ANSI.get_yellow()+str(host_name)+ANSI.get_end()
        msg += (ANSI.get_cyan() + ", attempting to connect..." + ANSI.get_end())
        print(msg)
        client_connect(host_name, invitation_port)  # try to connect with the server to start the game
        clear_previous_invitations(client) # to make sure we don't access old invitations
        print(ANSI.get_cyan() + "\nServer disconnected, listening for offer requests..." + ANSI.get_end())


def client_connect(hostname, port):

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.settimeout(MAX_TIMEOUT)
    try:
        tcp_socket.connect((hostname, port)) # connecting to the server
    except socket.error as err:
        print(ANSI.get_red() + "Error while trying to connect to server : "+str(err) + ANSI.get_end())
        return
    try:
        tcp_socket.sendall(TEAM_NAME.encode())
    except socket.error as err:
        print(ANSI.get_red() + "Error at sending the team name : "+str(err) + ANSI.get_red())
        tcp_socket.close() # closing he socket
        return
    tcp_socket.settimeout(socket.getdefaulttimeout())
    client_game(tcp_socket)  # client ready for starting the game


def client_game(conn_socket):
    stop_keyboard_event = threading.Event()
    keyboard_thread = threading.Thread(target=listen, args=(conn_socket, stop_keyboard_event,))
    try:
        welcome_message = conn_socket.recv(BUFF_SIZE).decode()  # decodes the welcome message sent from the server
        clear_input_buffer()  # clearing the buffer to avoid any mistakes
        print(welcome_message)
        keyboard_thread.start()  # start the keyboard thread to read from the clients
        while True:
            data = conn_socket.recv(BUFF_SIZE).decode()
            if not data:
                break
            print(data)  # print server message
        stop_keyboard_event.set()  # game is over
        conn_socket.close()  # closing connection
    except socket.error as err:
        print(ANSI.get_red() + "Error during the game : "+str(err) + ANSI.get_end())
        stop_keyboard_event.set()  # connection error occurs so we stop the keyboard thread
        conn_socket.close()  # cloe the connection
        return


def clear_previous_invitations(client):  # function to clear old invitations
    client.settimeout(0.0)
    while True:
        try:
            client.recv(BUFF_SIZE)
        except socket.error:
            client.settimeout(None)
            return


def listen(conn_socket, stop_keyboard):  # function that listens for the clients
    buffer_listener = KeyListen.KBHit()
    while not stop_keyboard.wait(0):  # loops until the main thread terminates the listen thread
        if buffer_listener.kbhit():  # when a key been hit
            buffered_char = buffer_listener.getch()  # try to send it to the server
            try:
                conn_socket.sendall(str(buffered_char).encode())  # encode and send
            except socket.error as err:
                print(ANSI.get_red() + "Could not send the keyboard input to server : " + str(err) + ANSI.get_end())


def clear_input_buffer():  # function to clear our buffer
    while KeyListen.KBHit().kbhit():
        KeyListen.KBHit().getch()


if __name__ == '__main__':
    ANSI.turn_on_colors()  # supporting ANSI colors on terminal
    broadcastPort = 13117
    print(ANSI.get_cyan() + "Client started, listening for offer requests..." + ANSI.get_end())
    client_listen(broadcastPort)    # start the client
