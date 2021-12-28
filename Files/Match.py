import threading
import random

from ANSI import *

'''
Here we implemented the game rules and the data/result sent from server to client 
at each match. We got two threads, one for group1 and another for group2 counting 
how many chars received from each group in every match.
'''


class Match:

    def __init__(self, Str):
        self.Str = Str
        self.Player1 = None
        self.Player2 = None
        self.name1 = None
        self.name2 = None
        self.player1_result = 0
        self.player2_result = 0
        self.threadLock1 = threading.Lock()
        self.threadLock2 = threading.Lock()

    def print_names(self):  # this helps the cuurent client to know his identity during the match
        if threading.current_thread() is self.Player1:
            return "The name of this Client 1 is:" + self.name1
        else:
            return "The name of this Client 2 is:" + self.name2

    def player1_AnswerCorrect(self):
        with self.threadLock1:
            self.player1_result += 1

    def player2_AnswerCorrect(self):
        with self.threadLock2:
            self.player2_result += 1

    def start_game_msg(self):  # this message is for the start of the game
        start_msg = ANSI.YELLOW + self.print_names() + "\n" + ANSI.END
        start_msg += ANSI.CYAN + "\nWelcome to Quick Maths." + ANSI.END
        start_msg += (ANSI.YELLOW + "\nPlayer 1:  " + ANSI.END)
        start_msg = ANSI.YELLOW + start_msg + "\n" + self.name1 + "\n" + ANSI.END
        start_msg += ANSI.YELLOW + "Player 2:  " + ANSI.END
        start_msg += ANSI.BOLD + "\n" + self.name2 + "\n" + ANSI.END
        start_msg += ANSI.CYAN + "Please answer the following question as fast as you can:" + "\n" + ANSI.END
        start_msg += ANSI.CYAN + "How much is " + self.Str + "?" + "\n" + ANSI.END
        return start_msg

    def print_result(self):
        result = ""
        if self.player1_result > self.player2_result:
            winner = self.name1
            return result + '\n' + ANSI.CYAN + "Congratulations to the winner:\n" + ANSI.END + winner
        elif self.player2_result > self.player1_result:
            winner = self.name2
            return result + '\n' + ANSI.CYAN + "Congratulations to the winner:\n" + ANSI.END + winner
        else:
            result = ("\n" + ANSI.RED + "Game Over!" + ANSI.END + "\n")
            return result + ANSI.YELLOW + "Draw!" + ANSI.END + "\n" + ANSI.GREEN_ITALIC

    def setPlayer1(self, team_name, client_thread):
        self.Player1 = client_thread
        self.name1 = team_name

    def setPlayer2(self, team_name, client_thread):
        self.Player2 = client_thread
        self.name2 = team_name

    def run_threads(self):  # running each thread to start the match
        self.Player1.start()
        self.Player2.start()

    def join_threads(self):
        self.Player1.join()
        self.Player2.join()
