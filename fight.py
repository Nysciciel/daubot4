from time import sleep


def do_fight(status):
    print("Starting the fight")
    while status.status == "Not started":
        sleep(3)
    print("Doing the fight")
    while status.status != "Finished":
        sleep(3)
    print("Fight done")
