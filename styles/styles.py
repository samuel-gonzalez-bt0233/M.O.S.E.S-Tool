# styles.py

STYLE_SHEET = """
    QMainWindow { background-color: #FFFFFF; }
    QWidget#Header { background-color: #F4F7F6; border-bottom: 1px solid #E0E0E0; }
    QLabel { color: #2D3436; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
    QLabel#ValorWatts { font-size: 42px; font-weight: 800; color: #2ECC71; }
    QLabel#Titulo { font-size: 18px; font-weight: bold; color: #27AE60; }
    QLineEdit {
        background-color: white; border: 2px solid #DCDDE1; border-radius: 8px;
        padding: 5px; color: #2D3436; font-size: 14px; font-weight: bold;
    }
    QPushButton {
        background-color: #27AE60; color: white; border-radius: 8px;
        padding: 8px 12px; font-weight: bold; font-size: 11px;
    }
    QPushButton#BtnToggle { background-color: #8E44AD; }
    QPushButton#BtnExport { background-color: #3498DB; }
    QPushButton#BtnHistory { background-color: #F39C12; }
    QPushButton#BtnAccuracy {background-color: #96235E; }
    QPushButton#BtnHelp {background-color: #D16821; }
    QPushButton#BtnReconnect {background-color: #7724E3; }
    QTextEdit#Terminal {
        background-color: #1E1E1E; color: #D4D4D4;
        font-family: 'Consolas', monospace; font-size: 11px;
        border: none; border-top: 3px solid #27AE60;
    }
    QGroupBox {
    border: 2px solid #C0C0C0; /* Color del borde del recuadro */
    border-radius: 8px;
    margin-top: 10px; /* Espacio para que el título no choque con el borde superior */
    font-weight: bold;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left; /* Posición del título */
        left: 10px;
        padding: 0 5px;
        color: black; /* <--- ESTO fuerza el color negro siempre */
    }
"""