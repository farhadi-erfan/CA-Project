import random
from Clocketc import *


class Memory(Clockable):
    def __init__(self, size = 256, arr = None, minDelay = 1, maxDelay = 4):
        Clockable.__init__(self)
        if arr == None:
            self.size = size
            self.arr = [0] * size
        else:
            self.arr = arr
            self.size = len(arr)
        self.minDelay = minDelay
        self.maxDelay = maxDelay
        self.datasOfThisClk["reset"] = False
        self.datasOfThisClk["rwn"] = True
        self.datasOfThisClk["start"] = False
        self.datasOfThisClk["ready"] = True

    def clk(self):
        self.showData()
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
        if addr + 3 < self.size:
            # print(hex(self.arr[addr + 1]))
            # return (bits(self.arr[addr ], 8), bits(self.arr[addr + 1], 8), bits(self.arr[addr + 2], 8), bits(self.arr[addr + 3], 8))
            return ((self.arr[addr] * 256 + self.arr[addr + 1]) * 256 + self.arr[addr + 2]) * 256 + self.arr[addr + 3]

    def write(self, addr, data):
        self.datasOfThisClk["start"] = True
        self.datasOfThisClk["rwn"] = False
        self.datasOfThisClk["ready"] = False
        pdata = self.partition(data)
        self.arr[addr] = pdata[0]
        self.arr[addr + 1] = pdata[1]
        self.arr[addr + 2] = pdata[2]
        self.arr[addr + 3] = pdata[3]


    def partition(self, data):
        data1 = data % 256
        data //= 256
        data2 = data % 256
        data //= 256
        data3 = data % 256
        data //= 256
        data4 = data % 256
        return (data4, data3, data2, data1)


    def prArr(self):
        out = []
        for i in range(self.size):
            if self.arr[i] != 0:
                out += [(i, self.arr[i])]
        print(out)

    def showData(self):
        print("Memory", end = " ")
        Clockable.showData(self)
        print()

def bits(number, size_in_bits):
    if number < 0:
        return compliment(bin(abs(number) - 1)[2:]).rjust(size_in_bits, '1')
    else:
        return bin(number)[2:].rjust(size_in_bits, '0')

def compliment(value):
    return ''.join(COMPLEMENT[x] for x in value)

COMPLEMENT = {'1': '0', '0': '1'}

def addOne(bits):
    i = len(bits) - 1
    while i >= 0:
        if bits[i] == '1':
            bits = bits[:i] + '0' + bits[i + 1:]
        elif bits[i] == '0':
            bits = bits[:i] + '1' + bits[i + 1:]
            print(bits)
            return bits
        i -= 1
    print('1' + '0' * len(bits))
    return '1' + '0' * len(bits)

def checkNeg(bits):
    if bits[0] == '1':
        return -int(addOne(compliment(bits)), 2)
    else:
        return int(bits, 2)
