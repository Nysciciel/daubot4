import threading
from treasureHuntObjects import msg_list


class LockManager:
    def __init__(self):
        self.lock_dict = {msg: threading.Event() for msg in msg_list}

    def release(self, msg):
        self.lock_dict[msg].set()

    def acquire(self, msg, timeout=None):
        print("Acquired " + msg)
        ret = self.lock_dict[msg].wait(timeout)
        self.lock_dict[msg].clear()
        print("Released " + msg)
        return ret

    def prepare_to_wait(self, msg):
        self.lock_dict[msg].clear()
