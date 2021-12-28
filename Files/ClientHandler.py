import socket
import time
import threading
from ANSI import *
import control

# Constant variables
BUFF_SIZE = 1024


class ClientHandler:

    def __init__(self, connection_socket, team_name, match, Sum, c):
        self.client_socket = connection_socket
        self.team_name = team_name
        self.match = match
        self.Sum = Sum
        self.c = c
        self.j = 0

    def start_game(self):
        self.client_socket.settimeout(10)
        end_game = time.time() + 10
        try:
            self.client_socket.sendall(self.match.start_game_msg().encode())
        except socket.error as err:
            print(ANSI.RED + "Error while sending welcome message to team " + str(err) + ANSI.END)
            self.client_socket.close()
            return
        lock = threading.Lock()
        while time.time() < end_game:
            try:
                lock.acquire()
                timeOut = end_game - time.time()
                if timeOut < 0:
                    timeOut = 0
                self.client_socket.settimeout(timeOut)
                data = self.client_socket.recv(BUFF_SIZE).decode()  # data received from client
                if not data:  # nothing has been sent
                    break
                # print("DATAA==  " + data)
                # print("Sum==  " + str(self.Sum))
                # print(self.Sum == int(data))
                self.j = int(self.c.getJ())
                # print(self.j)
                if self.j % 2 == 0:  # we check if this is the first client who answered to determine the winner
                    if threading.current_thread() is self.match.Player1:
                        if self.Sum == int(data):
                            self.match.player1_AnswerCorrect()
                            end_game = time.time()
                        else:
                            self.match.player2_AnswerCorrect()
                            end_game = time.time()
                    else:
                        if self.Sum == int(data):
                            self.match.player2_AnswerCorrect()
                            end_game = time.time()
                        else:
                            self.match.player1_AnswerCorrect()
                            end_game = time.time()

            except socket.error:
                result_message = self.match.print_result()
                try:
                    self.client_socket.sendall(result_message.encode())
                    self.c.resetJ()
                except socket.error:
                    self.client_socket.close()
                print(end='\r')
                self.client_socket.close()  # connection closing
                return
            lock.release()
        result_message = self.match.print_result()
        try:
            self.client_socket.sendall(result_message.encode())  # make sure all data the clients write has been sent
            # to the server
        except socket.error:
            pass
        self.client_socket.close()
