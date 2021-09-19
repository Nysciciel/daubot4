import threading
from treasureHuntObjects import msg_list
from fight_status import msg_list as msg_list_fight


class LockManager:
    def __init__(self):
        self.lock_dict = {msg: threading.Event() for msg in msg_list + msg_list_fight}

    def release(self, msg):
        self.lock_dict[msg].set()

    def acquire(self, msg, timeout=10, nocrash=False):
        print("Acquired " + msg)
        res = self.lock_dict[msg].wait(timeout)
        if (not res) and (not nocrash):
            assert False, "Lock ran out"
        self.lock_dict[msg].clear()
        if res:
            print("Released " + msg)
        else:
            print("Released " + msg + " by timeout")
        return res

    def prepare_to_wait(self, msg):
        self.lock_dict[msg].clear()
