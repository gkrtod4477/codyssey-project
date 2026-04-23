import sys
from decimal import Decimal, InvalidOperation

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGridLayout, QPushButton, QSizePolicy, QVBoxLayout, QWidget, QLabel


class CalculatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_input = "0"
        self.stored_value = None
        self.pending_operator = None
        self.waiting_for_new_input = False

        self.setWindowTitle("iPhone Calculator")
        self.setFixedSize(360, 640)
        self._build_ui()
        self._update_display()

    def _build_ui(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: #111111;
            }
            QLabel {
                color: white;
                background-color: #111111;
                padding: 12px 20px;
            }
            QPushButton {
                border: none;
                border-radius: 38px;
                color: white;
                font-size: 28px;
                min-height: 76px;
                max-height: 76px;
            }
            QPushButton[classType="digit"] {
                background-color: #333333;
            }
            QPushButton[classType="utility"] {
                background-color: #a5a5a5;
                color: black;
            }
            QPushButton[classType="operator"] {
                background-color: #f09a36;
            }
            QPushButton[classType="operator_active"] {
                background-color: white;
                color: #f09a36;
            }
            """
        )

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(16, 24, 16, 16)
        root_layout.setSpacing(12)

        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setFixedHeight(150)
        self.display.setStyleSheet("font-size: 64px; font-weight: 300;")
        root_layout.addWidget(self.display)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)

        button_rows = [
            [("AC", "utility"), ("+/-", "utility"), ("%", "utility"), ("÷", "operator")],
            [("7", "digit"), ("8", "digit"), ("9", "digit"), ("×", "operator")],
            [("4", "digit"), ("5", "digit"), ("6", "digit"), ("-", "operator")],
            [("1", "digit"), ("2", "digit"), ("3", "digit"), ("+", "operator")],
            [("0", "digit"), (".", "digit"), ("=", "operator")],
        ]

        self.operator_buttons = {}

        for row_index, row in enumerate(button_rows):
            column_index = 0
            for text, class_type in row:
                button = QPushButton(text)
                button.setProperty("classType", class_type)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.clicked.connect(self._create_click_handler(text))

                if text in {"+", "-", "×", "÷", "="}:
                    self.operator_buttons[text] = button

                if text == "0":
                    button.setStyleSheet("text-align: left; padding-left: 30px;")
                    grid_layout.addWidget(button, row_index, column_index, 1, 2)
                    column_index += 2
                else:
                    grid_layout.addWidget(button, row_index, column_index)
                    column_index += 1

        root_layout.addLayout(grid_layout)
        self.setLayout(root_layout)

    def _create_click_handler(self, value):
        def handler():
            if value.isdigit():
                self._input_digit(value)
            elif value == ".":
                self._input_decimal()
            elif value in {"+", "-", "×", "÷"}:
                self._set_operator(value)
            elif value == "=":
                self._calculate_result()
            elif value == "AC":
                self._clear_all()
            elif value == "+/-":
                self._toggle_sign()
            elif value == "%":
                self._apply_percent()

        return handler

    def _input_digit(self, digit):
        if self.waiting_for_new_input:
            self.current_input = digit
            self.waiting_for_new_input = False
        elif self.current_input == "0":
            self.current_input = digit
        else:
            self.current_input += digit

        self._update_display()

    def _input_decimal(self):
        if self.waiting_for_new_input:
            self.current_input = "0."
            self.waiting_for_new_input = False
        elif "." not in self.current_input:
            self.current_input += "."

        self._update_display()

    def _set_operator(self, operator):
        if self.current_input == "Error":
            return

        if self.pending_operator and not self.waiting_for_new_input:
            self._calculate_result()

        self.stored_value = self._to_decimal(self.current_input)
        self.pending_operator = operator
        self.waiting_for_new_input = True
        self._refresh_operator_styles()

    def _calculate_result(self):
        if self.pending_operator is None or self.stored_value is None:
            self._refresh_operator_styles()
            return

        current_value = self._to_decimal(self.current_input)

        try:
            if self.pending_operator == "+":
                result = self.stored_value + current_value
            elif self.pending_operator == "-":
                result = self.stored_value - current_value
            elif self.pending_operator == "×":
                result = self.stored_value * current_value
            else:
                if current_value == 0:
                    self.current_input = "Error"
                    self.stored_value = None
                    self.pending_operator = None
                    self.waiting_for_new_input = True
                    self._update_display()
                    self._refresh_operator_styles()
                    return
                result = self.stored_value / current_value
        except InvalidOperation:
            self.current_input = "Error"
            self.stored_value = None
            self.pending_operator = None
            self.waiting_for_new_input = True
            self._update_display()
            self._refresh_operator_styles()
            return

        self.current_input = self._format_decimal(result)
        self.stored_value = result
        self.pending_operator = None
        self.waiting_for_new_input = True
        self._update_display()
        self._refresh_operator_styles()

    def _clear_all(self):
        self.current_input = "0"
        self.stored_value = None
        self.pending_operator = None
        self.waiting_for_new_input = False
        self._update_display()
        self._refresh_operator_styles()

    def _toggle_sign(self):
        if self.current_input in {"0", "Error"}:
            return

        if self.current_input.startswith("-"):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = f"-{self.current_input}"

        self._update_display()

    def _apply_percent(self):
        if self.current_input == "Error":
            return

        value = self._to_decimal(self.current_input) / Decimal("100")
        self.current_input = self._format_decimal(value)
        self._update_display()

    def _to_decimal(self, value):
        return Decimal(value)

    def _format_decimal(self, value):
        normalized = format(value.normalize(), "f")
        if "." in normalized:
            normalized = normalized.rstrip("0").rstrip(".")
        return normalized or "0"

    def _update_display(self):
        self.display.setText(self.current_input)

    def _refresh_operator_styles(self):
        for operator, button in self.operator_buttons.items():
            class_type = "operator_active" if operator == self.pending_operator else "operator"
            button.setProperty("classType", class_type)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()


def main():
    app = QApplication(sys.argv)
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
