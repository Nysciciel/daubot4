from fight import do_fight
from locks import LockManager
from misc.pydofus.pydofus.dlm import DLM
from sniffer import sniffer
from treasureHuntObjects import *


def getMapJson(mapId):
    file = "misc/dlm/" + str(mapId) + ".dlm"
    dlm_input = open(file, "rb")
    dlm = DLM(dlm_input, "649ae451ca33ec53bbcbcc33becf15f4")
    data = dlm.read()
    dlm_input.close()
    return data


class Cell:

    def __init__(self, data, idd: int):
        self.id = idd
        self.data = data
        self.los = data['los']
        self.walkable = data['mov'] and not data['nonWalkableDuringFight']

    def __str__(self):
        return "Cell:" + str(self.id)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.data[item]


class FightMap:
    def __init__(self, mapId: int):
        self.json = getMapJson(int(mapId))
        self.ordered_cells = [Cell(self.json['cells'][i], i) for i in range(len(self.json['cells']))]
        self.cells = [[self.ordered_cells[i + j * 14] for i in range(14)] for j in range(40)]

    def neighbours_by_id(self, cellId: int):
        return ([self.cells[(cellId + cellId // 14 % 2 - 1) // 14 + j]
                 [(cellId + cellId // 14 % 2 - 1) % 14 + i]
                 for (i, j) in [(0, -1), (0, 1), (1, -1), (1, 1)]])

    def neighbours(self, cell: Cell):
        return self.neighbours_by_id(cell.id)

    def getCellFromId(self, cellId: int):
        return self.ordered_cells[cellId]

    def __str__(self):
        return ("Map:" + str(self.json['mapId']) +
                " coords:" + str(coordinatesFromMapId(self.json['mapId'])) +
                " version:" + str(self.json['mapVersion']) +
                "\n")

    def __repr__(self):
        return self.__str__()


class FightStatus:

    def __init__(self, lok, mapId):
        self.lok = lok
        self.mapId = mapId
        self.map = FightMap(mapId)

        self.status = "Not started"
        self.positionsForChallengers = []
        self.positionsForDefenders = []
        self.teamNumber = -1
        self.player_pos = -1
        self.enemy_pos = -1
        self.player_id = -1
        self.enemy_id = -1
        self.turn = -1

    def __str__(self):
        return ("Map:" + str(self.mapId) +
                " coords:" + str(coordinatesFromMapId(self.mapId)) +
                " status:" + str(self.status) +
                "\n")

    def print_map(self):
        res = ("Map:" + str(self.mapId) +
               " coords:" + str(coordinatesFromMapId(self.mapId)) +
               " status:" + str(self.status) +
               "\n")
        for j_index in range(len(self.map.cells)):
            j = self.map.cells[j_index]
            if j_index % 2 == 1:
                res += "  "
            for cell in j:
                if cell.id == self.player_pos:
                    res += " P"
                    continue
                if cell.id == self.enemy_pos:
                    res += " E"
                    continue
                if cell.walkable and cell.los:
                    res += " 0"
                if cell.walkable and not cell.los:
                    assert False
                if not cell.walkable and cell.los:
                    res += " -"
                if not cell.walkable and not cell.los:
                    res += " X"
            res += "\n"
        return ''.join([i + "\n" if i.replace(' ', '') != '' else '' for i in res.split("\n")])

    def __repr__(self):
        return self.__str__()

    def reset(self):
        self.__init__(self.lok, self.mapId)

    def handleMessage(self, msg):

        if msg is None:
            return
        if msg['__type__'] == "GameFightStartingMessage":
            self.status = "Preparation"
            self.player_id = int(msg['attackerId'])
        if msg['__type__'] == "GameFightPlacementPossiblePositionsMessage":
            self.positionsForChallengers = msg['positionsForChallengers']
            self.positionsForDefenders = msg['positionsForDefenders']
            self.teamNumber = msg['teamNumber']
        if msg['__type__'] == "GameEntitiesDispositionMessage":
            pos_dict = {entity['id']: entity['cellId'] for entity in msg['dispositions']}
            self.player_pos = pos_dict.pop(self.player_id)
            remaining_ids = list(pos_dict.keys())
            if len(remaining_ids) > 0:
                self.enemy_id = remaining_ids[0]
                self.enemy_pos = pos_dict.pop(self.enemy_id)
        if msg['__type__'] == "GameFightStartMessage":
            self.status = "Started"
        if msg['__type__'] == "GameFightTurnStartMessage":
            if msg['id'] == self.player_id:
                print("Player turn")
                self.turn = 0
        if msg['__type__'] == "GameFightTurnEndMessage":
            if msg['id'] == self.player_id:
                print("Player turn ended")
                self.turn = 1
        if msg['__type__'] == "GameFightEndMessage":
            self.status = "Finished"
        if msg['__type__'] == "GameMapMovementMessage":
            if msg['actorId'] == self.player_id:
                assert self.player_pos == msg["keyMovements"][0]
                self.player_pos = msg["keyMovements"][-1]
            if msg['actorId'] == self.enemy_id:
                assert self.enemy_pos == msg["keyMovements"][0]
                self.enemy_pos = msg["keyMovements"][-1]
        if msg['__type__'] in self.lok.lock_dict:
            self.lok.release(msg['__type__'])


if __name__ == "__main__":
    f_status = FightStatus(LockManager(), 143397)
    t_f = sniffer.SnifferThread(f_status.handleMessage)
    try:
        do_fight(f_status)
    finally:
        t_f.stop()
