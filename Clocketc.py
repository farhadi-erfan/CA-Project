class Clockable:
    def __init__(self):
        self.datasOfThisClk = {}
    def clk(self):
        self.showData()
        for i in self.datasOfThisClk.keys():
            self.datasOfThisClk[i] = None
    def showData(self):
        for k, v in self.datasOfThisClk.items():
            print(k.__str__() + ":" + v.__str__(), end = ", ")
