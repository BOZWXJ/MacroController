#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import enum
import gpiozero
import os
import sys
import datetime

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


class Click:
    def __init__(self, button, timing):
        self.button = button
        self.timing = timing


class Hold:
    def __init__(self, button, start, stop):
        self.button = button
        self.state = False
        self.startTime = start
        self.stopTime = stop


class OutputMode(enum.Enum):
    ONE = 0
    ON = 1
    OFF = 2


class State:
    def __init__(self):
        self.button = ""
        self.hFlg = False
        self.rFlg = False

    def CheckReset(self):
        if self.hFlg:
            print("Off command not found")
            sys.exit()
        if self.rFlg:
            print("Stop command not found")
            sys.exit()

    def HoldSet(self, button):
        if self.hFlg:
            print("Off command not found")
            sys.exit()
        if self.rFlg:
            print("Stop command not found")
            sys.exit()
        self.button = button
        self.hFlg = True

    def HoldReset(self, button):
        if not self.hFlg:
            print("On command not found")
            sys.exit()
        if self.rFlg:
            print("Stop command not found")
            sys.exit()
        if self.button != button:
            print("Button is mismatched")
            sys.exit()
        self.hFlg = False

    def RepeatSet(self, button):
        if self.hFlg:
            print("Off command not found")
            sys.exit()
        if self.rFlg:
            print("Stop command not found")
            sys.exit()
        self.button = button
        self.rFlg = True

    def RepeatReset(self, button):
        if self.hFlg:
            print("Off command not found")
            sys.exit()
        if not self.rFlg:
            print("Start command not found")
            sys.exit()
        if self.button != button:
            print("Button is mismatched")
            sys.exit()
        self.rFlg = False


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


def main(filepath):
    # ファイル読込
    with codecs.open(filepath, "r", "utf8") as f:
        lines = f.readlines()
    # データー読込
    list = []
    Flg = State()
    tmg = None
    tmp = None
    t1: datetime.timedelta
    t2: datetime.timedelta
    minimum = datetime.timedelta.max
    for i in range(len(lines) - 1):
        cell = lines[i + 1].lower().split(",")
        btn = cell[0][:1]
        cmd = cell[0][1:]
        tmp = tmg
        tmg = datetime.datetime.strptime(cell[2], "%H:%M:%S:%f")
        if not tmp is None and tmg - tmp < minimum:
            minimum = tmg - tmp
        print(i + 2, ":", btn, ":", cmd, ":", tmg.strftime("%H:%M:%S:%f"))
        if i == 0:
            st = tmg
            # print(st.strftime("%H:%M:%S:%f"))
        if not cmd:
            Flg.CheckReset()
            t1 = tmg - st
            obj = Click(btn, t1)
            list.append(obj)
            # print(obj.button, obj.timing.total_seconds())
        elif cmd == "on":
            Flg.HoldSet(btn)
            t1 = tmg - st
        elif cmd == "off":
            Flg.HoldReset(btn)
            t2 = tmg - st
            obj = Hold(btn, t1, t2)
            list.append(obj)
            # print(obj.button, obj.startTime.total_seconds(), obj.stopTime.total_seconds())
        elif cmd == "start":
            Flg.RepeatSet(btn)
            t1 = tmg - st
        elif cmd == "stop":
            Flg.RepeatReset(btn)
            t2 = tmg - st
            # print("repeat", btn, t1.total_seconds(), t2.total_seconds())
            while t1 + datetime.timedelta(seconds=0.05) < t2:
                obj = Click(btn, t1)
                list.append(obj)
                # print(obj.button, obj.timing.total_seconds())
                t1 += datetime.timedelta(seconds=0.1)
        else:
            print("Command error!")
            sys.exit()
    print("Minimum Interval:", minimum)
    # 開始待ち
    input("Hit Enter Key")
    # 出力
    startTime = datetime.datetime.now()
    print("Start", startTime)
    while len(list) > 0:
        now = datetime.datetime.now()
        if type(list[0]) is Click:
            if list[0].timing <= now - startTime:
                print(now - startTime, list[0].button)
                output(list[0].button, OutputMode.ONE)
                list.pop(0)
        elif type(list[0]) is Hold:
            if not list[0].state and list[0].startTime <= now - startTime:
                print(now - startTime, list[0].button, "ON")
                output(list[0].button, OutputMode.ON)
                list[0].state = True
            elif list[0].state and list[0].stopTime <= now - startTime:
                print(now - startTime, list[0].button, "OFF")
                output(list[0].button, OutputMode.OFF)
                list.pop(0)


# 引数確認
if __name__ == "__main__":
    args = sys.argv
    if 2 <= len(args):
        if os.path.isfile(args[1]):
            main(args[1])
        else:
            print("File not found.")
    else:
        print("File required.")
