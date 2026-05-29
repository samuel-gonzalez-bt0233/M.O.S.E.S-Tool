import csv
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SeriesData:
    label: str
    timestamps: list[datetime]
    values: list[float]


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
            watts.append(float(row["watts"]))
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

            timestamp = datetime.fromisoformat(row[timestamp_col])

            if value_name not in series:
                series[value_name] = {}

            if phase not in series[value_name]:
                series[value_name][phase] = SeriesData(
                    label=f"{value_name}",
                    timestamps=[],
                    values=[],
                )

            series[value_name][phase].timestamps.append(timestamp)
            series[value_name][phase].values.append(value)

    return TrainingMetricsData(
        file_path=file_path,
        series=series,
    )