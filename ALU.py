# this module is created by Sina, One of the best teammates ever.
from Clocketc import *
class ALU(Clockable):
    def __init__(self):
        super()
        self.datasOfThisClk["Z"] = 0
        self.datasOfThisClk["N"] = 0
        self.datasOfThisClk["opcode"] = 0
        self.datasOfThisClk["result"] = 0

    @staticmethod
    def check_outputs(self, outp):
        if outp == 0:
            self.datasOfThisClk["Z"] = 1
        elif outp < 0:
            self.datasOfThisClk["N"] = 1
        self.datasOfThisClk["result"] = outp

    @staticmethod
    def add(self, a, b):
        res = a + b
        self.check_outputs(res)
        self.datasOfThisClk["opcode"] = 60

    @staticmethod
    def ent_a(self, a, b):
        self.check_outputs(a)
        self.datasOfThisClk["opcode"] = 24

    @staticmethod
    def ent_b(self, a, b):
        self.check_outputs(b)
        self.datasOfThisClk["opcode"] = 20

    @staticmethod
    def app (self, a, b):
        self.check_outputs(a + 1)
        self.datasOfThisClk["opcode"] = 57

    @staticmethod
    def bpp(self, a, b):
        self.check_outputs(b + 1)
        self.datasOfThisClk["opcode"] = 61

    @staticmethod
    def sub(self, a, b):
        self.check_outputs(b - a)
        self.datasOfThisClk["opcode"] = 63

    @staticmethod
    def neg_a (self, a, b):
        self.check_outputs(-a)
        self.datasOfThisClk["opcode"] = 59

