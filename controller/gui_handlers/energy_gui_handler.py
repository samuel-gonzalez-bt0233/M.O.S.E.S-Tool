from PyQt6.QtWidgets import QMessageBox, QStackedWidget
from styles.config_logs import LogType
from model.energy_saver import EnergySaver
from gui.components.graph import Graph
from gui.components.terminal import Terminal


class EnergyHandler:
    def __init__(
        self,
        model: EnergySaver,
        parent,
        stack: QStackedWidget,
        btn_toggle,
        graph_inst: Graph,
        graph_accum: Graph,
        label_watts,
        terminal: Terminal
    ):
        self._model = model
        self._parent = parent
        self._stack = stack
        self._btn_toggle = btn_toggle
        self._graph_inst = graph_inst
        self._graph_accum = graph_accum
        self._label_watts = label_watts
        self._terminal = terminal


    def update(self, value: float):
        self._graph_inst.curve.setData(self._model.data_y)
        self._graph_accum.curve.setData(self._model.data_accum)
        self._label_watts.setText(f"{value:.1f} W")

    def reset(self):
        self._model.reset()
        self._graph_inst.curve.setData([])
        self._graph_accum.curve.setData([])
        self._terminal.log("SISTEMA: Datos reseteados.", LogType.INFO)

    def toggle_graph(self):
        if self._stack.currentWidget() is self._graph_inst:
            self._stack.setCurrentWidget(self._graph_accum)
            self._btn_toggle.setText("Vista: Acumulado")
        else:
            self._stack.setCurrentWidget(self._graph_inst)
            self._btn_toggle.setText("Vista: Instantáneo")

