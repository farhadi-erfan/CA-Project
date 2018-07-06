class Register:
    def __init__(self, val = 0, radix = "Dec"):
        self.val = val
        self.radix = radix

    def assign(self, data):
        if data >= 0:
            self.val = data % (2** 31)
        else:
            self.val = -(-data % (2** 31))
        if data / (2** 31) != 0:
            print("overflow")

    def inc(self):
        self.assign(self.val + 1)

    def dec(self):
        self.assign(self.val - 1)

    def setRadix(self, radix):
        self.radix = radix