from PyQt6.QtWidgets import QMessageBox, QStackedWidget
from styles.config_logs import LogType
from handlers.models.energy_model import EnergyModel
from gui.gui_components import EcoGraph, EcoTerminal


class EnergyHandler:
    def __init__(
        self,
        model: EnergyModel,
        parent,
        stack: QStackedWidget,
        btn_toggle,
        graph_inst: EcoGraph,
        graph_accum: EcoGraph,
        label_watts,
        input_inst_threshold,
        input_accum_threshold,
        input_baseline,
    ):
        self._model = model
        self._parent = parent
        self._stack = stack
        self._btn_toggle = btn_toggle
        self._graph_inst = graph_inst
        self._graph_accum = graph_accum
        self._label_watts = label_watts
        self._warning_inst_blocked = False
        self._warning_accum_blocked = False

        input_inst_threshold.textChanged.connect(self._on_inst_threshold_changed)
        input_accum_threshold.textChanged.connect(self._on_accum_threshold_changed)
        input_baseline.textChanged.connect(self._on_baseline_changed)

    def update(self, value: float):
        self._graph_inst.curve.setData(self._model.data_y)
        self._graph_accum.curve.setData(self._model.data_accum)
        self._label_watts.setText(f"{value:.1f} W")
        self._manage_warnings(value)

    def reset(self):
        self._model.reset()
        self._graph_inst.curve.setData([])
        self._graph_accum.curve.setData([])
        EcoTerminal().log("SISTEMA: Datos reseteados.", LogType.DEBUG)

    def toggle_graph(self):
        if self._stack.currentWidget() is self._graph_inst:
            self._stack.setCurrentWidget(self._graph_accum)
            self._btn_toggle.setText("Vista: Acumulado")
        else:
            self._stack.setCurrentWidget(self._graph_inst)
            self._btn_toggle.setText("Vista: Instantáneo")

    def _on_inst_threshold_changed(self, text: str):
        try:
            self._model.inst_threshold = float(text)
            self._graph_inst.threshold_line.setPos(self._model.inst_threshold)
        except ValueError:
            pass

    def _on_accum_threshold_changed(self, text: str):
        try:
            self._model.accum_threshold = float(text)
            self._graph_accum.threshold_line.setPos(self._model.accum_threshold)
        except ValueError:
            pass

    def _on_baseline_changed(self, text: str):
        try:
            self._model.baseline = float(text)
            if self._graph_inst.baseline_line is not None:
                self._graph_inst.baseline_line.setPos(self._model.baseline)
        except ValueError:
            pass

    def _manage_warnings(self, value: float):
        color = "#E74C3C" if value > self._model.inst_threshold else "#2ECC71"
        self._label_watts.setStyleSheet(f"font-size: 42px; font-weight: 800; color: {color};")

        if value > self._model.inst_threshold and not self._warning_inst_blocked:
            EcoTerminal().log(f"ALERTA INST: {value:.1f} W superados", LogType.ERROR)
            QMessageBox.warning(self._parent, "ALERTA POTENCIA", f"Potencia excesiva: {value:.1f} W")
            self._warning_inst_blocked = True
        elif value <= self._model.inst_threshold:
            self._warning_inst_blocked = False

        if self._model.total_consumption > self._model.accum_threshold and not self._warning_accum_blocked:
            EcoTerminal().log(f"ALERTA ACUM: {self._model.total_consumption:.1f} alcanzado", LogType.ACUM)
            QMessageBox.warning(self._parent, "ALERTA ENERGÍA", f"Límite acumulado alcanzado: {self._model.total_consumption:.1f}")
            self._warning_accum_blocked = True
