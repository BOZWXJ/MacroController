#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import enum
import gpiozero
import os
import sys
import time

uOut = gpiozero.LED(14)
dOut = gpiozero.LED(15)
rOut = gpiozero.LED(17)
lOut = gpiozero.LED(18)
shareOut = gpiozero.LED(27)
psOut = gpiozero.LED(22)
optOut = gpiozero.LED(23)
sOut = gpiozero.LED(10)
tOut = gpiozero.LED(9)
r1Out = gpiozero.LED(25)
l1Out = gpiozero.LED(11)
xOut = gpiozero.LED(8)
oOut = gpiozero.LED(12)
r2Out = gpiozero.LED(13)
l2Out = gpiozero.LED(19)
sIn = gpiozero.Button(21)
tIn = gpiozero.Button(20)
xIn = gpiozero.Button(26)
oIn = gpiozero.Button(16)


class click:
    def __init__(self, button, time):
        self.button = button
        self.time = time


class hold:
    def __init__(self, button, start, stop):
        self.button = button
        self.state = False
        self.startTime = start
        self.stopTime = stop


class OutputMode(enum):
    ONE = 0
    ON = 1
    OFF = 2


def output(btn, mode: OutputMode):
    if btn == "u":
        out = uOut
    elif btn == "d":
        out = dOut
    elif btn == "r":
        out = rOut
    elif btn == "l":
        out = lOut
    elif btn == "sh":
        out = shareOut
    elif btn == "ps":
        out = psOut
    elif btn == "op":
        out = optOut
    elif btn == "s":
        out = sOut
    elif btn == "t":
        out = tOut
    elif btn == "r1":
        out = r1Out
    elif btn == "l1":
        out = l1Out
    elif btn == "x":
        out = xOut
    elif btn == "o":
        out = oOut
    elif btn == "r2":
        out = r2Out
    elif btn == "l2":
        out = l2Out
    if mode == OutputMode.ONE:
        out.blink(0.05, 0, 1)
    elif mode == OutputMode.ON:
        out.on()
    elif mode == OutputMode.OFF:
        out.off()


# 引数確認
if __name__ == "__main__":
    args = sys.argv
    if 2 <= len(args):
        if not os.path.isfile(args[1]):
            print("ファイルがみつかりません")
            sys.exit()
    else:
        print("ファイルを指定してください")
        sys.exit()
# ファイル読込
with codecs.open(args[1], "r", "utf8") as f:
    lines = f.readlines()
# データー読込
list = []
for s in lines:
    if s.startswith("start"):
        start = s.split("=")[1].strip()
    elif s.startswith("wait"):
        wait = float(s.split("=")[1].strip())
    elif s.startswith("c"):
        c = s.split()
        t = float(c[2])
        obj = click(c[1], t)
        list.append(obj)
    elif s.startswith("r"):
        c = s.split()
        t1 = float(c[2])
        t2 = float(c[3])
        while t1 + 0.05 < t2:
            obj = click(c[1], round(t1, 2))
            list.append(obj)
            t1 += 0.1
    elif s.startswith("l"):
        c = s.split()
        t1 = float(c[2])
        t2 = float(c[3])
        obj = hold(c[1], t1, t2)
        list.append(obj)
# 開始待ち
print("Wait", start, "Button")
while True:
    if (
        (start == "s" and sIn.is_active)
        or (start == "t" and tIn.is_active)
        or (start == "x" and xIn.is_active)
        or (start == "o" and oIn.is_active)
    ):
        break
# 出力
startTime = time.time() + wait
print("Start")
while len(list) > 0:
    if type(list[0]) is click:
        if startTime + list[0].time <= time.time():
            print(round(time.time() - startTime, 2), list[0].button)
            output(list[0].button, OutputMode.ONE)
            list.pop(0)
    elif type(list[0]) is hold:
        if not list[0].state and startTime + list[0].startTime <= time.time():
            print(round(time.time() - startTime, 2), list[0].button, "ON")
            output(list[0].button, OutputMode.ON)
            list[0].state = True
        elif list[0].state and startTime + list[0].stopTime <= time.time():
            print(round(time.time() - startTime, 2), list[0].button, "OFF")
            output(list[0].button, OutputMode.OFF)
            list.pop(0)
