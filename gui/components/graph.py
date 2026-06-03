import pyqtgraph as pg
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt
import time
from styles.config_logs import LogType

class Graph(pg.PlotWidget):
    def __init__(self, line_color, color_fill):
        super().__init__()
        self.setBackground('#FFFFFF')
        self.showGrid(x=True, y=True, alpha=0.1)
        self.curve = self.plot(pen=pg.mkPen(color=line_color, width=3),
                               fillLevel=0, brush=color_fill)