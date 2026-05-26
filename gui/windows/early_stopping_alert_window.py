from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QFrame

from core.early_stopping_handler import EarlyStoppingHandler
from gui.windows.early_stopping_config_window import EarlyStoppingConfigWindow
from typing import Literal


class EarlyStoppingAlertWindow(QDialog):
    handler = EarlyStoppingHandler()
    def __init__(self, metric: str, phase: Literal["train", "val"]):
        super().__init__()
        self.setWindowTitle("Alerta Early Stopping")
        self.setFixedSize(300, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.early_stopping_config_dialog = EarlyStoppingConfigWindow()

        self.metric = metric
        self.phase = phase

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("<b>⚠ Alerta Early Stopping</b>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(f"Se ha detectado monotonía en la métrica {metric} en la fase {phase}\n\n¿Qué desea hacer?")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        layout.addStretch()

        self.btn_reset_window = QPushButton("Reiniciar ventana de la métrica")
        self.btn_reset_window.clicked.connect(self.reset_metric_window)
        self.btn_edit_rule = QPushButton("Gestionar regla")
        self.btn_edit_rule.clicked.connect(self.open_early_stopping_config_dialog)
        self.btn_early_stop = QPushButton("Aplicar Early Stopping")
        self.btn_early_stop.clicked.connect(self.apply_early_stopping)

        for btn in (self.btn_reset_window, self.btn_edit_rule, self.btn_early_stop):
            layout.addWidget(btn)

        layout.addStretch()

    def open_early_stopping_config_dialog(self):
        self.early_stopping_config_dialog.exec()

    def apply_early_stopping(self):
        self.close()
        self.handler.send_stop_signal()

    def reset_metric_window(self):
        self.handler.reset_window(self.metric, self.phase)
        self.close()

    def closeEvent(self, event):
        self.handler.allow_alert()
        super().closeEvent(event)