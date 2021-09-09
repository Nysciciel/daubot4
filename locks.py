import threading
from treasureHuntObjects import msg_list
import pygame

pygame.mixer.init()
pygame.mixer.music.load("alert.wav")

class LockManager:
    def __init__(self):
        self.lock_dict = {msg: threading.Event() for msg in msg_list}

    def release(self, msg):
        self.lock_dict[msg].set()

    def acquire(self, msg, timeout=10):
        print("Acquired " + msg)
        if not self.lock_dict[msg].wait(timeout):
            pygame.mixer.music.play()
            assert False, "Lock ran out"
        self.lock_dict[msg].clear()
        print("Released " + msg)

    def prepare_to_wait(self, msg):
        self.lock_dict[msg].clear()
