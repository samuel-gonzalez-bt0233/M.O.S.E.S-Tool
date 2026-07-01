import os
from datetime import datetime

import pyqtgraph as pg
from PyQt6.QtGui import QBrush
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog, QDialog, QHBoxLayout, QLabel, QMessageBox, 
    QPushButton, QVBoxLayout, QLineEdit
)

from model.historic_data_loader import (
    ConsumptionData,
    TrainingMetricsData,
    load_consumption_csv,
    load_training_metrics_csv,
)

class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strings = []
        for value in values:
            try:
                strings.append(datetime.fromtimestamp(value).strftime("%H:%M:%S"))
            except (ValueError, OSError, OverflowError):
                strings.append("")
        return strings


class HistoricWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Análisis de Registro Histórico")
        self.resize(1100, 700)

        self.consumption_data: ConsumptionData | None = None
        self.metrics_data: TrainingMetricsData | None = None
        self.consumption_csv_path: str | None = None
        self.metrics_csv_path: str | None = None

        self.current_consumption_key = "inst"
        self.metric_names: list[str] = []
        self.current_metric_index = 0

        self.v_line = None 

        self.build_ui()
        self.configure_dual_axis()

    def build_ui(self):
        layout = QVBoxLayout(self)

        self.label_files = QLabel("Consumo: -- | Métricas: --")
        self.label_files.setStyleSheet("font-weight: bold; color: #27AE60;")
        layout.addWidget(self.label_files)
        
        self.label_audit_info = QLabel("Use el panel inferior para buscar hitos por Época o por Hora.")
        self.label_audit_info.setStyleSheet("font-weight: 500; color: #2C3E50; background-color: #ECF0F1; padding: 5px; border-radius: 4px;")
        layout.addWidget(self.label_audit_info)

        self.plot_item = pg.PlotItem(axisItems={"bottom": TimeAxisItem(orientation="bottom")})
        self.graph = pg.PlotWidget(plotItem=self.plot_item)
        self.graph.setBackground("#FFFFFF")
        self.graph.showGrid(x=True, y=True)
        self.plot_item.hideButtons()
        layout.addWidget(self.graph)

        layout_search = QHBoxLayout()
        self.input_epoch = QLineEdit()
        self.input_epoch.setPlaceholderText("Buscar por Época (ej. 20)")
        self.btn_search_epoch = QPushButton("Ir a Época")
        
        self.input_time = QLineEdit()
        self.input_time.setPlaceholderText("Buscar por Hora (ej. 17:59:30)")
        self.btn_search_time = QPushButton("Ir a Hora")

        layout_search.addWidget(QLabel("<b>Buscar Época:</b>"))
        layout_search.addWidget(self.input_epoch)
        layout_search.addWidget(self.btn_search_epoch)
        layout_search.addWidget(QLabel("  |  <b>Buscar Hora:</b>"))
        layout_search.addWidget(self.input_time)
        layout_search.addWidget(self.btn_search_time)
        layout.addLayout(layout_search)

        layout_btns = QHBoxLayout()
        self.btn_load_consumption = QPushButton("Importar Consumo")
        self.btn_load_metrics = QPushButton("Importar Métricas")
        self.btn_toggle_consumption = QPushButton("Ver Consumo")
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
        
        self.btn_search_epoch.clicked.connect(self.search_by_epoch)
        self.btn_search_time.clicked.connect(self.search_by_time)
        self.input_epoch.returnPressed.connect(self.search_by_epoch)
        self.input_time.returnPressed.connect(self.search_by_time)

    def configure_dual_axis(self):
        self.metrics_view = pg.ViewBox()
        self.metrics_view.setZValue(100)
        self.plot_item.scene().addItem(self.metrics_view)
        
        consumption_view = self.plot_item.getViewBox()
        self.metrics_view.setXLink(consumption_view)
        self.metrics_legend = pg.LegendItem(offset=(-10, 10))
        self.metrics_legend.setParentItem(consumption_view)
        self.metrics_legend.anchor(itemPos=(1, 1), parentPos=(1, 1))
        
        consumption_view.setMouseEnabled(x=False, y=False)
        self.metrics_view.setMouseEnabled(x=False, y=False)
        consumption_view.sigResized.connect(self.sync_views)
        self.sync_views()

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
        self.metric_names = []
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
        self.label_files.setText(f"Consumo: {consumption_name} | Métricas: {metrics_name}")

    def toggle_consumption_mode(self):
        self.current_consumption_key = "accum" if self.current_consumption_key == "inst" else "inst"
        self.btn_toggle_consumption.setText("Ver Potencia Activa" if self.current_consumption_key == "accum" else "Ver Consumo Total")
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
        
        self.v_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color="#E74C3C", width=2, style=Qt.PenStyle.DashLine))
        self.plot_item.addItem(self.v_line)
        self.v_line.hide() 

        # Control explícito de la visibilidad y enlace del eje Y secundario
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
            self.plot_item.setLabel("left", "Potencia (W)")

    def refresh_metrics(self, all_x: list, metrics_x: list, use_dual_axis: bool):
        # Solo procesamos y mostramos etiquetas del eje derecho si ambos archivos están cargados
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
            # Si no hay métricas o no se cumple el dual axis, nos aseguramos de limpiar cualquier etiqueta residual de la derecha
            self.plot_item.getAxis("right").setLabel("")

    def search_by_epoch(self):
        if not self.metrics_data or not self.metric_names:
            QMessageBox.warning(self, "Búsqueda", "Primero debe importar un archivo de métricas.")
            return

        text = self.input_epoch.text().strip()
        if not text.isdigit():
            QMessageBox.warning(self, "Búsqueda", "Introduzca un número de época válido.")
            return

        target_epoch = int(text)
        metric_name = self.metric_names[self.current_metric_index]
        phase_series = self.metrics_data.series[metric_name]

        val_train = "N/A"
        val_sub = "N/A"
        target_ts = None

        if "train" in phase_series and target_epoch in phase_series["train"].steps:
            idx_t = phase_series["train"].steps.index(target_epoch)
            val_train = f"{phase_series['train'].values[idx_t]:.4f}"
            target_ts = phase_series["train"].timestamps[idx_t]

        if "val" in phase_series and target_epoch in phase_series["val"].steps:
            idx_v = phase_series["val"].steps.index(target_epoch)
            val_sub = f"{phase_series['val'].values[idx_v]:.4f}"
            if not target_ts:
                target_ts = phase_series["val"].timestamps[idx_v]

        if not target_ts:
            QMessageBox.warning(self, "Búsqueda", f"La época {target_epoch} no existe en este registro.")
            return

        watts_info = "N/A (Cargue CSV consumo)"
        if self.consumption_data:
            c_series = self.consumption_data.series[self.current_consumption_key]
            idx_c = min(range(len(c_series.timestamps)), key=lambda i: abs((c_series.timestamps[i] - target_ts).total_seconds()))
            watts_info = f"{c_series.values[idx_c]:.1f} W"

        self.v_line.setValue(target_ts.timestamp())
        self.v_line.show()
        self.label_audit_info.setText(
            f" <b>Resultado Época {target_epoch}:</b> Hora: {target_ts.strftime('%H:%M:%S')} | "
            f" <b>Train {metric_name}:</b> {val_train} | "
            f" <b>Val {metric_name}:</b> {val_sub} | "
            f" <b>Potencia:</b> {watts_info}"
        )

    def search_by_time(self):
        if not self.metrics_data or not self.metric_names:
            QMessageBox.warning(self, "Búsqueda", "Primero debe importar un archivo de métricas.")
            return

        time_str = self.input_time.text().strip()
        metric_name = self.metric_names[self.current_metric_index]
        phase_series = self.metrics_data.series[metric_name]
        
        any_phase = list(phase_series.keys())[0]
        fecha_base = phase_series[any_phase].timestamps[0].date()

        try:
            target_ts = datetime.strptime(f"{fecha_base} {time_str}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            QMessageBox.warning(self, "Búsqueda", "Formato de hora incorrecto. Use HH:MM:SS (ej. 17:59:30).")
            return
        
        ref_phase = "train" if "train" in phase_series else any_phase
        series_ref = phase_series[ref_phase]
        
        idx_ref = min(range(len(series_ref.timestamps)), key=lambda i: abs((series_ref.timestamps[i] - target_ts).total_seconds()))
        nearest_epoch = series_ref.steps[idx_ref]
        ts_real_registro = series_ref.timestamps[idx_ref]

        val_train = f"{series_ref.values[idx_ref]:.4f}" if ref_phase == "train" else "N/A"
        val_sub = "N/A"

        if "val" in phase_series and nearest_epoch in phase_series["val"].steps:
            idx_v = phase_series["val"].steps.index(nearest_epoch)
            val_sub = f"{phase_series['val'].values[idx_v]:.4f}"
        
        if ref_phase != "train" and "train" in phase_series and nearest_epoch in phase_series["train"].steps:
            idx_t = phase_series["train"].steps.index(nearest_epoch)
            val_train = f"{phase_series['train'].values[idx_t]:.4f}"

        watts_info = "N/A"
        if self.consumption_data:
            c_series = self.consumption_data.series[self.current_consumption_key]
            idx_c = min(range(len(c_series.timestamps)), key=lambda i: abs((c_series.timestamps[i] - target_ts).total_seconds()))
            watts_info = f"{c_series.values[idx_c]:.1f} W"

        self.v_line.setValue(ts_real_registro.timestamp())
        self.v_line.show()
        self.label_audit_info.setText(
            f" <b>Resultado Hora {time_str}:</b> Registro más cercano: {ts_real_registro.strftime('%H:%M:%S')} | "
            f" <b>Época:</b> {nearest_epoch} | "
            f" <b>Train:</b> {val_train} |  <b>Val:</b> {val_sub} | "
            f" <b>Potencia:</b> {watts_info}"
        )