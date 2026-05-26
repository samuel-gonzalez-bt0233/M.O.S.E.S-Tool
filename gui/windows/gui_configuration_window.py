import csv
import time
import pyqtgraph as pg
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QGridLayout, QHBoxLayout, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from styles.hint import Hint

from gui.windows.early_stopping_alert_window import EarlyStoppingAlertWindow
from gui.windows.early_stopping_config_window import EarlyStoppingConfigWindow


# --- VENTANA DE CONFIGURACIÓN INICIAL ---
class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración Bananza 🍌")
        self.setFixedSize(350, 450)
        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowType.WindowContextHelpButtonHint)

        self.config_data = {}
        self.thresholds = (80.0, 5000.0)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Configuración de Umbrales y Alertas</b>"))

        grid_rules = QGridLayout()
        grid_rules.addWidget(QLabel("Umbral Instantáneo (W):"), 0, 0)
        self.input_inst = QLineEdit("80.0")
        grid_rules.addWidget(self.input_inst, 0, 1)
        grid_rules.addWidget(Hint("inst_threshold"), 0, 2)

        grid_rules.addWidget(QLabel("Umbral Acumulado (W):"), 1, 0)
        self.input_accum = QLineEdit("80.0")
        grid_rules.addWidget(self.input_accum, 1, 1)
        grid_rules.addWidget(Hint("accum_threshold"), 1, 2)

        grid_rules.addWidget(QLabel("Baseline (W/s)"), 2, 0)
        self.input_baseline = QLineEdit("10")
        grid_rules.addWidget(self.input_baseline, 2, 1)
        grid_rules.addWidget(Hint("baseline"), 2, 2)

        self.early_stopping_config_dialog = EarlyStoppingConfigWindow()
        self.btn_early_stopping = QPushButton("Configurar Early Stopping")
        self.btn_early_stopping.clicked.connect(self.open_early_stopping_config_dialog)
        grid_rules.addWidget(self.btn_early_stopping,3,0,1,3)

        layout.addLayout(grid_rules)

        layout.addWidget(QLabel("<hr>"))  # Separador visual

        # --- Campos del Enchufe Tapo ---
        layout.addWidget(QLabel("<b>Credenciales Tapo P110/P115</b>"))

        grid_credentials = QGridLayout()

        grid_credentials.addWidget(QLabel("Email (TP-Link):"),0,0)
        self.input_email = QLineEdit("samuel.gonzalez.ramos.2004@gmail.com")
        grid_credentials.addWidget(self.input_email,1,0,1,2)
        grid_credentials.addWidget(Hint("email"),1,2)


        grid_credentials.addWidget(QLabel("Contraseña:"),2,0)
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(
            QLineEdit.EchoMode.Password)  # Ocultar pass
        grid_credentials.addWidget(self.input_pass,3,0,1,2)
        grid_credentials.addWidget(Hint("password"),3,2)

        grid_credentials.addWidget(QLabel("IP del Enchufe:"),4,0)
        self.input_ip = QLineEdit("10.171.247.148")
        grid_credentials.addWidget(self.input_ip,4,1)
        grid_credentials.addWidget(Hint("ip"),4,2)

        layout.addLayout(grid_credentials)

        self.btn_start = QPushButton("Conectar")
        self.btn_start.setStyleSheet(
            "background-color: #27AE60; color: white; font-weight: bold; padding: 10px; margin-top: 10px;")
        self.btn_start.clicked.connect(self.validate_and_close)
        layout.addWidget(self.btn_start)


    def validate_and_close(self):
        try:
            # Validar que los umbrales sean números
            inst = float(self.input_inst.text())
            accum = float(self.input_accum.text())
            baseline = float(self.input_baseline.text())

            # Guardar todo en el diccionario
            self.config_data = {
                "inst_threshold": inst,
                "accum_threshold": accum,
                "baseline": baseline,
                "ip": self.input_ip.text(),
                "email": self.input_email.text(),
                "pass": self.input_pass.text()
            }

            # Validar que no haya campos vacíos en credenciales
            if not all([self.config_data["ip"], self.config_data["email"], self.config_data["pass"]]):
                raise ValueError("Las credenciales no pueden estar vacías.")

            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Dato no válido: {e}")

    def open_early_stopping_config_dialog(self):
        self.early_stopping_config_dialog.exec()

"""
a partir de layout.addWigdet(input_acum)
self.btn_iniciar = QPushButton("Iniciar Monitorización")
        self.btn_iniciar.setStyleSheet("background-color: #27AE60; color: white; font-weight: bold; padding: 10px;")
        self.btn_iniciar.clicked.connect(self.validar_y_cerrar)
        layout.addWidget(self.btn_iniciar)

    def validar_y_cerrar(self):
        try:
            inst = float(self.input_inst.text())
            acum = float(self.input_acum.text())
            self.umbrales = (inst, acum)
            self.accept()
        except ValueError:
            QMessageBox.critical(self, "Error", "Introduce valores numéricos válidos.")



"""
