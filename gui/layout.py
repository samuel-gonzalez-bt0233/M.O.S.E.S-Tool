from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QStackedWidget, QGroupBox)
from PyQt6.QtCore import Qt
from gui.components.graph import Graph
from gui.components.terminal import Terminal
import pyqtgraph as pg


class AppLayout(QMainWindow):
    def setup_ui(self, model):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --- HEADER ---
        self.header = QWidget(objectName="Header")
        header_layout = QGridLayout(self.header)

        self.title_label = QLabel("Visual MOSES", objectName="Titulo")
        self.title_label.setStyleSheet("font-size: 56px; font-weight: bold; color: #2ECC71;")
        header_layout.addWidget(self.title_label, 0,0)

        self.label_author = QLabel("Desarrollado por: Samuel González Ramos", objectName="TextoAutor")
        self.label_author.setStyleSheet(
            "font-size: 10px; "          
            "font-style: italic; "       
            "color: #7F8C8D; "           
            "margin-top: 25px;"          
        )
        header_layout.addWidget(self.label_author, 0, 3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        # 1. Grupo Monitorización (Cuadrícula 2x2)
        self.group_monit = QGroupBox("Monitorización")
        layout_monit = QGridLayout(self.group_monit)
        self.btn_toggle = QPushButton("Vista: Acumulado", objectName="BtnToggle")
        self.btn_training_metrics = QPushButton("Vista: Resultados", objectName="BtnAccuracy")
        self.btn_reset = QPushButton("Resetear")

        layout_monit.addWidget(self.btn_toggle, 0, 0)
        layout_monit.addWidget(self.btn_training_metrics, 0, 1)
        layout_monit.addWidget(self.btn_reset, 1, 0, 1, 2)

        # 2. Grupo Registers
        self.group_registers = QGroupBox("Registros")
        layout_registers = QVBoxLayout(self.group_registers)
        self.btn_history = QPushButton("Visualizar Históricos", objectName="BtnHistory")
        self.btn_export = QPushButton("Exportar Logs", objectName="BtnExport")

        layout_registers.addWidget(self.btn_history)
        layout_registers.addWidget(self.btn_export)

        # 3. Grupo Ayuda
        self.group_help = QGroupBox("Config y Ayuda")
        layout_help = QVBoxLayout(self.group_help)
        self.btn_help = QPushButton("Ayuda/Info", objectName="BtnHelp")
        self.btn_reconnect = QPushButton("Reconfigurar", objectName="BtnReconnect")

        layout_help.addWidget(self.btn_help)
        layout_help.addWidget(self.btn_reconnect)

        #4. Voltaje actual
        self.group_watts = QGroupBox("Voltaje actual")
        layout_watts = QVBoxLayout(self.group_watts)
        self.label_watts = QLabel("0.0 W", objectName="ValorWatts")
        layout_watts.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.label_watts.setStyleSheet("font-size: 38px; font-weight: bold;")
        layout_watts.addWidget(self.label_watts)


        # Añadir grupos al header
        header_layout.addWidget(self.group_monit, 1, 0)
        header_layout.addWidget(self.group_registers, 1, 1)
        header_layout.addWidget(self.group_help, 1, 2)
        header_layout.addWidget(self.group_watts, 1, 3)

        main_layout.addWidget(self.header)

        # GRÁFICAS
        self.stack = QStackedWidget()
        self.graph_inst = Graph('#2ECC71', (46, 204, 113, 40))
        self.graph_accum = Graph('#8E44AD', (142, 68, 173, 40))
        self.graph_inst.setLabel('left', 'Potencia', units='W')
        self.graph_inst.setLabel('bottom', 'Tiempo', units='s')
        
        self.graph_accum.setLabel('left', 'Consumo Total', units='W s')
        self.graph_accum.setLabel('bottom', 'Tiempo', units='s')
        self.training_container = QWidget()
        training_layout = QVBoxLayout(self.training_container)

        self.graph_training_metrics = pg.PlotWidget()
        self.graph_training_metrics.setBackground('#FFFFFF')
        self.graph_training_metrics.showGrid(x=True, y=True, alpha=0.1)
        self.graph_training_metrics.setLabel('bottom', 'Tiempo', units='s')

        self.training_controls = QWidget()
        self.btn_prev_metric = QPushButton("<<<")
        self.btn_next_metric = QPushButton(">>>")
        controls_layout = QHBoxLayout(self.training_controls)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(self.btn_prev_metric)
        controls_layout.addWidget(self.btn_next_metric)

        training_layout.addWidget(self.graph_training_metrics)
        training_layout.addWidget(self.training_controls)

        self.stack.addWidget(self.graph_inst)
        self.stack.addWidget(self.graph_accum)
        self.stack.addWidget(self.training_container)

        # --- TERMINAL ---
        self.terminal = Terminal()
        main_layout.addWidget(self.stack, stretch=4)
        main_layout.addWidget(self.terminal, stretch=1)