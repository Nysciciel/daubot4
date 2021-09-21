from time import sleep


def do_fight(status):
    while status.status == "Not started":
        print("Starting the fight")
        sleep(2)
    while status.status != "Finished":
        print(status)
        sleep(3)
    print("\nFight done")
