from time import sleep

import fight_status


def do_fight(status: fight_status):
    print("Starting the fight")
    while status.status == "Not started":
        sleep(3)
    print("Doing the fight")
    while status.status != "Finished":
        sleep(3)
    print("Fight done")
