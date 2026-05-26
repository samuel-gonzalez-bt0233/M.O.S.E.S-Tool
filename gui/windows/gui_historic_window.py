import os
from datetime import datetime

import pyqtgraph as pg
from PyQt6.QtGui import QBrush
from PyQt6.QtWidgets import QFileDialog, QDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout

from handlers.models.historic_data_loader import (
    ConsumptionData,
    TrainingMetricsData,
    load_consumption_csv,
    load_training_metrics_csv,
)

# se usa para mostrar el tiempo en el eje x con un formato más legible
class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(value).strftime("%H:%M:%S") for value in values]


class HistoricWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Análisis de Registro Historico")
        self.resize(1000, 650)

        self.consumption_data: ConsumptionData | None = None
        self.metrics_data: TrainingMetricsData | None = None
        self.consumption_csv_path: str | None = None
        self.metrics_csv_path: str | None = None

        self.current_consumption_key = "inst"
        self.metric_names: list[str] = []
        self.current_metric_index = 0

        self.build_ui()
        self.configure_dual_axis()

    def build_ui(self):
        layout = QVBoxLayout(self)

        self.label_files = QLabel("Consumo: -- | Métricas: --")
        self.label_files.setStyleSheet("font-weight: bold; color: #27AE60;")
        layout.addWidget(self.label_files)

        self.plot_item = pg.PlotItem(axisItems={"bottom": TimeAxisItem(orientation="bottom")})
        self.graph = pg.PlotWidget(plotItem=self.plot_item)
        self.graph.setBackground("#FFFFFF")
        self.graph.showGrid(x=True, y=True)
        self.plot_item.hideButtons()
        layout.addWidget(self.graph)

        layout_btns = QHBoxLayout()
        self.btn_load_consumption = QPushButton("Importar Consumo")
        self.btn_load_metrics = QPushButton("Importar Métricas")
        self.btn_toggle_consumption = QPushButton("Ver Acumulado")
        self.btn_prev_metric = QPushButton("Métrica Anterior")
        self.btn_next_metric = QPushButton("Métrica Siguiente")

        layout_btns.addWidget(self.btn_load_consumption)
        layout_btns.addWidget(self.btn_load_metrics)
        layout_btns.addWidget(self.btn_toggle_consumption)
        layout_btns.addWidget(self.btn_prev_metric)
        layout_btns.addWidget(self.btn_next_metric)
        layout.addLayout(layout_btns)

        self.btn_load_consumption.clicked.connect(self.select_consumption_csv)
        self.btn_load_metrics.clicked.connect(self.select_metrics_csv)
        self.btn_toggle_consumption.clicked.connect(self.toggle_consumption_mode)
        self.btn_prev_metric.clicked.connect(self.previous_metric)
        self.btn_next_metric.clicked.connect(self.next_metric)

    def configure_dual_axis(self):
        self.metrics_view = pg.ViewBox()
        self.metrics_view.setZValue(100)
        self.plot_item.showAxis("right")
        self.plot_item.scene().addItem(self.metrics_view)
        self.plot_item.getAxis("right").linkToView(self.metrics_view)
        consumption_view = self.plot_item.getViewBox()
        self.metrics_view.setXLink(consumption_view)
        self.metrics_legend = pg.LegendItem(offset=(-10, 10))
        self.metrics_legend.setParentItem(consumption_view)
        self.metrics_legend.anchor(itemPos=(1, 1), parentPos=(1, 1))
        consumption_view.setMouseEnabled(x=False, y=False)
        self.metrics_view.setMouseEnabled(x=False, y=False)
        consumption_view.sigResized.connect(self.sync_views)
        self.sync_views()

    # solo permitimos zoom del eje Y si hay únicamente UN fichero importado por cuestión de proporcionalidad de ejes, que si no se
    # desajusta demasiado la escala entre ambos y se ve fatal
    def update_zoom_state(self):
        has_consumption = self.consumption_data is not None
        has_metrics = self.metrics_data is not None
        enable_zoom = has_consumption ^ has_metrics

        consumption_view = self.plot_item.getViewBox()
        consumption_view.setMouseEnabled(x=True, y=enable_zoom)
        self.metrics_view.setMouseEnabled(x=True, y=enable_zoom)

    def sync_views(self):
        consumption_view = self.plot_item.getViewBox()
        self.metrics_view.setGeometry(consumption_view.sceneBoundingRect())
        self.metrics_view.linkedViewChanged(consumption_view, self.metrics_view.XAxis)

    def select_consumption_csv(self):
        self.select_csv("Importar CSV de consumo", False)

    def select_metrics_csv(self):
        self.select_csv("Importar CSV de métricas", True)

    def select_csv(self, caption, metrics):
        path, _ = QFileDialog.getOpenFileName(self, caption, "", "CSV (*.csv)")
        if path:
            if metrics:
                self.load_metrics(path)
            else:
                self.load_consumption(path)

    def unload_metrics(self):
        self.metrics_csv_path = None
        self.metrics_data = None
        self.btn_load_metrics.setText("Importar Métricas")
        self.btn_load_metrics.clicked.disconnect(self.unload_metrics)
        self.btn_load_metrics.clicked.connect(self.select_metrics_csv)
        self.refresh()

    def unload_consumption(self):
        self.consumption_csv_path = None
        self.consumption_data = None
        self.btn_load_consumption.setText("Importar Consumo")
        self.btn_load_consumption.clicked.disconnect(self.unload_consumption)
        self.btn_load_consumption.clicked.connect(self.select_consumption_csv)
        self.refresh()

    def load_consumption(self, path: str):
        self.consumption_data = load_consumption_csv(path)
        self.consumption_csv_path = path
        self.btn_load_consumption.setText("Vaciar Consumo")
        self.btn_load_consumption.clicked.disconnect(self.select_consumption_csv)
        self.btn_load_consumption.clicked.connect(self.unload_consumption)
        self.refresh()

    def load_metrics(self, path: str):
        self.metrics_data = load_training_metrics_csv(path)
        self.metrics_csv_path = path
        self.metric_names = list(self.metrics_data.series.keys())
        self.current_metric_index = 0
        self.btn_load_metrics.setText("Vaciar Métricas")
        self.btn_load_metrics.clicked.disconnect(self.select_metrics_csv)
        self.btn_load_metrics.clicked.connect(self.unload_metrics)
        self.refresh()

    def update_labels(self):
        consumption_name = os.path.basename(self.consumption_csv_path) if self.consumption_csv_path else "--"
        metrics_name = os.path.basename(self.metrics_csv_path) if self.metrics_csv_path else "--"
        self.label_files.setText(f"Consumo: {consumption_name} | Metricas: {metrics_name}")

    def toggle_consumption_mode(self):
        self.current_consumption_key = "accum" if self.current_consumption_key == "inst" else "inst"
        self.btn_toggle_consumption.setText("Ver Instantaneo" if self.current_consumption_key == "accum" else "Ver Acumulado")
        self.refresh()

    def next_metric(self):
        if not self.metric_names:
            return
        self.current_metric_index = (self.current_metric_index + 1) % len(self.metric_names)
        self.refresh()

    def previous_metric(self):
        if not self.metric_names:
            return
        self.current_metric_index = (self.current_metric_index - 1) % len(self.metric_names)
        self.refresh()

    def refresh(self):
        self.update_labels()
        self.update_zoom_state()
        self.plot_item.clear()
        self.metrics_view.clear()
        self.metrics_legend.clear()

        use_dual_axis = self.consumption_data is not None and self.metrics_data is not None
        if use_dual_axis:
            self.plot_item.showAxis("right")
            self.plot_item.getAxis("right").linkToView(self.metrics_view)
            self.metrics_view.setXLink(self.plot_item.getViewBox())
        else:
            self.plot_item.hideAxis("right")

        all_x = []
        metrics_x = []

        self.refresh_consumption(all_x)
        self.refresh_metrics(all_x, metrics_x, use_dual_axis)

        self.reset_zoom_to_initial(use_dual_axis)

        self.sync_views()

    def reset_zoom_to_initial(self, use_dual_axis: bool):
        consumption_view = self.plot_item.getViewBox()
        consumption_view.autoRange(padding=0.02)
        if use_dual_axis:
            self.metrics_view.autoRange(padding=0.02)

    def refresh_consumption(self, all_x: list):
        if self.consumption_data:
            series = self.consumption_data.series[self.current_consumption_key]
            x = [ts.timestamp() for ts in series.timestamps]
            y = series.values
            all_x.extend(x)
            color = "#2ECC71" if self.current_consumption_key == "inst" else "#8E44AD"
            self.plot_item.setLabel("left", series.label)
            brush = pg.mkBrush(pg.mkColor(color))
            brush_color = brush.color()
            brush_color.setAlpha(100)
            brush.setColor(brush_color)
            consumption_curve = self.plot_item.plot(
                x,
                y,
                pen=pg.mkPen(color=color, width=1),
                name=series.label,
                fillLevel=0,
                brush=brush,
            )
            consumption_curve.setZValue(-10)
        else:
            self.plot_item.setLabel("left", "Consumo (W)")

    def refresh_metrics(self, all_x: list, metrics_x: list, use_dual_axis: bool):
        if self.metrics_data and self.metric_names:
            metric_name = self.metric_names[self.current_metric_index]
            phase_series = self.metrics_data.series[metric_name]
            if use_dual_axis:
                self.plot_item.setLabel("right", metric_name)
            else:
                self.plot_item.setLabel("left", metric_name)

            colors = {"train": "#3498DB", "val": "#E74C3C", "test": "#F1C40F"}
            for phase, phase_data in phase_series.items():
                x = [ts.timestamp() for ts in phase_data.timestamps]
                y = phase_data.values
                all_x.extend(x)
                metrics_x.extend(x)
                pen = pg.mkPen(color=colors.get(phase, "#34495E"), width=3)
                curve = pg.PlotDataItem(
                    x,
                    y,
                    pen=pen,
                    name=phase,
                    symbol="o",
                    symbolSize=5,
                    symbolBrush=colors.get(phase, "#34495E"),
                    symbolPen=pg.mkPen(color=colors.get(phase, "#34495E"), width=1),
                )
                curve.setZValue(10)
                if use_dual_axis:
                    self.metrics_view.addItem(curve)
                else:
                    self.plot_item.addItem(curve)
                self.metrics_legend.addItem(curve, phase)
        else:
            self.plot_item.setLabel("right", "Métrica")
