from Clocketc import *
class Register(Clockable):
    def __init__(self, val = 0, radix = "Dec"):
        Clockable.__init__(self)
        self.val = val
        self.radix = radix
        self.datasOfThisClk["inc"] = False
        self.datasOfThisClk["load"] = False
        self.datasOfThisClk["dec"] = False
        self.datasOfThisClk["val"] = self.val

    def assign(self, data):
        self.datasOfThisClk["load"] = True
        if data >= 0:
            self.val = data % (2** 31)
        else:
            self.val = -(-data % (2** 31))
        if data / (2** 31) != 0:
            print("overflow")

    def inc(self):
        self.datasOfThisClk["inc"] = True
        self.assign(self.val + 1)

    def dec(self):
        self.datasOfThisClk["dec"] = True
        self.assign(self.val - 1)

    def setRadix(self, radix):
        self.radix = radix

    def clk(self):
        self.datasOfThisClk["inc"] = False
        self.datasOfThisClk["load"] = False
        self.datasOfThisClk["dec"] = False
        self.datasOfThisClk["val"] = self.val