def do_fight(status):
    status.lok.prepare_to_wait("GameFightStartingMessage")
    status.lok.prepare_to_wait("MapInformationsRequestMessage")
    #Start
    status.lok.acquire('GameFightStartingMessage')
    #fight
    status.lok.acquire('MapInformationsRequestMessage')
