import sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from datetime import datetime
import json

from logging import getLogger
logger = getLogger("app").getChild("GraphWidget")

class GraphWidget(pg.GraphicsLayoutWidget):
    color = [
        "color: rgb(78, 205, 196)",
        "color: rgb(255, 107, 107)",
        "color: rgb(163, 229, 17)",
        "color: rgb(234, 189, 0)",
        "color: rgb(22, 148, 178)",
        "color: rgb(197, 77, 87)"
    ]

    line_color = [
        pg.mkPen(color=(78, 205, 196), width=2, style=QtCore.Qt.SolidLine),
        pg.mkPen(color=(255, 107, 107), width=2, style=QtCore.Qt.SolidLine),
        pg.mkPen(color=(163, 229, 17), width=2, style=QtCore.Qt.SolidLine),
        pg.mkPen(color=(234, 189, 0), width=2, style=QtCore.Qt.SolidLine),
        pg.mkPen(color=(22, 148, 178), width=2, style=QtCore.Qt.SolidLine),
        pg.mkPen(color=(197, 77, 87), width=2, style=QtCore.Qt.SolidLine)
    ]

    brush_color = [
        pg.mkBrush(color=(0, 90, 160)),
        pg.mkBrush(color=(255, 107, 107)),
        pg.mkBrush(color=(163, 229, 17)),
        pg.mkBrush(color=(234, 189, 0)),
        pg.mkBrush(color=(22, 148, 178)),
        pg.mkBrush(color=(197, 77, 87))
    ]

    def __init__(self, dat, soc):
        super().__init__()
        
        pg.setConfigOption('background', (18, 28, 32))
        pg.setConfigOption('foreground', (87, 99, 108))
        pg.setConfigOptions(antialias=True)

        try:
            f = open("conf.json", "r")
            self.jconf = json.load(f)
        except:
            logger.debug(sys.exc_info())
            sys.exit()

        self.updating = True
        self.dat = dat
        self.soc = soc
        self.soc.begin()

        self.initWidget()

    def close(self):
        self.soc.end()
        self.soc.kill()

    def initWidget(self):
        tics_font = QtGui.QFont("Spica Neue Light", 12)
        ts_font = QtGui.QFont("Spica Neue Light", 9)
        label_font = QtGui.QFont("Spica Neue Light", 20)
        val_font = QtGui.QFont("Spica Neue Light", 14)

        self.plot = {}
        self.curve = {}
        self.ts_item = {}
        self.label_item = {}
        self.val_item = {}
        self.ts = {}
        self.label = {}
        self.val = {}
        
        for index, sname in enumerate(self.jconf):
            try:
                if "layer" not in self.jconf[sname]:
                    self.plot[sname] = self.addPlot(title="", row=index, col=0)
                    self.plot[sname].showGrid(x=True, y=True, alpha=0.5)
                    self.plot[sname].setXRange(self.jconf[sname]["xrange"][0], self.jconf[sname]["xrange"][1])
                    self.plot[sname].setYRange(self.jconf[sname]["yrange"][0], self.jconf[sname]["yrange"][1])
                    self.plot[sname].getAxis('bottom').setTickSpacing(major= self.jconf[sname]["xtics"][0], minor=self.jconf[sname]["xtics"][1])
                    self.plot[sname].getAxis('left').setTickSpacing(major=self.jconf[sname]["ytics"][0], minor=self.jconf[sname]["ytics"][1])
                    self.plot[sname].getAxis("bottom").tickFont = tics_font
                    self.plot[sname].getAxis("left").tickFont = tics_font
                    self.plot[sname].setMenuEnabled(False)

                    self.ts_item[sname] = pg.TextItem(color=(150, 150, 150))
                    self.ts_item[sname].setParentItem(self.plot[sname])
                    self.ts_item[sname].setFont(ts_font)
                    self.ts_item[sname].setPos(40, 15)

                    self.label_item[sname] = pg.TextItem(color=(200,200,200))
                    self.label_item[sname].setParentItem(self.plot[sname])
                    self.label_item[sname].setFont(label_font)
                    self.label_item[sname].setHtml("<div align=left>" + sname + "</div>")
                    self.label_item[sname].setPos(40, 35)

                    self.val_item[sname] = pg.TextItem(color=(150, 150, 150))
                    self.val_item[sname].setParentItem(self.plot[sname])
                    self.val_item[sname].setFont(val_font)
                    self.val_item[sname].setPos(40, 65)

                    layer = sname
                else:
                    layer = self.jconf[sname]["layer"]

                if self.jconf[sname]["plot"] == "line":
                    self.curve[sname] = self.plot[layer].plot(pen=self.line_color[self.jconf[sname]["color"]])
                elif self.jconf[sname]["plot"] == "point":
                    self.curve[sname] = self.plot[layer].plot(pen=None, symbolBrush=self.brush_color[self.jconf[sname]["color"]], symbolSize=3, symbolPen=self.line_color[self.jconf[sname]["color"]])
                elif self.jconf[sname]["plot"] == "line-point":
                    self.curve[sname] = self.plot[layer].plot(pen=self.line_color[self.jconf[sname]["color"]], symbolBrush=self.brush_color[self.jconf[sname]["color"]], symbolSize=2, symbolPen=self.line_color[self.jconf[sname]["color"]])
                else:
                    self.curve[sname] = self.plot[layer].plot(pen=self.line_color[self.jconf[sname]["color"]])

            except:
                logger.debug(sys.exc_info())
                sys.exit()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def toggle_updating(self):
        self.updating = not self.updating

    def update(self):
        if not self.updating:
            return
        
        now = datetime.now().timestamp()
        for sname in self.jconf:
            try:
                sig = self.dat.get_signal(sname)
                if len(sig) != 0:
                    xl = list(sig.keys())
                    yl = list(sig.values())

                    if "layer" in self.jconf[sname]:
                        layer = self.jconf[sname]["layer"]
                        self.ts[layer] = str(max(xl))
                        self.label[layer] = self.label[layer] + ", " + sname
                        self.val[layer] = self.val[layer] + "<br>" + "<span style=\"{0}\">".format(self.color[self.jconf[sname]["color"]]) + sname + " : " + str(round(yl[xl.index(max(xl))], int(self.jconf[sname]["digit"]))) + "</span>"
                    else:
                        layer = sname
                        self.ts[layer] = str(max(xl))
                        self.label[layer] = sname
                        self.val[layer] = "<span style=\"{0}\">".format(self.color[self.jconf[sname]["color"]]) + sname + " : " + str(round(yl[xl.index(max(xl))], int(self.jconf[layer]["digit"]))) + "</span>"

                    self.ts_item[layer].setHtml("<div align=left>" + self.ts[layer] + "</div>")
                    self.label_item[layer].setHtml("<div align=left>" + self.label[layer] + "</div>")
                    self.val_item[layer].setHtml("<div align=left>" + self.val[layer] + "</div>")
                                        
                    xl = list(map(lambda x: x - now, xl))
                    self.curve[sname].setData(xl, yl, clear=False)

            except:
                logger.debug(sys.exc_info())
                sys.exit()

