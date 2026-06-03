import csv
import time
import pyqtgraph as pg
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QGridLayout, QHBoxLayout, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from styles.hint import Hint


# --- VENTANA DE CONFIGURACIÓN INICIAL ---
class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración de M.O.S.E.S")
        self.setFixedSize(300, 350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.config_data = {}

        # 2. Inicialización de Layouts
        layout = QVBoxLayout(self)
        grid_credentials = QGridLayout()

        # 3. Título de la sección
        grid_credentials.addWidget(QLabel("<b>Credenciales Tapo P110/P115</b>"),0,0,1,3)

        # 4. Campo: Email
        grid_credentials.addWidget(QLabel("Email (TP-Link):"), 1, 0, 1, 3)
        self.input_email = QLineEdit("example@gmail.com")
        grid_credentials.addWidget(self.input_email, 2, 0, 1, 2)
        grid_credentials.addWidget(Hint("email"), 2, 2)

        # 5. Campo: Contraseña
        grid_credentials.addWidget(QLabel("Contraseña:"), 3, 0,1,3)
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)  # Ocultar pass
        grid_credentials.addWidget(self.input_pass, 4, 0, 1, 2)
        grid_credentials.addWidget(Hint("password"), 4, 2)

        # 6. Campo: IP del Enchufe
        grid_credentials.addWidget(QLabel("IP del Enchufe:"), 5, 0,1,3)
        self.input_ip = QLineEdit("10.171.247.148")
        grid_credentials.addWidget(self.input_ip, 6,0,1,2)
        grid_credentials.addWidget(Hint("ip"), 6,2)

        grid_credentials.setColumnStretch(0, 4)
        grid_credentials.setColumnStretch(1, 1)
        grid_credentials.setColumnStretch(2, 0)

        # 7. Integración de Layouts y Botón de Acción
        layout.addLayout(grid_credentials)

        self.btn_start = QPushButton("Conectar")
        self.btn_start.setStyleSheet(
            "background-color: #27AE60; "
            "color: white; "
            "font-weight: bold; "
            "padding: 10px; "
            "margin-top: 10px;"
        )
        self.btn_start.clicked.connect(self.validate_and_close)
        layout.addWidget(self.btn_start)


    def validate_and_close(self):
        try:
        
            # Guardar todo en el diccionario
            self.config_data = {
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


