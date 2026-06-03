import pyqtgraph as pg
from PyQt6.QtWidgets import QStackedWidget

from model.metrics_saver import MetricsSaver
from model.metrics_dto import MetricsDto


class MetricsHandler:
    def __init__(
        self,
        model: MetricsSaver,
        stack: QStackedWidget,
        training_container,
        graph_training_metrics,
        btn_toggle,
        btn_training_metrics,
        btn_next_metric,
        btn_prev_metric,
    ):
        self._model = model
        self._stack = stack
        self._training_container = training_container
        self._graph = graph_training_metrics
        self._btn_toggle = btn_toggle

        btn_training_metrics.clicked.connect(self.show_training_metrics_graph)
        btn_next_metric.clicked.connect(self.next_metric)
        btn_prev_metric.clicked.connect(self.previous_metric)

    def show_training_metrics_graph(self):
        if self._stack.currentWidget() is not self._training_container:
            self._stack.setCurrentWidget(self._training_container)
            self._btn_toggle.setText("Vista: Instantáneo")
            self.update_training_graph()

    def update_training_graph(self):
        data = self._model.get_plot_data()
        if not data:
            return

        metric_name, step_type, points = data
        self._graph.clear()

        legend = self._graph.addLegend(offset=(-10, 10))
        legend.anchor(itemPos=(1, 1), parentPos=(1, 1))

        self._graph.setLabel("left", metric_name)
        self._graph.setLabel("bottom", step_type)

        colors = {"train": "#3498DB", "val": "#E74C3C", "test": "#2ECC71"}

        for phase, (x, y) in points.items():
            color = colors.get(phase, "#F1C40F")
            pen = pg.mkPen(color=color, width=3)
            self._graph.plot(x, y, name=phase, pen=pen, symbol="o", symbolSize=5, symbolPen=pen)

    def process_new_training_metrics(self, metrics_dto: MetricsDto):
        self._model.register_metric(metrics_dto)
        if self._stack.currentWidget() is self._training_container:
            self.update_training_graph()

    def next_metric(self):
        self._model.next_metric()
        self.update_training_graph()

    def previous_metric(self):
        self._model.previous_metric()
        self.update_training_graph()
