import socket
import threading

import UDPMessage
import time
import random
import Match
import ClientHandler
import ANSI
import control

BUFF_SIZE = 1024
MAX_TIMEOUT = 10
c = control


def server_broadcast(server_port, broadcast_port):
    broadcast_socket = create_broadcast_socket()
    message = UDPMessage.send_offer(server_port)
    server_socket = create_server_socket(server_port)
    team_names = ["Rocket\n", "Instinct\n"]
    while True:
        Str = ""
        # generating the equation
        a = random.randint(0, 4)
        b = random.randint(0, 5)
        Sum = a + b
        Str += str(a) + "+" + str(b)
        i = 0
        match = Match.Match(Str)
        stop_broadcast = time.time() + MAX_TIMEOUT

        while i < 2:  # we accept the first 2 clients connections, and then sleep 10 seconds and then start thr game
            broadcast_socket.sendto(message, ('<broadcast>', broadcast_port))
            try:
                conn, address = server_socket.accept()  # accept new connection
                conn.settimeout(None)
                team_name = receive_team_name(conn)  # accept new connection
                team_name = team_names[i]
                if team_name is None:
                    conn.close()
                else:
                    handler = ClientHandler.ClientHandler(conn, team_name, match, Sum, c.control.getInstance())
                    client_thread = threading.Thread(target=handler.start_game)
                    i += 1
                    print(ANSI.get_cyan() + "Connection from: " + str(address) + ANSI.get_end())
                    if match.Player1 is None:
                        match.setPlayer1(team_name, client_thread)
                    else:
                        match.setPlayer2(team_name, client_thread)
            except socket.error:
                print(end='\r')
            time.sleep(1)
        time.sleep(10)  # sleep 10secs after 2 client connect and start the match after the sleep
        match.run_threads()
        threading.current_thread()
        match.join_threads()


def create_broadcast_socket():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # broadcast socket
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # start broadcasting
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return udp_socket


def create_server_socket(server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', server_port))  # bind host address and port
    server_socket.settimeout(0.0)
    server_socket.listen()  # server start listening for clients
    return server_socket


def receive_team_name(client_socket):
    start_time = time.time()
    while True:

        try:
            team_name = str(client_socket.recv(BUFF_SIZE), 'utf-8')
            if not team_name:
                print(ANSI.get_red() + "Client socket closed" + ANSI.get_end())
                return None
            if team_name[len(team_name) - 1] == '\n':  # to make sure we have new line after each name
                clear_socket_input_buffer(client_socket)
                break
            else:
                client_socket.close()
                return None
        except socket.error as err:
            print(ANSI.get_red() + "Error while receiving the team name : " + str(err) + ANSI.get_end())
            return None
    return team_name[:len(team_name) - 1]


def clear_socket_input_buffer(client_socket):
    client_socket.settimeout(0.0)
    while True:
        try:
            client_socket.recv(BUFF_SIZE)
        except socket.error:
            client_socket.settimeout(None)
            break


if __name__ == '__main__':
    ANSI.turn_on_colors()
    serverPort = 2050  # the server port
    broadcastPort = 13117
    msg = ANSI.get_cyan() + "Server started,listening on IP address : " + ANSI.get_end()
    msg += (ANSI.get_yellow() + socket.gethostbyname(socket.gethostname()) + ANSI.get_end())
    print(msg)
    server_broadcast(serverPort, broadcastPort)
