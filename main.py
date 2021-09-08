import threading
from sniffer.sniffer import SnifferThread
from treasureHuntObjects import *
from daufousMap import *
import pyperclip
import logging
import os
from controls import *
import time

lok = threading.Lock()
status = HuntStatus(lok)

os.remove("messages.log")
logging.basicConfig(filename="messages.log", level=logging.INFO, format='%(message)s')

if __name__ == "__main__":

    t = SnifferThread(print)
    while True:
        time.sleep(1)

    t = SnifferThread(status.handleMessage)
    try:
        print("Started")
        while t.is_alive():

            if not status.exists:
                print("doesnt exist")
                lok.acquire(blocking=True, timeout=1)
                if not currentlyHunting():
                    print("really doesnt exist")
                    continue
                else:
                    print("actually exist")
                    unStuckHunt(status, lok)
            elif status.time_to_fight():
                print("fight")
                lok.acquire(blocking=True, timeout=1)
                continue
            elif status.time_to_validate():
                validate(status, lok)
            elif status.time_to_flag():
                flag(status, lok)
            elif status.is_phorreur():
                coord = status.currentStep.startMap.coord
                while status.pho_location is None:
                    while not status.pho_analysed:
                        lok.acquire(blocking=True, timeout=1)
                    if status.pho_location is not None:
                        status.pho_analysed = True
                        goto(status, lok)
                        break
                    else:
                        coord = getMinDistCoord(*coord, status.currentStep.direction)
                        status.currentStep.endMap = Map(coord=coord)
                        status.pho_analysed = False
                        goto(status, lok)
            elif not status.currentStep.endMap.isUnknown() and status.currentStep.endMap:
                goto(status, lok)

    finally:
        t.stop()
        print("Sniffing stopped")
