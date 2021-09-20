from daufousMap import *
import logging

from locks import msg_list


def PoiIdToName(idd):
    try:
        return nameIdToName[str(PoiIdToNameId[idd])]
    except KeyError:
        return "?"


def coordinatesFromMapId(idd):
    try:
        return tuple(mapIdToCoord[idd])
    except KeyError:
        return None, None


def mapIdFromCoord(coord):
    try:
        return \
            (lambda dicc, val: [item[0] for item in list(dicc.items()) if (item[1] == val)]) \
                (mapIdToCoord, list(coord))[0]
    except (TypeError, IndexError):
        return None


class Map:

    # def __init__(self, **kwargs):
    #     if "id" in kwargs:
    #         self.id = kwargs["id"]
    #     if "coord" in kwargs:
    #         self.coord = kwargs["coord"]
    #     else:
    #         self._coord = (None, None)
    #         self._id = None

    def __init__(self, idd=None):
        self.id = idd

    @property
    def coord(self):
        return self._coord

    @coord.setter
    def coord(self, coord):
        self._coord = coord
        self._id = mapIdFromCoord(coord)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, idd):
        self._id = idd
        self._coord = coordinatesFromMapId(idd)

    def __str__(self):
        return str(self.coord)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not self or not other:
            return False
        return self.coord == other.coord

    def __bool__(self):
        return not self.isUnknown()

    def travelStr(self):
        if self:
            return "/travel " + str(self.coord[0]) + "," + str(self.coord[1])
        return ''

    def isUnknown(self):
        return self.coord == (None, None) or self.id is None

    def copy(self):
        return Map(self.id)

    def __sub__(self, other):
        if self.coord is None or other.id is None:
            return float('inf')
        return abs(self.coord[0] - other.coord[0]) + abs(self.coord[1] - other.coord[1])


class UnknowMap(Map):
    def __str__(self):
        return '(?,?)'

    def __init__(self):
        super().__init__()

    def isUnknown(self):
        return True


class Indice:

    def __init__(self, Id=None):
        self.id = Id

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, idd):
        self._id = idd
        self.name = PoiIdToName(idd)

    def isPhorreur(self):
        return False


class Phorreur(Indice):

    def __init__(self, Id=None):
        super(Phorreur, self).__init__(Id)
        self.name = "Phorreur"

    def isPhorreur(self):
        return True


class Step:

    def __init__(self, direction="No direction", startMap=Map(), indice=Indice()):
        self.direction = direction
        self.startMap = startMap
        self.indice = indice
        if self.startMap.isUnknown() or indice.isPhorreur():
            self.endMap = UnknowMap()
        else:
            mapId = getIndiceMapId(indice.name, startMap.id, direction)
            if not mapId:
                if startMap.coord is not None:
                    mapId = getIndiceMapId(indice.name, startMap.id, direction)
                    if mapId is None:
                        self.endMap = UnknowMap()
                        return
                else:
                    self.endMap = UnknowMap()
                    return
            self.endMap = Map(mapId)

    def init_from_json(self, indice_json, mapp):
        direction = {0: 'right', 6: 'top', 4: 'left', 2: 'bottom'}[indice_json['direction']]
        if indice_json['__type__'] == 'TreasureHuntStepFollowDirectionToHint':
            indice = Phorreur(indice_json['npcId'])
        else:
            indice = Indice(indice_json['poiLabelId'])

        self.__init__(direction, mapp, indice)
        return self

    def __bool__(self):
        return self.direction != "No direction"

    def dir_str(self):
        return {"left": "←", "right": "→", "top": "↑", "bottom": "↓", "No direction": "?"}[self.direction]

    def __str__(self):
        return str(self.startMap) + ' ' + self.dir_str() + ' ' + str(self.indice)

    def __repr__(self):
        return self.__str__()


