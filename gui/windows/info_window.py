from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from styles.info import INFO_CONTENTS

class HelpWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guía de Uso - M.O.S.E.S")
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Visor de texto (soporta HTML básico)
        self.visor = QTextBrowser()
        self.visor.setHtml(INFO_CONTENTS)
        layout.addWidget(self.visor)
        
        self.btn_close = QPushButton("Entendido")
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close)