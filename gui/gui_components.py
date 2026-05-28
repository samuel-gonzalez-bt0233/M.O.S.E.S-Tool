import pyqtgraph as pg
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt
import time
from styles.config_logs import LogType

class EcoGraph(pg.PlotWidget):
    def __init__(self, line_color, color_fill):
        super().__init__()
        self.setBackground('#FFFFFF')
        self.showGrid(x=True, y=True, alpha=0.1)
        self.curve = self.plot(pen=pg.mkPen(color=line_color, width=3),
                               fillLevel=0, brush=color_fill)

class EcoTerminal(QTextEdit):
    def __init__(self, parent=None):
        
        super().__init__(parent)
        self.setObjectName("Terminal")
        self.setReadOnly(True)

    def log(self, message, log_type=LogType.INFO):
        ts = time.strftime('%H:%M:%S')
        color = log_type.value if isinstance(log_type, LogType) else log_type
        html_msg = f'<span style="color: #888888;">[{ts}]</span> <span style="color: {color};">{message}</span>'
        self.append(html_msg)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())