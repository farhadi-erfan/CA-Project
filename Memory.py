from random import *
from Clocketc import *


class Memory(Clockable):
    def __init__(self, size = 256, arr = None, minDelay = 1, maxDelay = 4):
        Clockable.__init__(self)
        if arr == None:
            self.size = size
            self.arr = [0] * size
        else:
            self.arr = arr
        self.minDelay = minDelay
        self.maxDelay = maxDelay
        self.datasOfThisClk["reset"] = False
        self.datasOfThisClk["rwn"] = True
        self.datasOfThisClk["start"] = False
        self.datasOfThisClk["ready"] = True

    def clk(self):
        self.datasOfThisClk["reset"] = False
        self.datasOfThisClk["start"] = False

    def delayDuration(self):
        return random.randint(self.minDelay, self.maxDelay)

    def reset(self, arr = None):
        self.datasOfThisClk["reset"] = True
        if arr == None:
            self.arr = [0] * self.size
        else:
            self.arr = arr

    def read(self, addr):
        self.datasOfThisClk["start"] = True
        self.datasOfThisClk["rwn"] = True
        self.datasOfThisClk["ready"] = False
        return self.arr[addr]

    def write(self, addr, data):
        self.datasOfThisClk["start"] = True
        self.datasOfThisClk["rwn"] = False
        self.datasOfThisClk["ready"] = False
        self.arr[addr] = data