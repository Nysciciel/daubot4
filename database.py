import json

from daufousMap import getIndiceCoordFromMapId, getIndiceCoord
import pyperclip


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
        return "Name not found"


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

    def __eq__(self, other):
        return self.coord == other.coord

    def __bool__(self):
        return self.id is not None

    def travelStr(self):
        if self:
            return "/travel " + str(self.coord[0]) + "," + str(self.coord[1])
        return ''


class Indice:

    def __init__(self, Id=None):
        self.id = Id

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
        coord = getIndiceCoordFromMapId(indice.name, startMap.id, direction)
        if not coord:
            coord = getIndiceCoord(indice.name, *startMap.coord, direction)
        self.endMap = Map(coord=coord)

    def __bool__(self):
        return self.direction != "No direction"


class HuntStatus:

    def __init__(self):
        self.maxStep = None
        self.stepList = []
        self.nIndice = None
        self.exists = False
        self.pos = None
        self._currentStep = Step()

    def reset(self):
        self.__init__()

    @property
    def currentStep(self):
        return self._currentStep

    @currentStep.setter
    def currentStep(self, newCurrentStep):
        if not hasattr(self, "_currentStep"):
            self._currentStep = newCurrentStep
            return
        if len(self.stepList) > 0:
            assert self.stepList[-1].endMap == newCurrentStep.startMap, "Map continuity failed"
        self._currentStep = newCurrentStep
        self.stepList.append(newCurrentStep)

        pyperclip.copy((newCurrentStep.endMap or newCurrentStep.startMap).travelStr())
