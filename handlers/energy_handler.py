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
    ):
        self._model = model
        self._parent = parent
        self._stack = stack
        self._btn_toggle = btn_toggle
        self._graph_inst = graph_inst
        self._graph_accum = graph_accum
        self._label_watts = label_watts


    def update(self, value: float):
        self._graph_inst.curve.setData(self._model.data_y)
        self._graph_accum.curve.setData(self._model.data_accum)
        self._label_watts.setText(f"{value:.1f} W")

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

