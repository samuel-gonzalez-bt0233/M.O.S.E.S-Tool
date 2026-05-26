from statistics import mode
from typing import Literal

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QScrollArea, QWidget, QGridLayout, QFrame, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt

from core.early_stopping_handler import EarlyStoppingHandler, PhaseState, Rule
from styles.hint import Hint


class EarlyStoppingConfigWindow(QDialog):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    modes = {
        "Creciente": "inc",
        "Decreciente": "dec",
    }

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__()

        self.handler = EarlyStoppingHandler()

        self.setWindowTitle("Configuración Early Stopping")
        self.setFixedSize(460, 540)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        # --- Formulario ---
        main_layout.addWidget(QLabel("<b><u>Añadir regla</u></b>"))
        rule_info_label = QLabel("Añade las reglas para las métricas sobre las que desees identificar situaciones de Early Stopping. En caso de detectarse tnedrás la opción de parar el entrenamiento.")
        rule_info_label.setWordWrap(True)
        main_layout.addWidget(rule_info_label)

        creation_grid = QGridLayout()
        
        creation_grid.addWidget(QLabel("Nombre de la métrica:"),0,0)
        self.input_metric = QLineEdit()
        self.input_metric.setPlaceholderText("ej: val_loss, accuracy...")
        creation_grid.addWidget(self.input_metric,0,1,1,2)
        creation_grid.addWidget(Hint("metric_name"),0,3)

        creation_grid.addWidget(QLabel("Tendencia de la métrica:"),1,0)
        self.dropdown_mode = QComboBox()
        self.dropdown_mode.addItems(["Creciente", "Decreciente"])
        creation_grid.addWidget(self.dropdown_mode,1,1,1,2)
        creation_grid.addWidget(Hint("tendency"),1,3)
        

        creation_grid.addWidget(QLabel("Ventana de alerta:"),2,0)
        self.input_window = QLineEdit()
        self.input_window.setPlaceholderText("ej: 5")
        creation_grid.addWidget(self.input_window,3,0)
        creation_grid.addWidget(Hint("es_window"),3,1)

        creation_grid.addWidget(QLabel("Variación mínima (%):"),2,2)
        self.input_pct = QLineEdit()
        self.input_pct.setPlaceholderText("ej: 1.5")
        creation_grid.addWidget(self.input_pct,3,2)
        creation_grid.addWidget(Hint("min_var"),3,3)

        creation_grid.addWidget(QLabel("Fases:"),4,0)
        self.check_train = QCheckBox("Entrenamiento")
        self.check_val = QCheckBox("Validación")
        phases_row = QHBoxLayout()
        phases_row.addWidget(self.check_train)
        phases_row.addWidget(self.check_val)
        creation_grid.addLayout(phases_row,5,0)
        creation_grid.addWidget(Hint("train_mode"),4,3)

        main_layout.addLayout(creation_grid)

        self.btn_add = QPushButton("+ Añadir regla")
        self.btn_add.clicked.connect(self.add_rule)
        main_layout.addWidget(self.btn_add)


        # --- Separador ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # --- Lista de reglas ---
        main_layout.addWidget(QLabel("<b><u>Reglas configuradas:<u></b>"))

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(180)

        rules_container = QWidget()
        self.rules_layout = QVBoxLayout(rules_container)
        self.rules_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.rules_layout.setSpacing(4)

        self.empty_label = QLabel("Sin reglas configuradas.")
        self.empty_label.setStyleSheet("color: #999; font-style: italic;")
        self.rules_layout.addWidget(self.empty_label)

        scroll_area.setWidget(rules_container)
        main_layout.addWidget(scroll_area)

        # --- Guardar ---
        self.btn_save = QPushButton("Confirmar")
        self.btn_save.clicked.connect(self.close)
        main_layout.addWidget(self.btn_save)


    def add_rule(self):
        result = self.validate_fields()
        if result is None:
            return

        metric, window, percentage, phases, mode = result
        rule = Rule(window=window, var_percentage=percentage, state={p: PhaseState() for p in phases}, mode=mode)
        if self.handler.get_rule(metric):
            QMessageBox.warning(self, "Error de validación", f"Ya existe una regla para {metric}.")
            return
        self.handler.add_rule(metric, rule)
        self._add_rule_row(metric, rule)
        self.input_metric.clear()
        self.input_window.clear()
        self.input_pct.clear()
        self.check_train.setChecked(False)
        self.check_val.setChecked(False)

    def validate_fields(self):
        metric = self.input_metric.text().strip()
        window_text = self.input_window.text().strip()
        percentage_text = self.input_pct.text().strip()

        errors = []
        if not metric:
            errors.append("El nombre de la métrica no puede estar vacío.")

        window = None
        if not window_text:
            errors.append("La ventana de alerta no puede estar vacía.")
        else:
            try:
                window = int(window_text)
                if window <= 0:
                    errors.append("La ventana de alerta debe ser un entero positivo.")
            except ValueError:
                errors.append("La ventana de alerta debe ser un número entero.")

        percentage = None
        if not percentage_text:
            errors.append("La mejora mínima no puede estar vacía.")
        else:
            try:
                percentage = float(percentage_text.replace(',', '.'))
                if percentage < 0:
                    errors.append("La variación mínima debe ser un valor positivo.")
            except ValueError:
                errors.append("La variación mínima debe ser un número decimal.")

        phases = []
        if self.check_train.isChecked():
            phases.append("train")
        if self.check_val.isChecked():
            phases.append("val")
        if not phases:
            errors.append("Selecciona al menos una fase (Entrenamiento o Validación).")

        mode_text = self.dropdown_mode.currentText()
        mode = self.modes[mode_text]

        if errors:
            QMessageBox.warning(self, "Error de validación", "\n".join(errors))
            return

        return metric, window, percentage, phases, mode

    def _add_rule_row(self, metric: str, rule: Rule):
        self.empty_label.setVisible(False)

        phases_str = ", ".join(rule.state.keys())
        label = QLabel(f"{metric} | Tendencia: {rule.mode} | Ventana: {rule.window} | Variación: {rule.var_percentage}% | Fases: {phases_str}")
        label.setWordWrap(True)

        btn_edit = QPushButton("Editar")
        btn_edit.setFixedWidth(55)

        btn_delete = QPushButton("Eliminar")
        btn_delete.setFixedWidth(55)



        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(label)
        row_layout.addWidget(btn_edit)
        row_layout.addWidget(btn_delete)


        btn_delete.clicked.connect(lambda: self._remove_rule_row(metric, row_widget))
        btn_edit.clicked.connect(lambda: self.edit_rule(metric, row_widget))
        self.rules_layout.addWidget(row_widget)

    def _remove_rule_row(self, metric: str, widget: QWidget):
        self.handler.delete_rule(metric)
        widget.deleteLater()
        if not self.handler.rules:
            self.empty_label.setVisible(True)

    def edit_rule(self, metric: str, widget: QWidget):
        rule = self.handler.get_rule(metric)
        if rule is not None:
            self.input_metric.setText(metric)
            self.input_window.setText(f"{rule.window}")
            self.input_pct.setText(f"{rule.var_percentage}")
            self.check_train.setChecked(rule.state.__contains__("train"))
            self.check_val.setChecked(rule.state.__contains__("val"))
            self.dropdown_mode.setCurrentIndex(self.get_mode_index(rule.mode))
            self._remove_rule_row(metric, widget)

    def get_mode_index(self, mode: Literal["inc", "dec"]):
        if mode == "inc":
            return 0
        else:
            return 1