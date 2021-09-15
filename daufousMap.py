# -*- coding: utf-8 -*-
import requests
import json

with open('misc/json/MapPositions.Json') as f:
    mapPositions = json.load(f)
    mapIdToCoord = {int(k['id']): [k['posX'], k['posY']] for k in mapPositions}

with open('misc/json/SubAreas.Json') as f:
    subAreaToNameIdJson = json.load(f)
    subAreaToNameId = {i["id"]: i["nameId"] for i in subAreaToNameIdJson}
    subAreaToMapId = {i["id"]: i["mapIds"] for i in subAreaToNameIdJson}

with open('misc/json/PointOfInterest.Json') as f:
    mapPositions = json.load(f)
    PoiIdToNameId = {int(k['id']): k['nameId'] for k in mapPositions}

with open('misc/json/i18n_fr.Json', encoding='utf-8') as f:
    NameIdToName = json.load(f)
    nameIdToName = NameIdToName["texts"]

with open('misc/json/translator.Json') as f:
    translator = json.load(f)


def getKeyFromValue(dic, value):
    return [tupl[0] for tupl in list(dic.items()) if (tupl[1] == value)]


mapIdToSubArea = {}
for areaId in subAreaToMapId:
    for mapIdd in subAreaToMapId[areaId]:
        mapIdToSubArea[mapIdd] = areaId

directions = ['top', 'bottom', 'left', 'right', 'No direction']


# returns the keys from the distionnary that give the value


def getIndices(mapId, direction, world=0):
    assert direction in directions
    # returns all the data of the list of objects present in said direction from coordinates
    site = "https://dofus-map.com/huntTool/getData.php?mapId=" + str(mapId)
    site += "&direction=" + direction + "&world=" + str(world) + "&language=fr"
    r = requests.post(site)
    try:
        if not ("hints" in json.loads(r.text).keys()):
            return []
        return json.loads(r.text)["hints"]
    except json.decoder.JSONDecodeError:
        return []


def getIndicesFromCoord(x, y, direction, world=0):
    assert direction in directions
    # returns all the data of the list of objects present in said direction from coordinates
    site = "https://dofus-map.com/huntTool/getData.php?x=" + str(x) + "&y=" + str(y)
    site += "&direction=" + direction + "&world=" + str(world) + "&language=fr"
    r = requests.post(site)
    try:
        if not ("hints" in json.loads(r.text).keys()):
            return []
        return json.loads(r.text)["hints"]
    except (NameError or json.decoder.JSONDecodeError) as e:
        print(e)
        return []


def getIndiceMapId(indice, mapId, direction, world=0):
    assert direction in directions
    # return coordinates of said object
    hints = getIndices(mapId, direction, world)
    indexList = getKeyFromValue(translator, indice)
    for dic in hints:
        for index in indexList:
            if str(dic['n']) == index:
                if 'i' in dic:
                    return dic['i']
                return getKeyFromValue(mapIdToCoord, [dic['x'], dic['y']])[0]
    hints = getIndicesFromCoord(*mapIdToCoord[mapId], direction, world)
    indexList = getKeyFromValue(translator, indice)
    for dic in hints:
        for index in indexList:
            if str(dic['n']) == index:
                if 'i' in dic:
                    return dic['i']
                return getKeyFromValue(mapIdToCoord, [dic['x'], dic['y']])[0]
    return


def getMinDistCoord(mapId, direction, world=0):
    assert direction in directions
    x, y = mapIdToCoord[mapId]
    hints = getIndices(mapId, direction, world)
    dx = int(direction == "right") - int(direction == "left")
    dy = int(direction == "bottom") - int(direction == "top")
    if not hints:
        return getKeyFromValue(mapIdToCoord, [x + dx, y + dy])[0], 1
    for dic in hints:
        if int(dic['d']) == 1:
            if 'i' in dic:
                return dic['i'], 1
            return getKeyFromValue(mapIdToCoord, [dic['x'], dic['y']])[0], 1
    return getKeyFromValue(mapIdToCoord, [x + dx, y + dy])[0], 1


def getMaxDistCoord(mapId, direction, world=0):
    assert direction in directions
    x, y = mapIdToCoord[mapId]
    hints = getIndices(mapId, direction, world)
    dx = int(direction == "right") - int(direction == "left")
    dy = int(direction == "bottom") - int(direction == "top")
    maxD = 0
    maxId = None
    if not hints:
        return getKeyFromValue(mapIdToCoord, [x + dx, y + dy])[0], 1
    for dic in hints:
        if int(dic['d']) == 10:
            if 'i' in dic:
                return dic['i'], 10
            return getKeyFromValue(mapIdToCoord, [dic['x'], dic['y']])[0], 10
        if int(dic['d']) >= maxD:
            maxD = int(dic['d'])
            if 'i' in dic:
                maxId = dic['i']
            else:
                maxId = getKeyFromValue(mapIdToCoord, [dic['x'], dic['y']])[0]
    return maxId, maxD