class HuntStatus:

    def __init__(self, lok):
        self.lok = lok
        self.maxCheckPoint = None
        self.currentCheckPoint = None
        self.stepList = []
        self.flags = []
        self.nIndice = None
        self.exists = False
        self.pos = None
        self.startPos = None
        self.pho_location = None
        self.retries = None
        self.normalHunt = True
        self.zaap_dest = None

    def __str__(self):
        return ('Current Position:' + str(self.pos) + "\n" +
                "Checkpoint:" + str(self.currentCheckPoint) + "/" + str(self.maxCheckPoint) + "\n" +
                'Start map:' + str(self.startPos) + "\n" +
                'Indices number:' + str(self.nIndice) + "\n" +
                ''.join([str(step) + "\n" for step in self.stepList])) if self.exists else ""

    def __repr__(self):
        return self.__str__()

    def reset(self):
        self.__init__(self.lok)

    @property
    def currentStep(self):
        try:
            return self.stepList[len(self.flags)]
        except IndexError:
            return Step()

    def time_to_fight(self):
        return self.maxCheckPoint == self.currentCheckPoint and self.exists

    def time_to_validate(self):
        return len(self.flags) == self.nIndice

    def time_to_flag(self):
        if self.currentStep.indice.isPhorreur():
            return self.pos == self.pho_location if self.pos else False
        return self.pos == self.currentStep.endMap

    def is_phorreur(self):
        return self.currentStep.indice.isPhorreur()

    def handleMessage(self, msg):

        if msg is None:
            return
        if msg['__type__'] in msg_list:
            logging.info(str(msg))
        else:
            logging.debug(str(msg))
        if msg['__type__'] == "CurrentMapMessage":
            newMap = Map(msg['mapId'])
            if not newMap.isUnknown():
                self.pos = newMap
        if msg['__type__'] == "ChangeMapMessage":
            newMap = Map(msg['mapId'])
            if not newMap.isUnknown():
                self.pos = newMap
        if msg['__type__'] == "MapInformationsRequestMessage":
            newMap = Map(msg['mapId'])
            if not newMap.isUnknown():
                self.pos = newMap
        if msg['__type__'] == "MapComplementaryInformationsDataMessage":
            newMap = Map(msg['mapId'])
            if not newMap.isUnknown():
                self.pos = newMap
            for actor in msg['actors']:
                if "npcId" in actor:
                    if (actor["npcId"] == self.currentStep.indice.id) and (
                            actor["__type__"] == 'GameRolePlayTreasureHintInformations'):
                        self.pho_location = self.pos.copy()
                        print("pho found at " + str(self.pho_location))
        if msg['__type__'] == 'TreasureHuntFinishedMessage':
            self.reset()
        if msg['__type__'] == 'ZaapDestinationsMessage':
            self.zaap_dest = msg['destinations']
        if msg['__type__'] == "TreasureHuntMessage":
            self.pho_location = None
            self.exists = True
            self.nIndice = msg['totalStepCount']
            self.maxCheckPoint = msg['checkPointTotal']
            self.currentCheckPoint = msg['checkPointCurrent'] + 1
            self.retries = msg['availableRetryCount']
            self.normalHunt = msg['questType'] == 0
            self.startPos = Map(msg['startMapId'])
            if self.maxCheckPoint == self.currentCheckPoint:
                self.stepList = [Step(startMap=self.startPos)]
                self.currentStep.endMap = self.startPos
                self.flags = []
                self.nIndice = None
            else:
                self.flags = [Map(flag_json['mapId']) for flag_json in msg['flags']]
                if self.nIndice != 0:
                    self.stepList = []
                    current_map = self.startPos
                    for index in range(self.nIndice):
                        if index >= len(msg['knownStepsList']):
                            self.stepList.append(Step(startMap=current_map))
                            current_map = UnknowMap()
                        else:
                            step_json = msg['knownStepsList'][index]
                            s = Step().init_from_json(step_json, current_map)
                            if (s.indice.isPhorreur() or s.endMap.isUnknown()) and index < len(self.flags):
                                current_map = self.flags[index]
                            else:
                                current_map = s.endMap
                            self.stepList.append(s)
            print(self)
        if msg['__type__'] in self.lok.lock_dict:
            self.lok.release(msg['__type__'])
