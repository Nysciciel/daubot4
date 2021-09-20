import sys
from locks import LockManager
from treasureHuntObjects import *
from fight_status import *
import logging
import os
from controls import *
import pygame
import sniffer.sniffer
from fight import *


def restart_program():
    os.execv(sys.executable, ['python'] + sys.argv)


if __name__ == "__main__":
    pygame.mixer.init()
    pygame.mixer.music.load("alert.mp3")
    try:
        os.remove("messages.log")
    except (FileNotFoundError, PermissionError):
        pass
    logging.basicConfig(filename="messages.log", level=logging.INFO,
                        format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
    lok = LockManager()
    status = HuntStatus(lok)
    t = sniffer.sniffer.SnifferThread(status.handleMessage)
    pho_started = False
    pho_distance = 0
    try:
        if currentlyHuntingNoFight():
            unStuckHunt(status, lok)
        while t.is_alive():
            sleep(1)
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
            elif status.time_to_fight():
                if not status.pos:
                    unStuckHunt(status, lok)
                print("at ", status.pos, "fight is at ", status.startPos)
                if status.pos != status.startPos:
                    goto_start(status, lok)
                    goto(status, lok)
                lok.prepare_to_wait("GameFightEndMessage")
                print("fight")
                pygame.mixer.music.play()
                status_fight = FightStatus(lok, status.pos.id)
                t.stop()
                t_f = sniffer.sniffer.SnifferThread(status_fight.handleMessage)
                try:
                    do_fight(status_fight)
                finally:
                    t_f.stop()
                    t = sniffer.sniffer.SnifferThread(status.handleMessage)
                    sleep(3)
                    press('escape')
                    status.reset()
            elif status.time_to_validate():
                validate(status, lok)
            elif status.time_to_flag():
                flag(status, lok)
            elif status.is_phorreur():
                if status.currentCheckPoint == 1 and len(status.flags) == 0:
                    goto_start(status, lok)
                mapId = status.currentStep.startMap.id
                print(status.currentStep.startMap)
                while True:
                    if status.pho_location is not None:
                        status.currentStep.endMap = status.pho_location
                        goto(status, lok)
                        pho_started = False
                        pho_distance = 0
                        break
                    else:
                        if not pho_started:
                            if status.pos != status.currentStep.startMap:
                                status.currentStep.endMap = status.currentStep.startMap
                            else:
                                idd, dist = getMinDistCoord(status.pos.id, status.currentStep.direction)
                                status.currentStep.endMap = Map(idd)
                                pho_started = True
                                pho_distance += dist
                        else:
                            print("Searching pho, did ", pho_distance, " maps")
                            if pho_distance > 10:
                                pho_distance = 0
                                status.currentStep.endMap = status.currentStep.startMap
                                goto(status, lok)
                            idd, dist = getMinDistCoord(status.pos.id, status.currentStep.direction)
                            mapp = Map(idd)
                            distt = dist
                            while mapp in status.flags:
                                idd, distt = getMinDistCoord(mapp.id, status.currentStep.direction)
                                distt += dist
                                mapp = Map(idd)
                            status.currentStep.endMap = mapp
                            pho_distance += distt
                        print(status, mapId)
                        goto(status, lok)
                        lok.acquire("MapComplementaryInformationsDataMessage")
            elif status.currentStep.endMap:
                print("BITE", status)
                if status.currentCheckPoint == 1 and len(status.flags) == 0:
                    goto_start(status, lok)
                    goto(status, lok)
                else:
                    goto(status, lok)
                pho_started = False
            else:
                abandon()
    except Exception as e:
        print(e)
        pygame.mixer.music.play()
    finally:
        t.stop()
        print("Sniffing stopped")
        sleep(5)
        restart_program()
