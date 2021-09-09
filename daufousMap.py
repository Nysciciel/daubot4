# -*- coding: utf-8 -*-
import requests
import json

with open('misc/json/MapPositions.Json') as f:
    mapPositions = json.load(f)
    mapIdToCoord = {int(k['id']): [k['posX'], k['posY']] for k in mapPositions}

with open('misc/json/SubAreas.Json') as f:
    subAreaToNameIdJson = json.load(f)
    subAreaToNameId = {i["id"]: i["nameId"] for i in subAreaToNameIdJson}
    subAreaToMapId = {i["id"]: i["mapIds"][0] for i in subAreaToNameIdJson}


with open('misc/json/PointOfInterest.Json') as f:
    mapPositions = json.load(f)
    PoiIdToNameId = {int(k['id']): k['nameId'] for k in mapPositions}

with open('misc/json/id_to_names.Json', encoding='utf-8') as f:
    NameIdToName = json.load(f)
    nameIdToName = NameIdToName["texts"]

with open('misc/json/translator.Json') as f:
    translator = json.load(f)

getKeyFromValue = lambda dic, value: [tupl[0] for tupl in list(dic.items()) if (tupl[1] == value)]

directions = ['top', 'bottom', 'left', 'right', 'No direction']


# returns the keys from the distionnary that give the value


def getIndices(x, y, direction, world=0):
    assert direction in directions
    # returns all the data of the list of objects present in said direction from coordinates
    site = "https://dofus-map.com/huntTool/getData.php?x=" + str(x) + "&y=" + str(y)
    site += "&direction=" + direction + "&world=" + str(world) + "&language=fr"
    r = requests.post(site)
    try:
        if not ("hints" in json.loads(r.text).keys()):
            return []
        return json.loads(r.text)["hints"]
    except:
        return []


def getIndiceAnswers(x, y, direction, world=0):
    assert direction in directions
    # returns names of list of objects present in said direction from coordinates
    hints = getIndices(x, y, direction, world)
    if not hints:
        return []
    res = []
    for dic in hints:
        res.append(translator[str(dic['n'])])
    return res


def getIndiceDist(indice, x, y, direction, world=0):
    assert direction in directions
    # return distance from said object
    hints = getIndices(x, y, direction, world)
    if not hints:
        return
    indexList = getKeyFromValue(translator, indice)
    for dic in hints:
        for index in indexList:
            if str(dic['n']) == index:
                return dic['d']
    return None


def getIndicesFromMapId(idd, direction, world=0):
    assert direction in directions
    # returns all the data of the list of objects present in said direction from coordinates
    site = "https://dofus-map.com/huntTool/getData.php?mapId=" + str(idd)
    site += "&direction=" + str(direction) + "&world=" + str(world) + "&language=fr"
    r = requests.post(site)
    try:
        if not ("hints" in json.loads(r.text).keys()):
            return []
        return json.loads(r.text)["hints"]
    except json.decoder.JSONDecodeError:
        return None


def getIndiceDistFromMapId(indice, idd, direction, world=0):
    assert direction in directions
    hints = getIndicesFromMapId(idd, direction, world)
    if not hints:
        return
    indexList = getKeyFromValue(translator, indice)
    for dic in hints:
        for index in indexList:
            if str(dic['n']) == index:
                return dic['d']


def getIndiceCoord(indice, x, y, direction, world=0):
    assert direction in directions
    # return coordinates of said object
    hints = getIndices(x, y, direction, world)
    if not hints:
        return
    indexList = getKeyFromValue(translator, indice)
    for dic in hints:
        for index in indexList:
            if str(dic['n']) == index:
                return dic['x'], dic['y']
    return None


def getMinDistCoord(x, y, direction, world=0):
    assert direction in directions
    hints = getIndices(x, y, direction, world)
    dx = int(direction == "right") - int(direction == "left")
    dy = int(direction == "bottom") - int(direction == "top")
    if not hints:
        return x + dx, y + dy
    for dic in hints:
        if int(dic['d']) == 1:
            return dic['x'], dic['y']
    return x + dx, y + dy


def getIndiceCoordFromMapId(indice, idd, direction, world=0):
    # return coordinates of said object
    assert direction in directions
    hints = getIndicesFromMapId(idd, direction, world)
    if not hints:
        return
    indexList = getKeyFromValue(translator, indice)
    for dic in hints:
        for index in indexList:
            if str(dic['n']) == index:
                return dic['x'], dic['y']
    return
