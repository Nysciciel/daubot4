import threading

from sniffer.network import launch_in_thread


class SnifferThread(threading.Thread):
    def __init__(self, action):
        super().__init__()

        def not_started_yet():
            print("Can't stop sniffer: hasn't started yet")

        self.stop = not_started_yet
        self.action = action

    def run(self):
        self.stop = launch_in_thread(self.action)