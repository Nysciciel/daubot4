from sniffer.network import launch_in_thread


class SnifferThread:
    def __init__(self, action):
        self.stop, self.thread = launch_in_thread(action)

    def is_alive(self):
        return self.thread.is_alive()