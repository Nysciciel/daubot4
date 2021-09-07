import json
from datetime import datetime
from daufousMap import getIndiceCoordFromMapId, getIndiceCoord
import logging
import time


def release(lokkk):
    try:
        lokkk.release()
    except RuntimeError:
        pass


def init_mapToCoordDict():
    with open('misc/json/MapPositions.Json') as f:
        mapPositions = json.load(f)

    dictIdToCoord = {}
    for k in mapPositions:
        dictIdToCoord[int(k['id'])] = [k['posX'], k['posY']]

    return dictIdToCoord


def init_PoiIdToNameIdDict():
    with open('misc/json/PointOfInterest.Json') as f:
        mapPositions = json.load(f)

    dictPoiIdToNameId = {}
    for k in mapPositions:
        dictPoiIdToNameId[int(k['id'])] = k['nameId']

    return dictPoiIdToNameId


def init_NameIdToNameDict():
    with open('misc/json/id_to_names.Json', encoding='utf-8') as f:
        NameIdToName = json.load(f)

    return NameIdToName["texts"]


mapIdToCoord = init_mapToCoordDict()
PoiIdToNameId = init_PoiIdToNameIdDict()
nameIdToName = init_NameIdToNameDict()


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
            (lambda dic, value: [item[0] for item in list(dic.items()) if (item[1] == value)]) \
                (mapIdToCoord, list(coord))[0]
    except (TypeError, IndexError):
        return None


class Map:

    def __init__(self, **kwargs):
        if "coord" in kwargs:
            self.coord = kwargs["coord"]
        elif "id" in kwargs:
            self.id = kwargs["id"]
        else:
            self._coord = (None, None)
            self._id = None

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
        return self.id is not None and not self.isUnknown()

    def travelStr(self):
        if self:
            return "/travel " + str(self.coord[0]) + "," + str(self.coord[1])
        return ''

    def isUnknown(self):
        return False

    def copy(self):
        return Map(id=self.id)


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
            coord = getIndiceCoordFromMapId(indice.name, startMap.id, direction)
            if not coord:
                if startMap.coord is not None:
                    coord = getIndiceCoord(indice.name, *startMap.coord, direction)
                else:
                    self.endMap = UnknowMap()
                    return
            self.endMap = Map(coord=coord)

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
        self.pho_analysed = True

    def __str__(self):
        return ('Current Position:' + str(self.pos) + "\n" +
                "Checkpoint:" + str(self.currentCheckPoint) + "/" + str(self.maxCheckPoint) + "\n" +
                'Start map:' + str(self.startPos) + "\n" +
                ''.join([str(step) + "\n" for step in self.stepList]))

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
        current_time = datetime.now().strftime("%H:%M:%S")
        logging.info(current_time + str(msg))
        if msg['__type__'] == 'SetCharacterRestrictionsMessage':
            release(self.lok)
        if msg['__type__'] == "CurrentMapMessage":
            self.pos = Map(id=msg['mapId'])
        if msg['__type__'] == "MapComplementaryInformationsDataMessage":
            if not self.currentStep.indice.isPhorreur:
                return
            for actor in msg['actors']:
                if "npcId" in actor:
                    if (actor["npcId"] == self.currentStep.indice.id) and (
                            actor["__type__"] == 'GameRolePlayTreasureHintInformations'):
                        self.pho_location = self.pos.copy()
                        release(self.lok)
            self.pho_analysed = True
        if msg['__type__'] == 'TreasureHuntFinishedMessage':
            self.reset()
        if msg['__type__'] == "TreasureHuntMessage":
            self.pho_location = None
            self.exists = True
            self.nIndice = msg['totalStepCount']
            self.maxCheckPoint = msg['checkPointTotal']
            self.currentCheckPoint = msg['checkPointCurrent'] + 1
            if self.maxCheckPoint == self.currentCheckPoint:
                self.stepList = []
                self.flags = []
                self.nIndice = None
            else:
                self.startPos = Map(id=msg['startMapId'])
                self.flags = [Map(id=flag_json['mapId']) for flag_json in msg['flags']]
                if self.nIndice != 0:
                    self.stepList = []
                    current_map = self.startPos
                    for index in range(self.nIndice):
                        if index >= len(msg['knownStepsList']):
                            self.stepList.append(Step(startMap=current_map))
                            current_map = UnknowMap()
                            continue
                        step_json = msg['knownStepsList'][index]
                        s = Step().init_from_json(step_json, current_map)
                        self.stepList.append(s)
                        if s.indice.isPhorreur() and index < len(self.flags):
                            current_map = self.flags[index]
                        else:
                            current_map = s.endMap

            print(self)
            release(self.lok)
