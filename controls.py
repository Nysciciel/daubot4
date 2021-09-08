import pyperclip
import win32gui
import cv2
import numpy as np
import win32ui
from PIL import Image
from ctypes import windll
import pyautogui
from time import sleep

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
    pyautogui.hotkey("ctrl", "v")
    sleep(paste_pause)


def press(key):
    waitForDofus()
    pyautogui.press(key)
    sleep(press_pause)


def click(x, y):
    waitForDofus()
    dx, dy, _, _ = win32gui.GetWindowRect(getDofusWindow())
    pyautogui.click(x + dx, y + dy)
    sleep(click_pause)


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
    paste()
    press('enter')
    lok.prepare_to_wait("MapComplementaryInformationsDataMessage")
    press('enter')
    press('escape')
    while True:
        while status.pos != status.currentStep.endMap:
            lok.prepare_to_wait("CurrentMapMessage")
            lok.prepare_to_wait("SetCharacterRestrictionsMessage")
            print("waiting to be at" + str(status.currentStep.endMap) + " currently at " + str(status.pos))
            lok.prepare_to_wait("MapComplementaryInformationsDataMessage")
            lok.acquire("CurrentMapMessage")
            lok.acquire("SetCharacterRestrictionsMessage")
        print("arrived at" + str(status.pos))
        lok.prepare_to_wait("GameMapMovementConfirmMessage")
        if not lok.acquire("GameMapMovementConfirmMessage", 0):
            break
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
    return getFlag() is not None


def unStuckHunt(status, lok):
    print('Trying to detect hunt')
    while not status.exists:
        x, y = getFlag()
        lok.prepare_to_wait('TreasureHuntMessage')
        click(x, y)
        if not lok.acquire('TreasureHuntMessage', 2):
            lok.prepare_to_wait("CurrentMapMessage")
            lok.prepare_to_wait("SetCharacterRestrictionsMessage")
            print('Move manually to another map')
            lok.acquire("CurrentMapMessage")
            lok.acquire("SetCharacterRestrictionsMessage")
            sleep(goto_pause)
        else:
            lok.prepare_to_wait("TreasureHuntFlagRemoveRequestMessage")
            lok.prepare_to_wait("TreasureHuntMessage")
            click(x, y)
            lok.acquire('TreasureHuntFlagRemoveRequestMessage')
            lok.acquire("TreasureHuntMessage")


def validateIndice():
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
    sleep(60 * 10)
    click(*locate("imgs/abandon.jpg"))
    press("enter")
