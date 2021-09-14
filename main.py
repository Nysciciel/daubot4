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
logging.basicConfig(filename="messages.log", level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')

if __name__ == "__main__":

    while True:
        lok = LockManager()
        status = HuntStatus(lok)
        t = SnifferThread(status.handleMessage)
        try:
            if currentlyHuntingNoFight():
                unStuckHunt(status, lok)
            while t.is_alive():
                if not status.exists:
                    if not currentlyHunting():
                        take_hunt(status, lok)
                    elif currentlyHuntingNoFight():
                        unStuckHunt(status, lok)
                    elif locate("imgs/validate.jpg") is not None:
                        validateEtape()
                        sleep(3)
                        continue
                    if not status.exists:
                        assert False, "Can't start at fight"
                    lok.prepare_to_wait("MapComplementaryInformationsDataMessage")
                    goto_start(status, lok)
                elif status.time_to_fight():
                    print("at ", status.pos, "fight is at ", status.startPos)
                    if status.pos != status.startPos:
                        goto_start(status, lok)
                        goto(status, lok)
                    lok.prepare_to_wait('TreasureHuntFinishedMessage')
                    lok.prepare_to_wait("GameFightEndMessage")
                    print("fight")
                    pygame.mixer.music.play()
                    while (not lok.acquire('TreasureHuntFinishedMessage', nocrash=True) and
                           not lok.acquire('GameFightEndMessage', nocrash=True)):
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
                            mapId = getMaxDistCoord(status.pos.id, status.currentStep.direction)
                            print(status, mapId)
                            if status.pos == status.currentStep.startMap:
                                status.currentStep.endMap = Map(mapId)
                            else:
                                status.currentStep.endMap = status.currentStep.startMap
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
            t.stop()
            print("Sniffing stopped")
            sleep(5)
