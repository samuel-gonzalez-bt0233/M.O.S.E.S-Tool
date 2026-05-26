import csv
import os
from datetime import datetime


class EnergyModel:
    def __init__(self, inst_threshold, accum_threshold, baseline):
        self.inst_threshold = inst_threshold
        self.accum_threshold = accum_threshold
        self.baseline = baseline
        self.last_measurement = 0.0
        self.total_consumption = 0.0
        self.data_y = []
        self.data_accum = []

        # Gestión de carpetas para desacoplar rutas
        os.makedirs("Training Metrics/Consumption Logs", exist_ok=True)
        
        # Nombres de archivos únicos
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        self.csv_file = os.path.join("Training Metrics","Consumption Logs",f"consumption_{timestamp}.csv")

        self._prepare_csv()

    def _prepare_csv(self):
        with open(self.csv_file, 'w', newline='') as f:
            csv.writer(f).writerow(["timestamp", "watts", "accum"])

    def register_measurement(self, value):
        self.last_measurement = value
        self.data_y.append(value)
        if len(self.data_y) > 100: self.data_y.pop(0)
        
        self.total_consumption += value
        self.data_accum.append(self.total_consumption)
        if len(self.data_accum) > 100: self.data_accum.pop(0)
        
        # Guardado automático persistente
        with open(self.csv_file, 'a', newline='') as f:
            csv.writer(f).writerow([datetime.now().isoformat(), round(value, 2), round(self.total_consumption, 2)])


    def reset(self):
        self.data_y, self.data_accum, self.total_consumption = [], [], 0.0