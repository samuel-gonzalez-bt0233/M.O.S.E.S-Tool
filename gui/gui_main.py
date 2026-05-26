from PyQt6.QtWidgets import QFileDialog, QDialog
from PyQt6.QtCore import QTimer, pyqtSignal

from handlers.models.metrics_model import MetricsModel
from gui.gui_layout import AppLayout
from handlers.models.energy_model import EnergyModel
from gui.windows.gui_historic_window import HistoricWindow
from gui.windows.gui_info_window import HelpWindow
from handlers.energy_handler import EnergyHandler
from handlers.metrics_handler import MetricsHandler
from styles.styles import STYLE_SHEET
from core.metrics_dto import MetricsDto
from styles.config_logs import LogType

class AppEco(AppLayout):
    new_training_metrics = pyqtSignal(MetricsDto)
    reconnection_request = pyqtSignal(dict)

    def __init__(self, data_queue):
        super().__init__()
        self.energy_model = EnergyModel()
        self.results_model = MetricsModel()
        self.data_queue = data_queue
        self.setup_ui(self.energy_model)
        self.resize(1200, 800)
        self.setStyleSheet(STYLE_SHEET)

        self.tapo_stop_event = None
        self._energy = EnergyHandler(
            self.energy_model, self, self.stack, self.btn_toggle,
            self.graph_inst, self.graph_accum,
            self.label_watts
        )
        self._metrics = MetricsHandler(
            self.results_model, self.stack, self.training_container,
            self.graph_training_metrics, self.btn_toggle,
            self.btn_training_metrics, self.btn_next_metric, self.btn_prev_metric,
        )
        self._connect_events()
        self.terminal.log(f"SESIÓN INICIADA: {self.energy_model.csv_file}", LogType.DEBUG)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(1000)

    def _connect_events(self):
        self.btn_reset.clicked.connect(self._energy.reset)
        self.btn_toggle.clicked.connect(self._energy.toggle_graph)
        self.btn_history.clicked.connect(self.open_history)
        self.btn_export.clicked.connect(self.export_logs)
        self.btn_help.clicked.connect(self.open_help)
        self.new_training_metrics.connect(self._metrics.process_new_training_metrics)
        self.btn_reconnect.clicked.connect(self.emit_config)

    def update_all(self):
        while not self.data_queue.empty():
            dato = self.data_queue.get_nowait()
            if isinstance(dato, str):
                self.terminal.log(f"TAPO: {dato}", LogType.ERROR)
            else:
                self.energy_model.register_measurement(dato)

        valor = self.energy_model.last_measurement
        self.energy_model.register_measurement(valor)
        self._energy.update(valor)

    def open_history(self):
        v = HistoricWindow(self)
        v.show()

    def export_logs(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Logs", "Logs.csv", "CSV (*.csv)")
        if path:
            with open(path, 'w', encoding='utf-8') as f: f.write(self.terminal.toPlainText())

    def open_help(self):
        modal = HelpWindow(self)
        modal.show()

    def emit_config(self):
        from gui.windows.gui_configuration_window import ConfigWindow
        window = ConfigWindow()
        if window.exec() == QDialog.DialogCode.Accepted:
            self.terminal.log("SISTEMA: Reiniciando config", LogType.WARNING)
            self.terminal.log(f"TAPO: Intentando conectar a {window.config_data['ip']}", LogType.DEBUG)
            self.reconnection_request.emit(window.config_data)

