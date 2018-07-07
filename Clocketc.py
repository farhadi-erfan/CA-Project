class Clockable:
    def __init__(self):
        self.datasOfThisClk = {}
    def clk(self):
        for i in self.datasOfThisClk.keys():
            self.datasOfThisClk[i] = None