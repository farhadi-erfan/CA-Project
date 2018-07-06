class Memory:
    def __init__(self, size = 256, arr = None):
        if arr == None:
            self.size = size
            self.arr = [0] * size
        else:
            self.arr = arr


    def reset(self, arr = None):
        if arr == None:
            self.arr = [0] * self.size
        else:
            self.arr = arr

    def read(self, addr):
        return self.arr[addr]

    def write(self, addr, data):
        self.arr[addr] = data