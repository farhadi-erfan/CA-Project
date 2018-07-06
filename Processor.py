from Reg import *

class Processor:
    def __init__(self, pc = 0, lv = 64, sp = 128, cpp = 192):
        self.pc = Register(pc)
        self.lv = Register(lv)
        self.sp = Register(sp)
        self.cpp = Register(cpp)
        self.ar = Register()
        self.dr = Register()
        self.tr = Register()
        self.acc = Register()
        self.ir = Register()