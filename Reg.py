from Clocketc import *
class Register(Clockable):
    def __init__(self, name, val = 0, radix = 10):
        Clockable.__init__(self)
        self.name = name
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
        self.datasOfThisClk["val"] = self.val
        if data // (2** 31) != 0 and data >= 0:
            print("overflow")

    def inc(self):
        self.datasOfThisClk["inc"] = True
        self.assign(self.val + 1)
        self.datasOfThisClk["val"] = self.val

    def dec(self):
        self.datasOfThisClk["dec"] = True
        self.assign(self.val - 1)
        self.datasOfThisClk["val"] = self.val

    def showData(self):
        print(self.name, end = " ")
        if self.radix == 10:
            Clockable.showData(self)
            print()
        elif self.radix == 16:
            for k, v in self.datasOfThisClk.items():
                if k.__str__() == "val":
                    print(k.__str__() + ":", hex(v))
                else:
                    print(k.__str__() + ":" + v.__str__(), end=", ")

    def clk(self):
        self.showData()
        self.datasOfThisClk["inc"] = False
        self.datasOfThisClk["load"] = False
        self.datasOfThisClk["dec"] = False
        self.datasOfThisClk["val"] = self.val