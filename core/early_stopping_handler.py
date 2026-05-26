from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from styles.config_logs import LogType
from PyQt6.QtWidgets import QMessageBox
from gui.gui_components import EcoTerminal


@dataclass
class PhaseState:
    count: int = 0
    best_value: Optional[float] = None


@dataclass
class Rule:
    window: int
    var_percentage: float
    state: Dict[str, PhaseState] = field(default_factory=dict)
    mode: Literal["inc","dec"] = "inc"


class EarlyStoppingHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.rules = {}
            cls._instance.alert_blocked = False
        return cls._instance

    def add_rule(self, metric: str, rule: Rule):
        self.rules[metric] = rule

    def delete_rule(self, metric: str):
        self.rules.pop(metric)

    def get_rules(self) -> Dict[str, Rule]:
        return self.rules

    def get_rule(self, metric: str) -> Rule | None:
        if metric in self.rules:
            return self.rules[metric]
        else:
            return None

    def update_phase_state(self, metric: str, value: float, phase: Literal["train", "val"], step: int, step_type: str):
        if not metric in self.rules:
            return
        rule = self.rules[metric]
        if phase not in rule.state:
            return

        phase_state = rule.state[phase]

        if phase_state.best_value is None:
            phase_state.best_value = value
            phase_state.count = 0
            return

        if self.value_is_worse_than_best(phase_state.best_value, value, rule.mode) or self.is_insufficient_improvement(phase_state.best_value, value, rule.var_percentage):
            phase_state.count += 1
            if phase_state.count >= rule.window and self.alert_blocked == False:
                self.alert_blocked = True
                EcoTerminal().log(f"[Early Stopping] ⚠ Situación de Early Stoppin: Métrica: {metric}, Fase: {phase}, {step_type}: {step}.", LogType.ALERT)
                from gui.windows.early_stopping_alert_window import EarlyStoppingAlertWindow
                self.alert_window = EarlyStoppingAlertWindow(metric, phase)
                self.alert_window.show()
        else:
            phase_state.count = 0

        self.update_best_value(phase_state.best_value, value, rule.mode)

    def reset_window(self, metric: str, phase: Literal["train", "val"]):
        rule = self.rules[metric]
        phase_state = rule.state[phase]
        phase_state.count = 0

    def is_insufficient_improvement(self, best_value: float, value: float, var_percentage: float) -> bool:
        variation = (abs(best_value-value)/best_value) * 100
        if variation < var_percentage:
            return True
        else:
            return False
    def value_is_worse_than_best(self, best_value: float, value: float, mode: Literal["inc", "dec"]) -> bool:
        if mode == "inc":
            if value < best_value:
                return True
        else:
            if value > best_value:
                return True
        return False


    def update_best_value(self, best_value: float, value: float, mode: Literal["inc", "dec"]):
        if mode == "inc":
            if value > best_value:
                best_value = value
        else:
            if value < best_value:
                best_value = value

    def send_stop_signal(self):
        from core.mqtt_publisher import MqttPublisher
        self.publisher = MqttPublisher()
        self.publisher.ack.connect(self.on_stop_ack)
        self.publisher.send_early_stopping_signal()

    def on_stop_ack(self, success: bool):
        from gui.gui_components import EcoTerminal
        if success:
            EcoTerminal().log("[Early Stopping] Señal de parada enviada correctamente.", LogType.SUCCESS)
        else:
            EcoTerminal().log("[Early Stopping] Error al enviar la señal de parada.", LogType.ERROR)

    def allow_alert(self):
        self.alert_blocked = False

