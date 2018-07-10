from Memory import *
from Reg import *
from Cache import *
from ALU import *
import sys


def init(fname, size = 256, pc = 0, lv = 64, sp = 128, cpp = 192, maxClock = 30):
    regs = {}
    regs['pc'] = Register('pc', pc)
    regs['lv'] = Register('lv', lv)
    regs['sp'] = Register('sp', sp)
    regs['cpp'] = Register('cpp', cpp)
    regs['ar'] = Register('ar')
    regs['dr'] = Register('dr')
    regs['tr'] = Register('tr')
    regs['acc'] = Register('acc')
    regs['ir'] = Register('ir', radix = 16)
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
            # print(l, end="")
            words = l.split()
            if words[0] == "ORG":
                head = int(words[1])
            else:
                arr[head] = enc[words[0]]
                if words[0] == "BIPUSH" or words[0] == "ILOAD":
                    head += 1
                    byte = int(words[1]) % 256
                    # if int(words[1]) < 0:
                    #      byte -= 256
                    arr[head] = byte
                elif words[0] == "GOTO" or words[0] == "IFEQ" or words[0] == "IFLT" or words[0] == "IF_ICMPEQ":
                    head += 1
                    dbyte = int(words[1]) % (2 ** 16)
                    arr[head] = dbyte // 256
                    head += 1
                    arr[head] = dbyte % 256
                elif words[0] == "IINC":
                    head += 1
                    byte = int(words[1]) % 256
                    arr[head] = byte
                    head += 1
                    byte = int(words[2]) % 256
                    arr[head] = byte
                head += 1
    print(arr)
    return maxClock, Memory(size, arr), enc, regs


global fname
maxClock, mem, enc, regs = init(fname)
cache = Cache()
alu = ALU()
clock = 0
offset = 0
varnum = 0
const = 0
byte = 0
datas = [{} for i in range(maxClock)]

def clk():
    global clock, maxClock
    if clock < maxClock:
        print("\nin clock:", clock, "executing: ", sys._getframe(1).f_code.co_name)
        for i in regs.keys():
            datas[clock][i] = regs[i].datasOfThisClk
            regs[i].clk()
        datas[clock]['cache'] = cache.datasOfThisClk
        cache.clk()
        datas[clock]['mem'] = mem.datasOfThisClk
        mem.clk()
        datas[clock]['ALU'] = alu.datasOfThisClk
        alu.clk()
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

def fenito():
    global datas, maxClock
    cells = cache.finish()
    addition = len(cells) * mem.maxDelay
    datas += [{} for i in range(addition)]
    maxClock += addition
    for c in cells:
        delay = mem.delayDuration()
        mem.write(c.tag, c.data)
        for i in range(delay - 1):
            clk()
        mem.datasOfThisClk["ready"] = True
        clk()
    x = regs['sp'].val
    while x < regs['cpp'].val:
        if mem.arr[x] > 0:
            mem.arr[x] = 0
        x += 1

def writeMem(addr, data):
    if cache.isIn(addr):
        cache.write(addr, data)
    else:
        readMem(addr)
        cache.write(addr, data)
    clk()

def pop():
    regs["sp"].dec()
    clk()
    regs["sp"].dec()
    clk()
    regs["sp"].dec()
    clk()
    regs["sp"].dec()
    clk()
    regs['ar'].assign(regs['sp'].val)
    clk()
    a = read()
    return a

def NOP():
    regs["pc"].inc()
    clk()

def IFEQ():
    a = pop()
    regs['acc'].assign(a)
    alu.ent_a(a, b = 0)
    if a == 0:
        regs['pc'].assign(regs['pc'].val + offset)
    else:
        regs['pc'].inc()
        clk()
        regs['pc'].inc()
        clk()
        regs['pc'].inc()
    clk()

def IFLT():
    a = pop()
    regs['dr'].assign(a)
    alu.ent_a(a, b = 0)
    if a < 0:
        regs['pc'].assign(regs['pc'].val + offset)
    else:
        regs['pc'].inc()
        clk()
        regs['pc'].inc()
        clk()
        regs['pc'].inc()
    clk()

def IF_ICMPEQ():
    a = pop()
    regs['dr'].assign(a)
    clk()
    b = pop()
    regs['acc'].assign(b)
    clk()
    alu.sub(a, b)
    if a == b:
        regs['pc'].assign(regs['pc'].val + offset)
    else:
        regs['pc'].inc()
        clk()
        regs['pc'].inc()
        clk()
        regs['pc'].inc()
    clk()

def GOTO():
    regs['pc'].assign(regs['pc'].val + offset)
    clk()

def IADD():
    a = pop()
    regs['acc'].assign(a)
    b = pop()
    regs['dr'].assign(b)
    alu.add(a, b)
    writeMem(regs['sp'].val, a + b)
    regs['sp'].inc()
    clk()
    regs['sp'].inc()
    regs['pc'].inc()
    clk()
    regs['sp'].inc()
    clk()
    regs['sp'].inc()
    clk()

def BIPUSH():
    regs['ar'].assign(regs['sp'].val)
    clk()
    regs['dr'].assign(byte)
    writeMem(regs['ar'].val, byte)
    regs["sp"].inc()
    regs['pc'].inc()
    clk()
    regs["sp"].inc()
    regs['pc'].inc()
    clk()
    regs["sp"].inc()
    clk()
    regs["sp"].inc()
    clk()

def ISUB():
    a = pop()
    regs['acc'].assign(a)
    b = pop()
    regs['dr'].assign(b)
    alu.sub(a, b)
    writeMem(regs['sp'].val, a - b)
    regs['sp'].inc()
    clk()
    regs['sp'].inc()
    regs['pc'].inc()
    clk()
    regs['sp'].inc()
    clk()
    regs['sp'].inc()
    clk()

def ILOAD():
    regs['ar'].assign(regs['lv'].val + 4 * varnum)
    regs['pc'].inc()
    clk()
    v = read()
    regs['pc'].inc()
    clk()
    regs['pc'].inc()
    writeMem(regs['sp'].val, v)
    regs['sp'].inc()
    clk()
    regs['sp'].inc()
    clk()
    regs['sp'].inc()
    clk()
    regs['sp'].inc()
    clk()

def IINC():
    regs['ar'].assign(regs['lv'].val + 4 * varnum)
    regs['pc'].inc()
    clk()
    a = read()
    regs['dr'].assign(a)
    regs['pc'].inc()
    clk()
    regs['acc'].assign(const)
    regs['pc'].inc()
    clk()
    regs['tr'].assign(regs['lv'].val + 4 * varnum)
    alu.add(const, a)
    writeMem(regs['tr'].val, a + const)

def read():
    v = cache.read(regs['ar'].val)
    if v == "notInHere":
        v = readMem(regs['ar'].val)
    return v

def fetch():
    regs['ar'].assign(regs['pc'].val)
    clk()
    regs['ir'].val = read()
    clk()

def decode():
    global offset, varnum, const, byte
    dec = {v: k for k, v in enc.items()}
    v = regs['ir'].val
    opCode = v // (2 ** 24)
    offset = (v // 256) % (2 ** 16)
    const = (v // 256) % 256
    varnum = (v // (2 ** 16)) % 256
    byte = (v // (2 ** 16)) % 256
    if byte > 127:
        byte -= 256
    if offset > (2 ** 15):
        offset -= 2 ** 16
    globals()[dec[opCode]]()

while clock < maxClock:
    fetch()
    decode()
    mem.prArr()
    cache.prArr()
fenito()
print(mem.arr)
