from Clocketc import *
class CacheCell:
    def __init__(self, addr = -1, data = 0):
        self.data = data
        self.tag = addr
        self.usage = 0
        self.dirty = False

    def isNone(self):
        return self.data == 0 and self.tag == -1


class Cache(Clockable):
    def __init__(self, size = 64, way = 2):
        Clockable.__init__(self)
        self.size = size
        self.way = way
        self.queries = 0
        self.hits = 0
        self.arr = [[CacheCell() for i in range(way)] for i in range(size)]
        self.datasOfThisClk['hitRate until now'] = 1
        self.datasOfThisClk['hits'] = self.hits
        self.datasOfThisClk['misses'] = self.queries - self.hits

    def showData(self):
        print('cache hitRate until now:', format(self.datasOfThisClk['hitRate until now'], '.2f'))
        print('cache hits:', self.hits)

    def clk(self):
        self.showData()
        if self.queries > 0:
            self.datasOfThisClk = {}
            self.datasOfThisClk['hitRate until now'] = self.hits / self.queries
            self.datasOfThisClk['hits'] = self.hits
            self.datasOfThisClk['misses'] = self.queries - self.hits


    def isIn(self, addr):
        out = False
        for i in range(self.way):
            if self.arr[addr % self.size][i] != None:
                if self.arr[addr % self.size][i].tag != -1:
                    out = out or self.arr[addr % self.size][i].tag == addr
        return out

    def find(self, addr):
        for i in range(self.way):
            if self.arr[addr % self.size][i].tag == addr:
                return self.arr[addr % self.size][i]

    def read(self, addr):
        self.queries += 1
        if self.isIn(addr):
            self.hits += 1
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
                if self.arr[p][i].isNone():
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

    def finish(self):
        out = []
        for i in range(self.size):
            for j in range(self.way):
                if self.arr[i][j].dirty:
                    out += [self.arr[i][j]]
                    self.arr[i][j] = CacheCell()
        return out

    def prArr(self):
        out = []
        for i in range(self.size):
            for j in range(self.way):
                if not self.arr[i][j].isNone():
                    out += ["index:" + str(i) + " way:" + str(j) + " addr:" + str(self.arr[i][j].tag) + " data:" + str(self.arr[i][j].data)]
        print("Cache summery:", out)