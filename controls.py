import pyperclip
import win32com.client
import win32gui
import win32api
import win32con
from time import sleep
import cv2
import numpy as np
import time
import win32ui
from PIL import Image
from ctypes import windll
import pyautogui


def getDofusWindow():
    for win in enumerateWindows():
        name = win[0]
        if "Dofus" in name:
            return win[1]
    return None


def waitForDofus():
    dofWin = getDofusWindow()
    while not win32gui.GetForegroundWindow() == dofWin:
        if not ((win32gui.GetWindowText(dofWin), dofWin) in enumerateWindows()):
            raise NameError("Allume Dofus C.O.N.N.A.R.D")


def paste():
    waitForDofus()
    pyautogui.hotkey("ctrl", "v")


def press(key):
    waitForDofus()
    pyautogui.press(key)


def click(x, y):
    waitForDofus()
    pyautogui.click(x, y)


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
    print("from " + str(status.pos) + " to " + str(status.currentStep.endMap))
    press('space')
    pyperclip.copy(status.currentStep.endMap.travelStr())
    paste()
    time.sleep(0.5)
    press('enter')
    time.sleep(0.5)
    press('enter')
    time.sleep(0.5)
    press('enter')
    time.sleep(0.5)
    press('enter')
    time.sleep(0.5)
    press('escape')
    lok.acquire(blocking=True, timeout=3)
    while status.pos != status.currentStep.endMap:
        lok.acquire(blocking=True, timeout=3)
        print("waiting to be at" + str(status.currentStep.endMap) + " currently at " + str(status.pos))


def locate(img, confidence=0.95):
    res = cv2.matchTemplate(screenshot(), cv2.imread(img), cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    x, y = min_loc
    if min_val < 1 - confidence:
        return x, y
    return None


def getFlag():
    return locate("imgs/flag.jpg")


def currentlyHunting():
    return getFlag() is not None


def unStuckHunt(status, lok):
    while not status.exists:
        x, y = getFlag()
        click(x, y)
        time.sleep(3)
        click(x, y)
        if not status.exists:
            print('Move manually to another map')
            lok.acquire(blocking=True, timeout=-1)


def validateIndice():
    x, y = getFlag()
    click(x, y)


def flag(status, lok):
    print('flag')
    index = len(status.flags)
    validateIndice()
    lok.acquire(blocking=True, timeout=3)
    while len(status.flags) == index:
        lok.acquire(blocking=True, timeout=3)
        print("waiting flag validation")


def validateEtape():
    left, top = locate("imgs/validate.jpg")
    click(left, top)


def validate(status, lok):
    print('validate')
    currentCheckPoint = status.currentCheckPoint
    retries = status.retries
    validateEtape()
    lok.acquire(blocking=True, timeout=3)
    while status.currentCheckPoint == currentCheckPoint:
        if status.retries != retries:
            assert False, "Dofus Map Error"
        lok.acquire(blocking=True, timeout=3)
        print("waiting flag next checkpoint")
