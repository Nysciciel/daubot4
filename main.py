from locks import LockManager
from sniffer.sniffer import SnifferThread
from treasureHuntObjects import *
import logging
import os
from controls import *
import pygame

pygame.mixer.init()
pygame.mixer.music.load("alert.wav")
try:
    os.remove("messages.log")
except FileNotFoundError:
    pass
logging.basicConfig(filename="messages.log", level=logging.DEBUG, format='%(asctime)s - %(message)s')

if __name__ == "__main__":

    while True:

        lok = LockManager()
        status = HuntStatus(lok)
        t = SnifferThread(status.handleMessage)
        try:

            while t.is_alive():
                if not status.exists:
                    if not currentlyHunting():
                        take_hunt(lok)
                    elif currentlyHuntingNoFight():
                        unStuckHunt(status, lok)
                    if not status.exists:
                        assert False, "Can't start at fight"
                    lok.prepare_to_wait("MapComplementaryInformationsDataMessage")
                    goto_start(status, lok)
                elif status.time_to_fight():
                    lok.prepare_to_wait('TreasureHuntFinishedMessage')
                    print("fight")
                    pygame.mixer.music.play()
                    while not lok.acquire('TreasureHuntFinishedMessage', nocrash=True) and not currentlyHuntingNoFight():
                        pass
                    print("fight done")
                    sleep(3)
                    press('escape')
                elif status.time_to_validate():
                    validate(status, lok)
                elif status.time_to_flag():
                    flag(status, lok)
                elif status.is_phorreur():
                    mapId = status.currentStep.startMap.id
                    print(status.currentStep.startMap)
                    while True:
                        if status.pho_location is not None:
                            status.currentStep.endMap = status.pho_location
                            goto(status, lok)
                            break
                        else:
                            mapId = getMinDistCoord(mapId, status.currentStep.direction)
                            print(status, mapId)
                            if Map(id=mapId) in status.flags:
                                continue
                            status.currentStep.endMap = Map(id=mapId)
                            goto(status, lok)
                            lok.acquire("MapComplementaryInformationsDataMessage")
                elif status.currentStep.endMap:
                    print("BITE", status)
                    goto(status, lok)
                else:
                    abandon()
        except AssertionError as e:
            print(e)
            pygame.mixer.music.play()
            sleep(5)
            t.stop()
            print("Sniffing stopped")
