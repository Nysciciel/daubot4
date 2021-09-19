from misc.pydofus.pydofus.dlm import DLM
from treasureHuntObjects import *

msg_list = ["GameFightStartingMessage",
            'GameFightPlacementPossiblePositionsMessage',
            ]


def getMapJson(mapId):
    file = "misc/dlm/" + str(mapId) + ".dlm"
    dlm_input = open(file, "rb")
    dlm = DLM(dlm_input, "649ae451ca33ec53bbcbcc33becf15f4")
    data = dlm.read()
    dlm_input.close()
    return data


class FightMap:
    def __init__(self, mapId):
        self.json = getMapJson(mapId)
        self.cells = [[self.json['cells'][i + j * 14] for i in range(14)] for j in range(40)]

    def __str__(self):
        res = ("Map:" + str(self.json['mapId']) +
               " coords:" + str(coordinatesFromMapId(self.json['mapId'])) +
               " version:" + str(self.json['mapVersion']) +
               "\n")
        for j_index in range(len(self.cells)):
            j = self.cells[j_index]
            if j_index % 2 == 1:
                res += "  "
            for i in j:
                b0 = i['mov'] and not i['nonWalkableDuringFight']
                b1 = i['los']
                if b0 and b1:
                    res += " ⬜ "
                if b0 and not b1:
                    assert False
                if not b0 and b1:
                    res += "   "
                if not b0 and not b1:
                    res += " ■ "
            res += "\n"

        return ''.join([i + "\n" if i.replace(' ', '') != '' else '' for i in res.split("\n")])

    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":
    print(FightMap(99090957))


class cell:
    def __init__(self, cellId, fight_map):
        pass


class FightStatus:

    def __init__(self, lok):
        self.lok = lok
        self.started = False

    def __str__(self):
        if self.started:
            return "Started"
        return "Not started yet"

    def __repr__(self):
        return self.__str__()

    def reset(self):
        self.__init__(self.lok)

    def handleMessage(self, msg):

        if msg is None:
            return
        if msg['__type__'] == "GameFightStartingMessage":
            self.started = True
        if msg['__type__'] in self.lok.lock_dict:
            self.lok.release(msg['__type__'])
