import sys
from locks import LockManager
from treasureHuntObjects import *
from fight_status import *
import logging
import os
import sniffer.sniffer
from fight import *
from time import sleep

if __name__ == "__main__":
    try:
        os.remove("messages.log")
    except (FileNotFoundError, PermissionError):
        pass
    logging.basicConfig(filename="messages.log", level=logging.INFO,
                        format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
    lok = LockManager()
    status = HuntStatus(lok)
    t = sniffer.sniffer.SnifferThread(status.handleMessage)
    while t.is_alive():
        if status.exists and status.time_to_fight():
            t.stop()
            f_status = FightStatus(lok, status.pos.id)
            t_f = sniffer.sniffer.SnifferThread(f_status.handleMessage)
            try:
                do_fight(f_status)
            finally:
                t_f.stop()
                status.reset()
                t = sniffer.sniffer.SnifferThread(status.handleMessage)
        if status.currentStep.endMap == status.pos:
            print("Arrived")
        sleep(0.1)
