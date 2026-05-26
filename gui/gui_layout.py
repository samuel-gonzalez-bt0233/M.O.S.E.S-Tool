from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QStackedWidget, QGroupBox)
from PyQt6.QtCore import Qt
from gui.gui_components import EcoGraph, EcoTerminal
import pyqtgraph as pg

from gui.windows.early_stopping_config_window import EarlyStoppingConfigWindow


class AppLayout(QMainWindow):
    def setup_ui(self, model):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --- HEADER ---
        self.header = QWidget(objectName="Header")
        header_layout = QGridLayout(self.header)

        # Título + watts en vivo
        header_layout.addWidget(QLabel("ECO", objectName="Titulo"), 0, 0)
        self.label_watts = QLabel("0.0 W", objectName="ValorWatts")
        header_layout.addWidget(self.label_watts, 0, 3, Qt.AlignmentFlag.AlignRight)

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
        self.group_registers = QGroupBox("Registers")
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

        # 4. Grupo Realtime
        self.group_data = QGroupBox("Umbrales y Alertas")
        layout_data = QGridLayout(self.group_data)

        self.input_inst_threshold = QLineEdit(str(model.inst_threshold))
        self.input_accum_threshold = QLineEdit(str(model.accum_threshold))
        self.input_baseline = QLineEdit(str(model.baseline))
        self.btn_early_stopping_config = QPushButton("Configurar Early Stopping", objectName="BtnEarlyStopping")
        self.early_stopping_config_dialog = EarlyStoppingConfigWindow()

        layout_data.addWidget(QLabel("Umbral  (W)"), 0, 0)
        layout_data.addWidget(QLabel("Umbral  (W)"), 0, 1)
        layout_data.addWidget(QLabel("Baseline (W/s)"), 0, 2)
        layout_data.addWidget(self.input_inst_threshold, 1, 0)
        layout_data.addWidget(self.input_accum_threshold, 1, 1)
        layout_data.addWidget(self.input_baseline, 1, 2)
        layout_data.addWidget(self.btn_early_stopping_config, 2, 0, 1, 2)

        legend_widget = QWidget()
        legend_layout = QVBoxLayout(legend_widget)
        legend_layout.setContentsMargins(4, 0, 0, 0)
        legend_layout.setSpacing(2)
        for color, label in [("#E74C3C", "Instantáneo"), ("#8E44AD", "Acumulado"), ("#F39C12", "Baseline")]:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(2)
            dot = QLabel("———")
            dot.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: 900; letter-spacing: 3px;")
            row_layout.addWidget(dot)
            row_layout.addWidget(QLabel(label))
            row_layout.addStretch()
            legend_layout.addWidget(row)
        layout_data.addWidget(legend_widget, 2, 2)

        # Añadir grupos al header
        header_layout.addWidget(self.group_monit, 1, 0)
        header_layout.addWidget(self.group_registers, 1, 1)
        header_layout.addWidget(self.group_help, 1, 2)
        header_layout.addWidget(self.group_data, 1, 3)

        main_layout.addWidget(self.header)

        # GRÁFICAS
        self.stack = QStackedWidget()
        self.graph_inst = EcoGraph('#2ECC71', (46, 204, 113, 40), model.inst_threshold, model.baseline)
        self.graph_accum = EcoGraph('#8E44AD', (142, 68, 173, 40), model.accum_threshold)

        # CONTENEDOR DE ENTRENAMIENTO
        self.training_container = QWidget()
        training_layout = QVBoxLayout(self.training_container)

        self.graph_training_metrics = pg.PlotWidget()
        self.graph_training_metrics.setBackground('#FFFFFF')
        self.graph_training_metrics.showGrid(x=True, y=True, alpha=0.1)

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
        self.terminal = EcoTerminal()
        main_layout.addWidget(self.stack, stretch=4)
        main_layout.addWidget(self.terminal, stretch=1)

    def open_early_stopping_config_dialog(self):
        self.early_stopping_config_dialog.exec()