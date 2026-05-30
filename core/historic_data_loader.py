import csv
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SeriesData:
    label: str
    timestamps: list[datetime]
    values: list[float]
    # Añadimos 'steps' como opcional para no romper el CSV de consumo
    steps: list[int] = field(default_factory=list)


@dataclass
class ConsumptionData:
    file_path: str
    series: dict[str, SeriesData]

@dataclass
class TrainingMetricsData:
    file_path: str
    series: dict[str, dict[str, SeriesData]]


def load_consumption_csv(file_path: str) -> ConsumptionData:
    watts: list[float] = []
    accum: list[float] = []
    timestamps: list[datetime] = []

    with open(file_path, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise ValueError("CSV de consumo sin cabecera")

        accum_col = "accum"
        watts_col = "watts"
        timestamp_col = "timestamp"

        required_cols = {watts_col, accum_col, timestamp_col}

        if not required_cols.issubset(reader.fieldnames):
            raise ValueError("Cabeceras de consumo inválidas.")

        for row in reader:
            timestamps.append(datetime.fromisoformat(row[timestamp_col]))
            watts.append(float(row[watts_col]))
            accum.append(float(row[accum_col]))

    series = {
        "inst": SeriesData(
            label="Consumo Instantáneo (W)",
            timestamps=timestamps,
            values=watts,
        ),
        "accum": SeriesData(
            label="Consumo Acumulado (W)",
            timestamps=timestamps,
            values=accum,
        )
    }

    return ConsumptionData(file_path=file_path, series=series)


def load_training_metrics_csv(file_path: str) -> TrainingMetricsData:
    series: dict[str, dict[str, SeriesData]] = {}

    with open(file_path, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        if not reader.fieldnames:
            raise ValueError("CSV de métricas de entrenamiento sin cabecera")

        phase_col = "phase"
        step_col = "step"
        step_type_col = "step_type"
        value_name_col = "value_name"
        value_col = "value"
        timestamp_col = "timestamp"

        required_cols = {
            phase_col,
            step_col,
            step_type_col,
            value_name_col,
            value_col,
            timestamp_col,
        }

        if not required_cols.issubset(reader.fieldnames):
            raise ValueError("Cabeceras de métricas de entrenamiento inválidas.")

        for row in reader:
            phase = row[phase_col]
            value_name = row[value_name_col]
            value = float(row[value_col])
            step = int(row[step_col]) # <--- CAPTURAMOS EL STEP (ÉPOCA)
            timestamp = datetime.fromisoformat(row[timestamp_col])

            if value_name not in series:
                series[value_name] = {}

            if phase not in series[value_name]:
                series[value_name][phase] = SeriesData(
                    label=f"{value_name}",
                    timestamps=[],
                    values=[],
                    steps=[] # <--- INICIALIZAMOS LA LISTA DE ÉPOCAS
                )

            series[value_name][phase].timestamps.append(timestamp)
            series[value_name][phase].values.append(value)
            series[value_name][phase].steps.append(step) # <--- GUARDAMOS LA ÉPOCA

    return TrainingMetricsData(file_path=file_path, series=series)


# =====================================================================
# NUEVA LÓGICA DE BÚSQUEDA BIDIRECCIONAL (INDEXACIÓN CRUZADA)
# =====================================================================

def buscar_timestamp_por_epoca(metrics_data: TrainingMetricsData, target_epoch: int, value_name: str = "Inertia", phase: str = "train") -> datetime | None:
    """Dado un número de época (step), devuelve su timestamp exacto."""
    if value_name not in metrics_data.series or phase not in metrics_data.series[value_name]:
        return None
    
    series_data = metrics_data.series[value_name][phase]
    
    # Buscamos la posición de la época en la lista
    if target_epoch in series_data.steps:
        idx = series_data.steps.index(target_epoch)
        return series_data.timestamps[idx]
    
    return None


def buscar_epoca_por_timestamp(metrics_data: TrainingMetricsData, target_ts: datetime, value_name: str = "Inertia", phase: str = "train") -> tuple[int, float, datetime] | None:
    """Dado un timestamp, encuentra la época del modelo más cercana temporalmente."""
    if value_name not in metrics_data.series or phase not in metrics_data.series[value_name]:
        return None
    
    series_data = metrics_data.series[value_name][phase]
    if not series_data.timestamps:
        return None
    
    # Encontramos el índice del timestamp con la diferencia absoluta mínima (Vecino más cercano)
    idx_cercano = min(
        range(len(series_data.timestamps)),
        key=lambda i: abs((series_data.timestamps[i] - target_ts).total_seconds())
    )
    
    epoch = series_data.steps[idx_cercano]
    valor = series_data.values[idx_cercano]
    ts_real = series_data.timestamps[idx_cercano]
    
    return epoch, valor, ts_real