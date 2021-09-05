import time
from sniffer.sniffer import SnifferThread

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
