from Memory import *
from Reg import *
from Cache import *
from random import *
from ALU import *

def init(pc = 0, lv = 64, sp = 128, cpp = 192, maxClock = 50):
    regs['pc'] = Register(pc)
    regs['lv'] = Register(lv)
    regs['sp'] = Register(sp)
    regs['cpp'] = Register(cpp)
    regs['ar'] = Register()
    regs['dr'] = Register()
    regs['tr'] = Register()
    regs['acc'] = Register()
    regs['ir'] = Register()
    maxClock = maxClock
maxClock = 50
mem = Memory()
cache = Cache()
regs = {}
clock = 0
init()
datas = [{}] * maxClock

def clk():
    global clock
    for i in regs.keys():
        datas[clock][i] = regs[i].datasOfThisClk
        regs[i].clk()
    datas[clock]['cache'] = cache.datasOfThisClk
    cache.clk()
    datas[clock]['mem'] = mem.datasOfThisClk
    mem.clk()
    clock += 1


def readMem(addr):
    delay = mem.delayDuration()
    data = mem.read(addr)
    for i in range(delay - 1):
        clk()
    mem.datasOfThisClk["ready"] = True
    res = cache.write(addr, data)
    clk()
    if res != None and res[0] == "write back":
        cell = res[1]
        delay = mem.delayDuration()
        mem.write(cell.tag, cell.data)
        for i in range(delay - 1):
            clk()
        mem.datasOfThisClk["ready"] = True
        clk()
    return data

def fetch():
    regs['ar'].assign(regs['pc'].val)
    clk()
    v = cache.read(regs['ar'].val)
    if v == "notInHere":
        readMem(regs['ar'].val)
        regs['ir'] = v
        clk()
    else:
        regs['ir'] = v
        clk()

def NOP():
    regs["pc"].inc()
    clk()

def IFEQ(offset):
    a = readMem(regs["sp"].val)
    regs["sp"].dec()
    clk()
    ALU.ent_a(a, b = 0)
    if a == 0:
        regs['pc'].assign(regs['pc'].val + offset)
    else:
        regs['pc'].inc()

def IFLT(offset):
    a = readMem(regs['sp'].val)
    regs['sp'].dec()
    clk()
    ALU.ent_a(a, b = 0)
    if a < 0:
        regs['pc'].assign(regs['pc'].val + offset)
    else:
        regs['pc'].inc()

def IF_ICMPEQ(offset):
    a = readMem(regs["sp"].val)
    regs["sp"].dec()
    clk()
    b = readMem(regs['sp'].val)
    regs['sp'].dec()
    clk()
    ALU.sub(a, b)
    if a == b:
        regs['pc'].assign(regs['pc'].val + offset)
    else:
        regs['pc'].inc()

def GOTO(offset):
