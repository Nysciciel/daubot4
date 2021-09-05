from sniffer.network import launch_in_thread
import threading
import time


class SnifferThread(threading.Thread):
    def __init__(self, action):
        super().__init__()

        def not_started_yet():
            print("Can't stop sniffer: hasn't started yet")

        self.stop = not_started_yet
        self.action = action

    def run(self):
        self.stop = launch_in_thread(self.action)


if __name__ == "__main__":

    def print_msg(msg):
        print(msg.json())
    t = SnifferThread(print_msg)
    t.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        t.stop()
