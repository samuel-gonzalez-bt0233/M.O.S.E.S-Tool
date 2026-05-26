import csv
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from core.early_stopping_handler import EarlyStoppingHandler
from core.metrics_dto import MetricsDto


@dataclass
class DataPoint:
    step: int
    step_type: str
    value: float
    timestamp: datetime

BASE_DIR = "Training Metrics"


class MetricsModel:
    def __init__(self):
        self.es_handler = EarlyStoppingHandler()
        self.metrics = {}
        self.metric_order = []
        self.current_index = 0
        self.run_id = None
        self.no_register = True

    def register_metric(self, metrics: MetricsDto):
        phase = metrics.phase

        for v in metrics.values:
            metric = v.value_name

            if metric not in self.metrics:
                self.metrics[metric] = {}
                self.metric_order.append(metric)

            self.metrics[metric].setdefault(phase, [])

            self.metrics[metric][phase].append(
                DataPoint(
                    step=metrics.step,
                    step_type=metrics.step_type,
                    value=v.value,
                    timestamp=metrics.timestamp
                )
            )

            self.save_metrics_log(metric, v.value, metrics)

            self.es_handler.update_phase_state(metric, v.value, phase, metrics.step, metrics.step_type)


    def save_metrics_log(self, val_name: str, value: float, metrics: MetricsDto):

        if self.run_id is None:
            self.run_id = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

        run_dir = f"{BASE_DIR}/{metrics.name}"
        os.makedirs(run_dir, exist_ok=True)

        file_path = f"{run_dir}/{self.run_id}.csv"
        file_exists = os.path.isfile(file_path)

        with open(file_path, 'a', newline='') as f:
            if not file_exists:
                csv.writer(f).writerow(["phase", "step_type", "step", "value_name", "value", "timestamp"])

            csv.writer(f).writerow([metrics.phase, metrics.step_type ,metrics.step, val_name, round(value, 4), metrics.timestamp])



    def get_metric_data(self):
        if not self.metric_order:
            return {}

        metric_name = self.metric_order[self.current_index]
        metric_data = self.metrics[metric_name]

        result = []

        step_type = None

        for phase, points in metric_data.items():
            for p in points:
                result.append({
                    "value": p.value,
                    "step": p.step,
                    "phase": phase
                })

                step_type = p.step_type

        return {
            "metric_name": metric_name,
            "step_type": step_type,
            "data": result
        }

    def get_plot_data(self):
        if not self.metric_order:
            return None

        metric_name = self.metric_order[self.current_index]
        metric_data = self.metrics[metric_name]

        result = {}
        step_type = None

        for phase, points in metric_data.items():
            x = [p.step for p in points]
            y = [p.value for p in points]

            result[phase] = (x, y)

            if points and step_type is None:
                step_type = points[0].step_type

        return metric_name, step_type, result

    def next_metric(self):
        total_metrics = len(self.metrics)
        if not total_metrics == 0:
            self.current_index = (self.current_index + 1) % len(self.metric_order)

    def previous_metric(self):
        total_metrics = len(self.metrics)
        if not total_metrics == 0:
            self.current_index = (self.current_index - 1) % len(self.metric_order)

