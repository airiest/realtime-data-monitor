import sys
from PyQt5 import QtGui
import GraphWidget as gw
import SignalData as sd
import TcpSocket as so

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
logger = getLogger('app')
handler = StreamHandler()

logger.setLevel(INFO)
handler.setLevel(INFO)
formatter = Formatter("[%(asctime)s - %(name)s - %(levelname)s - %(lineno)s]\n%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super().__init__()

        self.playing = True
   
        self.data = sd.SiganlData()
        self.soc = so.TcpSocket(self.data, host, port)
        self.graph = gw.GraphWidget(self.data, self.soc)

        self.initUI()

    def initUI(self):
        self.resize(1000,800)
        self.setWindowTitle('Real-Time Monitor')

        self.play_pause = QtGui.QAction(QtGui.QIcon('./assets/pause.png'), 'playing', self)
        self.play_pause.triggered.connect(self.toggle_playing)

        self.toolbar = self.addToolBar('Menu')
        self.toolbar.addAction(self.play_pause)

        self.setCentralWidget(self.graph)

    def closeEvent(self, event):
        self.graph.close()

    def toggle_playing(self):
        if self.playing:
            self.play_pause.setIcon(QtGui.QIcon("./assets/play.png"))
        else:
            self.play_pause.setIcon(QtGui.QIcon("./assets/pause.png"))
        
        self.playing = not self.playing
        self.graph.toggle_updating()


if __name__ == '__main__':
    host = "localhost"      # set host IP address
    port = 5000             # set host port number

    app = QtGui.QApplication([])
    mainwindow = MainWindow()
    mainwindow.show()

    sys.exit(app.exec_())
