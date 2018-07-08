from Memory import *
from Reg import *
from Cache import *
import re
from ALU import *

def prrint():
    print("kako :))")

def init(fname = 'input.txt', size = 256, pc = 0, lv = 64, sp = 128, cpp = 192, maxClock = 50):
    regs = {}
    regs['pc'] = Register(pc)
    regs['lv'] = Register(lv)
    regs['sp'] = Register(sp)
    regs['cpp'] = Register(cpp)
    regs['ar'] = Register()
    regs['dr'] = Register()
    regs['tr'] = Register()
    regs['acc'] = Register()
    regs['ir'] = Register()
    enc = {}
    enc["BIPUSH"] = int("10", base=16)
    enc["GOTO"] = int("A7", base=16)
    enc["IADD"] = int("60", base=16)
    enc["IFEQ"] = int("99", base=16)
    enc["IFLT"] = int("9B", base=16)
    enc["IF_ICMPEQ"] = int("9F", base=16)
    enc["IINC"] = int("84", base=16)
    enc["ILOAD"] = int("15", base=16)
    enc["ISUB"] = int("64", base=16)
    enc["NOP"] = 0
    arr = [0] * size
    with open(fname) as file:
        head = 0
        for l in file:
            print(l, end="")
            words = l.split()
            if words[0] == "ORG":
                head = int(words[1])
            else:
                arr[head] = enc[words[0]]
                if words[0] == "BIPUSH" or words[0] == "ILOAD":
                    head += 1
                    byte = int(words[1]) % 256
                    arr[head] = byte
                elif words[0] == "IINC" or words[0] == "GOTO" or words[0] == "IFEQ" or words[0] == "IFLT" or words[0] == "IF_ICMPEQ":
                    head += 1
                    dbyte = int(words[1]) % (2 ** 16)
                    arr[head] = dbyte / 256
                    head += 1
                    arr[head] = dbyte % 256
                head += 1
    print(arr)
    return maxClock, Memory(size, arr), enc, regs

cache = Cache()
clock = 0
maxClock, mem, enc, regs = init(size=16)
datas = [{}] * maxClock
alu = ALU()

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

def decode():
    dec = {v: k for k, v in enc.items()}
    opCode = regs['ir'].val / (2 ** 24)
    globals()[dec[opCode]]()


def write_mem(addr, data):
    if cache.isIn(addr):
        cache.write(addr, data)
    else:
        readMem(addr)
        cache.write(addr, data)
    clk()

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
    a = pop()
    regs['acc'].assign(a)
    alu.ent_a(a, b = 0)
    if a == 0:
        regs['pc'].assign(regs['pc'].val + offset)
    else:
        regs['pc'].inc()

def IFLT(offset):
    a = pop()
    regs['acc'].assign(a)
    alu.ent_a(a, b = 0)
    if a < 0:
        regs['pc'].assign(regs['pc'].val + offset)
    else:
        regs['pc'].inc()

def IF_ICMPEQ(offset):
    a = pop()
    regs['acc'].assign(a)
    b = pop()
    regs['dr'].assign(b)
    alu.sub(a, b)
    if a == b:
        regs['pc'].assign(regs['pc'].val + offset)
    else:
        regs['pc'].inc()

def GOTO(offset):
    regs['pc'].assign(regs['pc'].val + offset)
    clk()

def IADD():
    a = pop()
    regs['acc'].assign(a)
    b = pop()
    regs['dr'].assign(b)
    alu.add(a, b)
    write_mem(regs['sp'].val, a + b)
    regs['sp'].inc()
    clk()

def BIPUSH(byte):
    write_mem(regs['sp'].val, byte)
    regs["sp"].inc()
    clk()

def pop():
    regs["sp"].dec()
    clk()
    a = readMem(regs['sp']).val
    clk()
    return a


def ISUB():
    a = pop()
    b = pop()
    alu.sub(a, b)
    write_mem(regs['sp'].val, a + b)
    regs['sp'].inc()
    clk()

def ISTORE(varnum):
    regs['ar'].assign(regs['lv'].val + 4 * varnum)
    clk()
    a = pop()
    regs['acc'].assign(a)
    write_mem(regs['ar'].data, a)

def IINC(varnum, const):
    regs['ar'].assign(regs['ar'].val + 4 * varnum)
    clk()
    a = readMem(regs['ar'].val)
    regs['acc'].assign(const)
    alu.add(const, a)
    write_mem(regs['ar'].val, a + const)

