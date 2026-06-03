from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class MetricsValue:
    value: float
    # EJ: RMSE, R2, ...
    value_name: str


@dataclass
class MetricsDto:
    name: str #NAME OF THE TRAINING
    timestamp: datetime
    step: int                            
    step_type: str #EPOCH, BATCH, ITERATION, ...                      
    phase: Literal["train", "val"]
    values: list[MetricsValue]

    def __post_init__(self):
        #AUTOMATICATICALLY DESERIALIZES THE DICTIONARY TO METRICSVALUE TYPE
        self.values = [
            MetricsValue(**v) if isinstance(v, dict) else v
            for v in self.values
        ]
