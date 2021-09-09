import pyperclip
import win32gui
import cv2
import numpy as np
import win32ui
from PIL import Image
from ctypes import windll
import pyautogui
from time import sleep
from random import randint
from daufousMap import *
from treasureHuntObjects import Map

paste_pause = press_pause = click_pause = 0.7
goto_pause = 3


def getDofusWindow():
    for win in enumerateWindows():
        name = win[0]
        if "Dofus" in name:
            return win[1]
    return None


def waitForDofus():
    dofWin = getDofusWindow()
    while not win32gui.GetForegroundWindow() == dofWin:
        sleep(3)


def paste():
    waitForDofus()
    sleep(paste_pause)
    pyautogui.hotkey("ctrl", "v")
    sleep(paste_pause)


def use_skis(lok):
    waitForDofus()
    sleep(paste_pause)
    lok.prepare_to_wait('MapInformationsRequestMessage')
    pyautogui.hotkey("ctrl", "-")
    lok.acquire('MapInformationsRequestMessage')
    sleep(goto_pause)


def press(key):
    waitForDofus()
    pyautogui.press(key)
    sleep(press_pause)


def click(x, y):
    waitForDofus()
    dx, dy, _, _ = win32gui.GetWindowRect(getDofusWindow())
    pyautogui.click(x + dx, y + dy)
    sleep(click_pause)


def mouse_random_move():
    pyautogui.move(randint(-10, 10), randint(-10, 10))


