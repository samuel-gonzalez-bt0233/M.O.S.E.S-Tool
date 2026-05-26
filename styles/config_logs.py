from enum import Enum

class LogType(Enum):
    INFO = "#D4D4D4"      # Gris claro (estándar)
    SUCCESS = "#2ECC71"   # Verde
    WARNING = "#F1C40F"   # Amarillo
    ERROR = "#E74C3C"     # Rojo
    DEBUG = "#3498DB"     # Azul
    ACUM = "#8E44AD"