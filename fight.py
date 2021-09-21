from time import sleep

import fight_status


def do_fight(status: fight_status):
    while status.status == "Not started":
        print("Starting the fight")
        sleep(0.1)
    while status.status != "Finished":
        print("Doing the fight")
        sleep(0.1)
    print("\nFight done")
