import time
import threading
from sniffer.sniffer import SnifferThread
from treasureHuntObjects import HuntStatus
import pyperclip

lok = threading.Lock()
status = HuntStatus(lok)
lok.acquire(blocking=True, timeout=-1)

if __name__ == "__main__":

    t = SnifferThread(status.handleMessage)
    try:
        while t.is_alive():
            lok.acquire(blocking=True, timeout=-1)
            pyperclip.copy(status.currentStep.endMap.travelStr())
            if status.time_to_fight():
                todo = "fight"
            elif status.time_to_validate():
                todo = "validate"
            elif status.time_to_flag():
                todo = "flag"
            elif status.is_phorreur():
                if status.pho_location is not None:
                    todo = "go to:" + str(status.pho_location)
                else:
                    todo = "search pho "+str(status.currentStep.dir_str())
            elif not status.currentStep.endMap.isUnknown() and status.currentStep.endMap:
                todo = "go to:"+str(status.currentStep.endMap)
            else:
                todo = "lost"
            print(todo)

    finally:
        t.stop()
        print("Sniffing stopped")
