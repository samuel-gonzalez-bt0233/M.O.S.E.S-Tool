import pyqtgraph as pg
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt
import time
from styles.config_logs import LogType

class EcoGraph(pg.PlotWidget):
    def __init__(self, line_color, color_fill, initial_threshold, initial_baseline=None):
        super().__init__()
        self.setBackground('#FFFFFF')
        self.showGrid(x=True, y=True, alpha=0.1)
        self.curve = self.plot(pen=pg.mkPen(color=line_color, width=3),
                               fillLevel=0, brush=color_fill)
        self.threshold_line = pg.InfiniteLine(pos=initial_threshold, angle=0,
                                              pen=pg.mkPen(color='#E74C3C', width=2, style=Qt.PenStyle.DashLine))
        self.addItem(self.threshold_line)
        self.baseline_line = None
        if initial_baseline is not None:
            self.baseline_line = pg.InfiniteLine(pos=initial_baseline, angle=0,
                                                 pen=pg.mkPen(color='#F39C12', width=2, style=Qt.PenStyle.DashLine))
            self.addItem(self.baseline_line)

class EcoTerminal(QTextEdit):
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if EcoTerminal._initialized:
            return
        EcoTerminal._initialized = True
        super().__init__()
        self.setObjectName("Terminal")
        self.setReadOnly(True)

    def log(self, message, log_type=LogType.INFO):
        ts = time.strftime('%H:%M:%S')
        color = log_type.value if isinstance(log_type, LogType) else log_type
        html_msg = f'<span style="color: #888888;">[{ts}]</span> <span style="color: {color};">{message}</span>'
        self.append(html_msg)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())