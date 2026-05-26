from PyQt6.QtWidgets import QLabel, QStyle

HINTS = {
    "email": "Correo electrónico de la cuenta de Tapo asociada.",
    "password": "Contraseña de la cuenta de Tapo asociada.",
    "ip": "Dirección IP del enchufe. Se puede consultar desde la información de dispositivo en la aplicación de Tapo.",
}

class Hint(QLabel):

    def __init__(self, hint_key, parent=None):
        super().__init__(parent)

        icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_MessageBoxInformation
        )

        self.setPixmap(icon.pixmap(16, 16))

        info = HINTS.get(hint_key, "No hay información adicional.")
        self.setToolTip(info)