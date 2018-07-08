from Clocketc import *
class CacheCell:
    def __init__(self, addr = 0, data = 0):
        self.data = data
        self.tag = addr
        self.usage = 0
        self.dirty = False

class Cache(Clockable):
    def __init__(self, size = 64, way = 2):
        Clockable.__init__(self)
        self.size = size
        self.way = way
        self.arr = [[CacheCell()] * way] * size

    def isIn(self, addr):
        out = False
        for i in range(self.way):
            if self.arr[addr % self.size][i] != None:
                out = out or self.arr[addr % self.size][i].tag == addr
        return out

    def find(self, addr):
        for i in range(self.way):
            if self.arr[addr % self.size][i].tag == addr:
                return self.arr[addr % self.size][i]

    def read(self, addr):
        if self.isIn(addr):
            cell = self.find(addr)
            cell.usage += 1
            return cell.data
        else:
            return "notInHere"


    def write(self, addr, data):
        p = addr % self.size
        if self.isIn(addr):
            cell = self.find(addr)
            cell.usage += 1
            cell.data = data
            cell.dirty = True
        else:
            for i in range(self.way):
                if self.arr[p][i] == None:
                    self.arr[p][i] = CacheCell(addr, data)
                    return
            k = -1
            mink = float('inf')
            for i in range(self.way):
                if self.arr[p][i].usage < mink:
                    mink = self.arr[p][i].usage
                    k = i
            cell = self.arr[p][k]
            self.arr[p][k] = CacheCell(addr, data)
            if cell.dirty:
                return ("write back", cell)