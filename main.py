from locks import LockManager
from sniffer.sniffer import SnifferThread
from treasureHuntObjects import *
import logging
import os
from controls import *
import pygame
pygame.mixer.init()
pygame.mixer.music.load("alert.wav")


lok = LockManager()
status = HuntStatus(lok)

try:
    os.remove("messages.log")
except FileNotFoundError:
    pass
logging.basicConfig(filename="messages.log", level=logging.INFO, format='%(asctime)s - %(message)s')

if __name__ == "__main__":

    t = SnifferThread(status.handleMessage)
    try:

        while t.is_alive():

            if not status.exists:
                if not currentlyHunting():
                    # prendre chasse et sortir
                    assert False, "Hunt really doesnt exist"
                else:
                    unStuckHunt(status, lok)
                goto_start(status, lok)
            elif status.time_to_fight():
                pygame.mixer.music.play()
                lok.prepare_to_wait('TreasureHuntFinishedMessage')
                print("fight")
                lok.acquire('TreasureHuntFinishedMessage')
                print("fight done")
            elif status.time_to_validate():
                validate(status, lok)
            elif status.time_to_flag():
                flag(status, lok)
            elif status.is_phorreur():
                coord = status.currentStep.startMap.coord
                while True:
                    if status.pho_location is not None:
                        status.currentStep.endMap = status.pho_location
                        goto(status, lok)
                        break
                    else:
                        coord = getMinDistCoord(*coord, status.currentStep.direction)
                        status.currentStep.endMap = Map(coord=coord)
                        goto(status, lok)
                        lok.acquire("MapComplementaryInformationsDataMessage")
            elif not status.currentStep.endMap.isUnknown() and status.currentStep.endMap:
                goto(status, lok)
            else:
                pygame.mixer.music.play()
                abandon()

    finally:
        t.stop()
        print("Sniffing stopped")
