import threading
from treasureHuntObjects import msg_list


class LockManager:
    def __init__(self):
        self.lock_dict = {msg: threading.Event() for msg in msg_list}

    def release(self, msg):
        self.lock_dict[msg].set()

    def acquire(self, msg, timeout=10, nocrash=False):
        print("Acquired " + msg)
        res = self.lock_dict[msg].wait(timeout)
        if (not res) and (not nocrash):
            assert False, "Lock ran out"
        self.lock_dict[msg].clear()
        print("Released " + msg)
        return res

    def prepare_to_wait(self, msg):
        self.lock_dict[msg].clear()
