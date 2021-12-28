import threading
import random

from ANSI import *

'''
Here we implemented the game rules and the data/result sent from server to client 
at each match. We got two threads, one for group1 and another for group2 counting 
how many chars received from each group in every match.
'''


class control:
    __instance = None
    j = 0

    @staticmethod
    def getInstance():  # control class is a singleton class we have used it to find out the  first client who answers
        """ Static access method. """
        if control.__instance is None:
            control()
        return control.__instance

    def __init__(self):
        self.lock = threading.Lock()
        lk = threading.Lock()
        lk.acquire()
        """ Virtually private constructor. """
        if control.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            control.__instance = self

    @classmethod
    def getJ(cls):  # synchronized methods to make sure only one client thread enters at the time
        cls.lock = threading.Lock()
        cls.lock.acquire()
        cls.j += 1
        cls.lock.release()
        return cls.j - 1

    @classmethod
    def resetJ(cls):  # synchronized methods to make sure only one client thread enters at the time
        cls.lock = threading.Lock()
        cls.lock.acquire()
        cls.j = 0
        cls.lock.release()

