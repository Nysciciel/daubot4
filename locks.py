import threading
from treasureHuntObjects import msg_list


class LockManager:
    def __init__(self):
        self.lock_dict = {msg: threading.Event() for msg in msg_list}

    def release(self, msg):
        self.lock_dict[msg].set()

    def acquire(self, msg, timeout=30):
        print("Acquired " + msg)
        if not self.lock_dict[msg].wait(timeout):
            assert False, "Lock ran out"
        self.lock_dict[msg].clear()
        print("Released " + msg)

    def prepare_to_wait(self, msg):
        self.lock_dict[msg].clear()
