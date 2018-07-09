# this module is created by Sina, One of the best teammates ever.
# joon
from Clocketc import *
class ALU(Clockable):
    def __init__(self):
        Clockable.__init__(self)
        self.datasOfThisClk["Z"] = 0
        self.datasOfThisClk["N"] = 0
        self.datasOfThisClk["opcode"] = 0
        self.datasOfThisClk["result"] = 0

    def clk(self):
        self.showData()
        self.datasOfThisClk["Z"] = 0
        self.datasOfThisClk["N"] = 0
        self.datasOfThisClk["opcode"] = 0
        self.datasOfThisClk["result"] = 0


    def check_outputs(self, outp):
        if outp == 0:
            self.datasOfThisClk["Z"] = 1
        elif outp < 0:
            self.datasOfThisClk["N"] = 1
        self.datasOfThisClk["result"] = outp

    def add(self, a, b):
        res = a + b
        self.check_outputs(res)
        self.datasOfThisClk["opcode"] = 60

    def ent_a(self, a, b):
        self.check_outputs(a)
        self.datasOfThisClk["opcode"] = 24

    def ent_b(self, a, b):
        self.check_outputs(b)
        self.datasOfThisClk["opcode"] = 20

    def app (self, a, b):
        self.check_outputs(a + 1)
        self.datasOfThisClk["opcode"] = 57

    def bpp(self, a, b):
        self.check_outputs(b + 1)
        self.datasOfThisClk["opcode"] = 61

    def sub(self, a, b):
        self.check_outputs(b - a)
        self.datasOfThisClk["opcode"] = 63

    def neg_a (self, a, b):
        self.check_outputs(-a)
        self.datasOfThisClk["opcode"] = 59

    def showData(self):
        print("ALU", end = " ")
        Clockable.showData(self)
        print()