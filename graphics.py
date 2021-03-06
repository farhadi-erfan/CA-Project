# graphics.py
__version__ = "5.0"
from tkinter import *
from tkinter.filedialog import askopenfilename
import time, os, sys

try:  # import as appropriate for 2.x vs. 3.x
    import tkinter as tk
except:
    import Tkinter as tk


##########################################################################
# Module Exceptions

class GraphicsError(Exception):
    """Generic error class for graphics module exceptions."""
    pass


OBJ_ALREADY_DRAWN = "Object currently drawn"
UNSUPPORTED_METHOD = "Object doesn't support operation"
BAD_OPTION = "Illegal option value"

##########################################################################
# global variables and funtions

_root = tk.Tk()
_root.withdraw()

_update_lasttime = time.time()


def update(rate=None):
    global _update_lasttime
    if rate:
        now = time.time()
        pauseLength = 1 / rate - (now - _update_lasttime)
        if pauseLength > 0:
            time.sleep(pauseLength)
            _update_lasttime = now + pauseLength
        else:
            _update_lasttime = now

    _root.update()


############################################################################
# Graphics classes start here

class GraphWin(tk.Canvas):
    """A GraphWin is a toplevel window for displaying graphics."""

    def __init__(self, title="IJVM Emulator",
                 width=550, height=500, autoflush=True):
        assert type(title) == type(""), "Title must be a string"
        master = tk.Toplevel(_root)
        master.protocol("WM_DELETE_WINDOW", self.close)
        tk.Canvas.__init__(self, master, width=width, height=height,
                           highlightthickness=0, bd=0)
        self.master.title(title)
        self.pack()
        master.resizable(0, 0)
        self.filename = ""
        self.foreground = "black"
        self.items = []
        self.mouseX = None
        self.mouseY = None
        self.bind("<Button-1>", self._onClick)
        self.bind_all("<Key>", self._onKey)
        self.height = int(height)
        self.width = int(width)
        self.autoflush = autoflush
        self._mouseCallback = None
        self.trans = None
        self.closed = False
        master.lift()
        self.lastKey = ""
        if autoflush: _root.update()

    def __repr__(self):
        if self.isClosed():
            return "<Closed GraphWin>"
        else:
            return "GraphWin('{}', {}, {})".format(self.master.title(),
                                                   self.getWidth(),
                                                   self.getHeight())

    def __str__(self):
        return repr(self)

    def __checkOpen(self):
        if self.closed:
            raise GraphicsError("window is closed")

    def _onKey(self, evnt):
        self.lastKey = evnt.keysym

    def setBackground(self, color):
        """Set background color of the window"""
        self.__checkOpen()
        self.config(bg=color)
        self.__autoflush()

    def setCoords(self, x1, y1, x2, y2):
        """Set coordinates of window to run from (x1,y1) in the
        lower-left corner to (x2,y2) in the upper-right corner."""
        self.trans = Transform(self.width, self.height, x1, y1, x2, y2)
        self.redraw()

    def close(self):
        """Close the window"""

        if self.closed: return
        self.closed = True
        self.master.destroy()
        self.__autoflush()

    def isClosed(self):
        return self.closed

    def isOpen(self):
        return not self.closed

    def __autoflush(self):
        if self.autoflush:
            _root.update()

    def plot(self, x, y, color="black"):
        """Set pixel (x,y) to the given color"""
        self.__checkOpen()
        xs, ys = self.toScreen(x, y)
        self.create_line(xs, ys, xs + 1, ys, fill=color)
        self.__autoflush()

    def plotPixel(self, x, y, color="black"):
        """Set pixel raw (independent of window coordinates) pixel
        (x,y) to color"""
        self.__checkOpen()
        self.create_line(x, y, x + 1, y, fill=color)
        self.__autoflush()

    def flush(self):
        """Update drawing to the window"""
        self.__checkOpen()
        self.update_idletasks()

    def getMouse(self):
        """Wait for mouse click and return Point object representing
        the click"""
        self.update()  # flush any prior clicks
        self.mouseX = None
        self.mouseY = None
        while self.mouseX == None or self.mouseY == None:
            self.update()
            if self.isClosed(): raise GraphicsError("getMouse in closed window")
            time.sleep(.1)  # give up thread
        x, y = self.toWorld(self.mouseX, self.mouseY)
        self.mouseX = None
        self.mouseY = None
        return Point(x, y)

    def checkMouse(self):
        """Return last mouse click or None if mouse has
        not been clicked since last call"""
        if self.isClosed():
            raise GraphicsError("checkMouse in closed window")
        self.update()
        if self.mouseX != None and self.mouseY != None:
            x, y = self.toWorld(self.mouseX, self.mouseY)
            self.mouseX = None
            self.mouseY = None
            return Point(x, y)
        else:
            return None

    def getKey(self):
        """Wait for user to press a key and return it as a string."""
        self.lastKey = ""
        while self.lastKey == "":
            self.update()
            if self.isClosed(): raise GraphicsError("getKey in closed window")
            time.sleep(.1)  # give up thread

        key = self.lastKey
        self.lastKey = ""
        return key

    def checkKey(self):
        """Return last key pressed or None if no key pressed since last call"""
        if self.isClosed():
            raise GraphicsError("checkKey in closed window")
        self.update()
        key = self.lastKey
        self.lastKey = ""
        return key

    def getHeight(self):
        """Return the height of the window"""
        return self.height

    def getWidth(self):
        """Return the width of the window"""
        return self.width

    def toScreen(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.screen(x, y)
        else:
            return x, y

    def toWorld(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.world(x, y)
        else:
            return x, y

    def setMouseHandler(self, func):
        self._mouseCallback = func

    def _onClick(self, e):
        self.mouseX = e.x
        self.mouseY = e.y
        if self._mouseCallback:
            self._mouseCallback(Point(e.x, e.y))

    def addItem(self, item):
        self.items.append(item)

    def delItem(self, item):
        self.items.remove(item)

    def redraw(self):
        for item in self.items[:]:
            item.undraw()
            item.draw(self)
        self.update()


class Transform:
    """Internal class for 2-D coordinate transformations"""

    def __init__(self, w, h, xlow, ylow, xhigh, yhigh):
        # w, h are width and height of window
        # (xlow,ylow) coordinates of lower-left [raw (0,h-1)]
        # (xhigh,yhigh) coordinates of upper-right [raw (w-1,0)]
        xspan = (xhigh - xlow)
        yspan = (yhigh - ylow)
        self.xbase = xlow
        self.ybase = yhigh
        self.xscale = xspan / float(w - 1)
        self.yscale = yspan / float(h - 1)

    def screen(self, x, y):
        # Returns x,y in screen (actually window) coordinates
        xs = (x - self.xbase) / self.xscale
        ys = (self.ybase - y) / self.yscale
        return int(xs + 0.5), int(ys + 0.5)

    def world(self, xs, ys):
        # Returns xs,ys in world coordinates
        x = xs * self.xscale + self.xbase
        y = self.ybase - ys * self.yscale
        return x, y


# Default values for various item configuration options. Only a subset of
#   keys may be present in the configuration dictionary for a given item
DEFAULT_CONFIG = {"fill": "",
                  "outline": "black",
                  "width": "1",
                  "arrow": "none",
                  "text": "",
                  "justify": "center",
                  "font": ("helvetica", 12, "normal")}


class GraphicsObject:
    """Generic base class for all of the drawable objects"""

    # A subclass of GraphicsObject should override _draw and
    #   and _move methods.

    def __init__(self, options):
        # options is a list of strings indicating which options are
        # legal for this object.

        # When an object is drawn, canvas is set to the GraphWin(canvas)
        #    object where it is drawn and id is the TK identifier of the
        #    drawn shape.
        self.canvas = None
        self.id = None

        # config is the dictionary of configuration options for the widget.
        config = {}
        for option in options:
            config[option] = DEFAULT_CONFIG[option]
        self.config = config

    def setFill(self, color):
        """Set interior color to color"""
        self._reconfig("fill", color)

    def setOutline(self, color):
        """Set outline color to color"""
        self._reconfig("outline", color)

    def setWidth(self, width):
        """Set line weight to width"""
        self._reconfig("width", width)

    def draw(self, graphwin):

        """Draw the object in graphwin, which should be a GraphWin
        object.  A GraphicsObject may only be drawn into one
        window. Raises an error if attempt made to draw an object that
        is already visible."""

        if self.canvas and not self.canvas.isClosed(): raise GraphicsError(OBJ_ALREADY_DRAWN)
        if graphwin.isClosed(): raise GraphicsError("Can't draw to closed window")
        self.canvas = graphwin
        self.id = self._draw(graphwin, self.config)
        graphwin.addItem(self)
        if graphwin.autoflush:
            _root.update()
        return self

    def undraw(self):

        """Undraw the object (i.e. hide it). Returns silently if the
        object is not currently drawn."""

        if not self.canvas: return
        if not self.canvas.isClosed():
            self.canvas.delete(self.id)
            self.canvas.delItem(self)
            if self.canvas.autoflush:
                _root.update()
        self.canvas = None
        self.id = None

    def move(self, dx, dy):

        """move object dx units in x direction and dy units in y
        direction"""

        self._move(dx, dy)
        canvas = self.canvas
        if canvas and not canvas.isClosed():
            trans = canvas.trans
            if trans:
                x = dx / trans.xscale
                y = -dy / trans.yscale
            else:
                x = dx
                y = dy
            self.canvas.move(self.id, x, y)
            if canvas.autoflush:
                _root.update()

    def _reconfig(self, option, setting):
        # Internal method for changing configuration of the object
        # Raises an error if the option does not exist in the config
        #    dictionary for this object
        if option not in self.config:
            raise GraphicsError(UNSUPPORTED_METHOD)
        options = self.config
        options[option] = setting
        if self.canvas and not self.canvas.isClosed():
            self.canvas.itemconfig(self.id, options)
            if self.canvas.autoflush:
                _root.update()

    def _draw(self, canvas, options):
        """draws appropriate figure on canvas with options provided
        Returns Tk id of item drawn"""
        pass  # must override in subclass

    def _move(self, dx, dy):
        """updates internal state of object to move it dx,dy units"""
        pass  # must override in subclass


class Point(GraphicsObject):
    def __init__(self, x, y):
        GraphicsObject.__init__(self, ["outline", "fill"])
        self.setFill = self.setOutline
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "Point({}, {})".format(self.x, self.y)

    def _draw(self, canvas, options):
        x, y = canvas.toScreen(self.x, self.y)
        return canvas.create_rectangle(x, y, x + 1, y + 1, options)

    def _move(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy

    def clone(self):
        other = Point(self.x, self.y)
        other.config = self.config.copy()
        return other

    def getX(self): return self.x

    def getY(self): return self.y


class _BBox(GraphicsObject):
    # Internal base class for objects represented by bounding box
    # (opposite corners) Line segment is a degenerate case.

    def __init__(self, p1, p2, options=["outline", "width", "fill"]):
        GraphicsObject.__init__(self, options)
        self.p1 = p1.clone()
        self.p2 = p2.clone()

    def _move(self, dx, dy):
        self.p1.x = self.p1.x + dx
        self.p1.y = self.p1.y + dy
        self.p2.x = self.p2.x + dx
        self.p2.y = self.p2.y + dy

    def getP1(self): return self.p1.clone()

    def getP2(self): return self.p2.clone()

    def getCenter(self):
        p1 = self.p1
        p2 = self.p2
        return Point((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)



def openfile(win, b):
    b.config(state="normal")
    fn = askopenfilename()
    win.filename = fn

class Data_container:
    def __init__(self):
        self.data = 0
        self.counter = 0
        self.clksmiss = 0
        self.clkshit = 0
        self.cache = None
        self.mem = None


def emulate(win, dc):
    if win.filename == "":
        raise Exception("No file selected.")
    import runpy
    a = runpy.run_module("Controller", {"fname": win.filename, "maxClock": 200})
    dc.data = a['datas']
    dc.clksmiss = a['clksmiss']
    dc.clkshit = a['clkshit']
    dc.mem = a['mem']
    dc.cache = a['cache']
    print("-----------------final status-----------------")
    print("Throughput:", dc.clkshit)
    print("utilization:", format(dc.clkshit / (dc.clkshit + dc.clksmiss), ".3f"))
    print("cache hitRate:", format(dc.cache.datasOfThisClk['hitRate until now'], ".3f"))
    s = ''
    for i in dc.mem.arr:
        s += hex(i)[2:] + ', '
    s = "[" + s[:len(s) - 2] + "]"
    print('memory:', s)

def next_func(dc, vars):
    dc.counter += 1
    print(dc.counter)
    print(dc.data[dc.counter])
    vars["clk"].set("clk:" + str(dc.counter))
    vars["AR"].set("AR:" + str(dc.data[dc.counter]["ar"]["val"]))
    vars["AR-load"].set("AR-load:" + str(dc.data[dc.counter]["ar"]["load"]))
    vars["AR-Inc"].set("AR-Inc:" + str(dc.data[dc.counter]["ar"]["inc"]))
    vars["IR"].set("IR:" + hex(dc.data[dc.counter]["ir"]["val"]))
    vars["IR-load"].set("IR-load:" + str(dc.data[dc.counter]["ir"]["load"]))
    vars["IR-Inc"].set("IR-inc:" + str(dc.data[dc.counter]["ir"]["inc"]))
    vars["TR"].set("TR:" + str(dc.data[dc.counter]["tr"]["val"]))
    vars["TR-load"].set("TR-load:" + str(dc.data[dc.counter]["tr"]["load"]))
    vars["TR-inc"].set("TR-inc:" + str(dc.data[dc.counter]["tr"]["inc"]))
    vars["DR"].set("DR:" + str(dc.data[dc.counter]["dr"]["val"]))
    vars["DR-load"].set("DR-load:" + str(dc.data[dc.counter]["dr"]["load"]))
    vars["DR-inc"].set("DR-inc:" + str(dc.data[dc.counter]["dr"]["inc"]))
    vars["ACC"].set("ACC:" + str(dc.data[dc.counter]["acc"]["val"]))
    vars["ACC-load"].set("ACC-load:" + str(dc.data[dc.counter]["acc"]["load"]))
    vars["ACC-inc"].set("ACC-inc:" + str(dc.data[dc.counter]["acc"]["inc"]))
    vars["SP"].set("SP:" + str(dc.data[dc.counter]["sp"]["val"]))
    vars["SP-inc"].set("SP-inc:" + str(dc.data[dc.counter]["sp"]["inc"]))
    vars["lv"].set("lv:" + str(dc.data[dc.counter]["lv"]["val"]))
    vars["rwn"].set("rwn:" + str(dc.data[dc.counter]["Memory"]["rwn"]))
    vars["ready"].set("ready:" + str(dc.data[dc.counter]["Memory"]["ready"]))
    vars["start"].set("start:" + str(dc.data[dc.counter]["Memory"]["start"]))
    vars["hit rate so far"].set("hit rate so far:" +
                                str(dc.data[dc.counter]["cache"]["hitRate until now"]))
    vars["PC"].set("PC:" + str(dc.data[dc.counter]["pc"]["val"]))
    vars["PC-load"].set("PC-load:" + str(dc.data[dc.counter]["pc"]["load"]))
    vars["PC-inc"].set("PC-inc:" + str(dc.data[dc.counter]["pc"]["inc"]))


def prev_func(dc, vars):
    dc.counter -= 1
    print(dc.counter)
    print(dc.data[dc.counter])
    vars["clk"].set("clk:" + str(dc.counter))
    vars["AR"].set("AR:" + str(dc.data[dc.counter]["ar"]["val"]))
    vars["AR-load"].set("AR-load:" + str(dc.data[dc.counter]["ar"]["load"]))
    vars["AR-Inc"].set("AR-Inc:" + str(dc.data[dc.counter]["ar"]["inc"]))
    vars["IR"].set("IR:" + hex(dc.data[dc.counter]["ir"]["val"]))
    vars["IR-load"].set("IR-load:" + str(dc.data[dc.counter]["ir"]["load"]))
    vars["IR-Inc"].set("IR-inc:" + str(dc.data[dc.counter]["ir"]["inc"]))
    vars["TR"].set("TR:" + str(dc.data[dc.counter]["tr"]["val"]))
    vars["TR-load"].set("TR-load:" + str(dc.data[dc.counter]["tr"]["load"]))
    vars["TR-inc"].set("TR-inc:" + str(dc.data[dc.counter]["tr"]["inc"]))
    vars["DR"].set("DR:" + str(dc.data[dc.counter]["dr"]["val"]))
    vars["DR-load"].set("DR-load:" + str(dc.data[dc.counter]["dr"]["load"]))
    vars["DR-inc"].set("DR-inc:" + str(dc.data[dc.counter]["dr"]["inc"]))
    vars["ACC"].set("ACC:" + str(dc.data[dc.counter]["acc"]["val"]))
    vars["ACC-load"].set("ACC-load:" + str(dc.data[dc.counter]["acc"]["load"]))
    vars["ACC-inc"].set("ACC-inc:" + str(dc.data[dc.counter]["acc"]["inc"]))
    vars["SP"].set("SP:" + str(dc.data[dc.counter]["sp"]["val"]))
    vars["SP-inc"].set("SP-inc:" + str(dc.data[dc.counter]["sp"]["inc"]))
    vars["lv"].set("lv:" + str(dc.data[dc.counter]["lv"]["val"]))
    vars["rwn"].set("rwn:" + str(dc.data[dc.counter]["Memory"]["rwn"]))
    vars["ready"].set("ready:" + str(dc.data[dc.counter]["Memory"]["ready"]))
    vars["start"].set("start:" + str(dc.data[dc.counter]["Memory"]["start"]))
    vars["hit rate so far"].set("hit rate so far:" +
                                str(dc.data[dc.counter]["cache"]["hitRate until now"]))
    vars["PC"].set("PC:" + str(dc.data[dc.counter]["pc"]["val"]))
    vars["PC-load"].set("PC-load:" + str(dc.data[dc.counter]["pc"]["load"]))
    vars["PC-inc"].set("PC-inc:" + str(dc.data[dc.counter]["pc"]["inc"]))

def final_state(win, dc, vars, labels):
    for name in labels.keys():
        if name != "Throughput" and name != "Final Hit Rate" and name != "Utilization":
            labels[name].destroy()
    vars['Throughput'].set("Throughput:" + str(dc.clkshit))
    vars["Final Hit Rate"].set("Final Hit Rate:" + format(dc.cache.datasOfThisClk['hitRate until now'], ".3f"))
    vars['Utilization'].set("Utilization:" + format((dc.clkshit / (dc.clkshit + dc.clksmiss)), ".3f"))
    pass

def test():
    string = """Select code file to emulate.
        values of registers and signals are shown below.
        final values and memory data are reported in a text file at last."""
    win = GraphWin()
    dc = Data_container()
    win.setCoords(0, 0, 10, 10)
    b_emulate = Button(win, text="emulate", command=lambda: emulate(win, dc)
                       ,fg="#a1dbcd", bg="#383a39", state="disabled")
    b_emulate.place(x=350, y=450)
    b_open = Button(win, text="open file", command=lambda: openfile(win, b_emulate)
    ,fg="#a1dbcd", bg="#383a39")
    b_open.place(x=450, y=450)
    vars = {}
    vars["clk"] = StringVar()
    vars["AR"] = StringVar()
    vars["AR-load"] = StringVar()
    vars["AR-Inc"] = StringVar()
    vars["IR"] = StringVar()
    vars["IR-load"] = StringVar()
    vars["IR-Inc"] = StringVar()
    vars["TR"] = StringVar()
    vars["TR-load"] = StringVar()
    vars["TR-inc"] = StringVar()
    vars["DR"] = StringVar()
    vars["DR-load"] = StringVar()
    vars["DR-inc"] = StringVar()
    vars["ACC"] = StringVar()
    vars["ACC-load"] = StringVar()
    vars["ACC-inc"] = StringVar()
    vars["SP"] = StringVar()
    vars["SP-inc"] = StringVar()
    vars["lv"] = StringVar()
    vars["rwn"] = StringVar()
    vars["ready"] = StringVar()
    vars["start"] = StringVar()
    vars["hit rate so far"] = StringVar()
    vars["PC"] = StringVar()
    vars["PC-load"] = StringVar()
    vars["PC-inc"] = StringVar()
    vars["Throughput"] = StringVar()
    vars["Final Hit Rate"] = StringVar()
    vars["Utilization"] = StringVar()
    labels = {}
    myx = 10
    myy = 200
    for name in vars.keys():
        vars[name].set(name + ":" + str(0))
        labels[name] = Label(win, textvariable=vars[name])
        labels[name].place(x=myx, y=myy)
        myx += 120
        if myx > 450:
            myy += 20
            myx = 10

    w = Label(win, text=string, fg="green", font=("Helvetica", 14),
              justify=CENTER, wraplength=0, highlightthickness=2,
              highlightbackground="black")
    w.place(x=4, y=50)
    clock_button = Button(win, text="next", fg="#a1dbcd", bg="#383a39")
    clock_button.place(x=270, y=450)
    clock_button.configure(command=lambda: next_func(dc, vars))
    clock_button2 = Button(win, text="prev", fg="#a1dbcd", bg="#383a39")
    clock_button2.place(x=220, y=450)
    clock_button2.configure(command=lambda: prev_func(dc, vars))
    haji = Button(win, text="Final Statistics", fg="#a1dbcd", bg="#383a39")
    haji.place(x=90, y=450)
    haji.configure(command=lambda : final_state(win, dc, vars, labels))
    win.getMouse()


update()

if __name__ == "__main__":
    test()