def screenshot():
    hwnd = getDofusWindow()
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer('RGB',
                          (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                          bmpstr, 'raw', 'BGRX', 0, 1)
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if result == 1:
        return np.array(im)[:, :, ::-1]
    else:
        print("PrintWindow failed")


def enumerateWindows():
    res = []

    def winEnumHandler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if win32gui.GetWindowText(hwnd):
                res.append((win32gui.GetWindowText(hwnd), hwnd))

    win32gui.EnumWindows(winEnumHandler, None)
    return res


def goto(status, lok):
    if status.pos == status.currentStep.endMap:
        return
    print("from " + str(status.pos) + " to " + str(status.currentStep.endMap))
    press('space')
    pyperclip.copy(status.currentStep.endMap.travelStr())
    print("COPIED ", status.currentStep.endMap.travelStr())
    paste()
    press('enter')
    lok.prepare_to_wait("MapComplementaryInformationsDataMessage")
    press('enter')
    press('escape')
    lok.prepare_to_wait("MapComplementaryInformationsDataMessage")
    while status.pos != status.currentStep.endMap:
        print("waiting to be at" + str(status.currentStep.endMap) + " currently at " + str(status.pos))
        sleep(1)
    print("arrived at" + str(status.pos))
    sleep(goto_pause)


def locate(img, confidence=0.95):
    im = cv2.imread(img)
    res = cv2.matchTemplate(screenshot(), im, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    x, y = min_loc
    if min_val < 1 - confidence:
        return x + im.shape[0] // 2, y + im.shape[1] // 2
    return None


def getFlag():
    return locate("imgs/flag.jpg")


def currentlyHunting():
    return locate("imgs/abandon.jpg") is not None


def currentlyHuntingNoFight():
    return locate("imgs/flag.jpg") is not None


def unStuckHunt(status, lok):
    print('Trying to detect hunt')
    enter_haven(lok)
    while not status.exists:
        x, y = getFlag()
        lok.prepare_to_wait('TreasureHuntMessage')
        click(x, y)
        lok.prepare_to_wait("TreasureHuntFlagRemoveRequestMessage")
        lok.prepare_to_wait("TreasureHuntMessage")
        click(x, y)
        lok.acquire('TreasureHuntFlagRemoveRequestMessage')
        lok.acquire("TreasureHuntMessage")
    press('h')
    sleep(goto_pause)


def validateIndice():
    while getFlag() is None:
        mouse_random_move()
    x, y = getFlag()
    click(x, y)


def flag(status, lok):
    print('flag')
    flags = len(status.flags)
    lok.prepare_to_wait("TreasureHuntFlagRequestMessage")
    lok.prepare_to_wait("TreasureHuntMessage")
    validateIndice()
    lok.acquire('TreasureHuntFlagRequestMessage')
    lok.acquire("TreasureHuntMessage")
    if flags == len(status.flags):
        print("Can't place here twice, map messed up")


def validateEtape():
    left, top = locate("imgs/validate.jpg")
    click(left, top)


def validate(status, lok):
    print('validate')
    retries = status.retries
    lok.prepare_to_wait("TreasureHuntMessage")
    validateEtape()
    lok.acquire("TreasureHuntMessage")
    if status.retries != retries:
        assert False, "Dofus Map Error"


def abandon():
    print("abandon")
    assert False
    sleep(60 * 10)
    click(*locate("imgs/abandon.jpg"))
    press("enter")


def goto_start(status, lok):
    if status.pos == status.currentStep.startMap:
        return
    pos = status.pos
    print("at ", str(status.pos), " need to be at ", str(status.currentStep.startMap))
    x, y = status.currentStep.startMap.coord
    if x <= -42 and y <= -20:
        frigost_area_name = nameIdToName[str(subAreaToNameId[mapIdToSubArea[status.currentStep.startMap.id]])]
    else:
        frigost_area_name = None
    enter_haven(lok)
    click_zap(lok)
    min_dist = float('inf')
    area_id = None
    for dest in status.zaap_dest:
        dist = Map(id=dest['mapId']) - status.currentStep.startMap
        if dist < min_dist:
            min_dist = dist
            area_id = dest['subAreaId']
    if pos - status.currentStep.startMap <= min_dist:
        lok.prepare_to_wait('LeaveDialogRequestMessage')
        press('escape')
        lok.acquire('LeaveDialogRequestMessage')
        press('h')
        sleep(goto_pause)
        return
    dest_str = nameIdToName[str(subAreaToNameId[area_id])]
    if dest_str == "Centre-ville":
        if Map(id=subAreaToMapId[area_id][0]).coord[1] < 0:
            dest_str = "bonta"
        else:
            dest_str = "brakmar"
    if frigost_area_name in ["Village enseveli", "Forêt pétrifiée"]:
        dest_str = "Village enseveli"
    elif frigost_area_name is not None:
        dest_str = "bourgade"
    print("zaap to ", dest_str)
    pyperclip.copy(dest_str)
    paste()
    lok.prepare_to_wait('CurrentMapMessage')
    press('enter')
    lok.acquire('CurrentMapMessage')
    sleep(goto_pause)
    if x <= -42 and y <= -20:
        frigost_area_name = nameIdToName[str(subAreaToNameId[mapIdToSubArea[status.currentStep.startMap.id]])]
        if frigost_area_name == "Berceau d'Alma":
            use_skis(lok)
            lok.prepare_to_wait("NpcDialogQuestionMessage")
            click(1026, 647)
            lok.acquire("NpcDialogQuestionMessage")

            lok.prepare_to_wait("CurrentMapMessage")
            click(1003, 671)
            lok.acquire("CurrentMapMessage")
            sleep(goto_pause)
            return
        elif frigost_area_name == "Larmes d'Ouronigride":
            use_skis(lok)
            lok.prepare_to_wait("NpcDialogQuestionMessage")
            click(1026, 647)
            lok.acquire("NpcDialogQuestionMessage")

            lok.prepare_to_wait("CurrentMapMessage")
            click(1064, 692)
            lok.acquire("CurrentMapMessage")
            sleep(goto_pause)
            return
        elif frigost_area_name == 'Crevasse Perge':
            use_skis(lok)
            lok.prepare_to_wait("NpcDialogQuestionMessage")
            click(1026, 647)
            lok.acquire("NpcDialogQuestionMessage")

            lok.prepare_to_wait("CurrentMapMessage")
            click(1037, 717)
            lok.acquire("CurrentMapMessage")
            sleep(goto_pause)


def enter_haven(lok):
    lok.prepare_to_wait("EnterHavenBagRequestMessage")
    lok.prepare_to_wait("CurrentMapMessage")
    press('h')
    lok.acquire("EnterHavenBagRequestMessage")
    lok.acquire("CurrentMapMessage")
    sleep(goto_pause)


def click_zap(lok):
    lok.prepare_to_wait("ZaapDestinationsMessage")
    click(573, 371)
    lok.acquire("ZaapDestinationsMessage")
