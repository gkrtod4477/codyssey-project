import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget


class Calculator:
    MAX_ABS_VALUE = Decimal("999999999999")
    MAX_DISPLAY_LENGTH = 12
    ROUNDING_PRECISION = Decimal("0.000001")

    def __init__(self):
        self.reset()

    def reset(self):
        self.current_input = "0"
        self.left_operand = None
        self.pending_operator = None
        self.waiting_for_new_input = False
        self.last_error = None
        return self.current_input

    def input_digit(self, digit):
        if self.last_error:
            self.reset()

        if self.waiting_for_new_input:
            self.current_input = digit
            self.waiting_for_new_input = False
        elif self.current_input == "0":
            self.current_input = digit
        else:
            self.current_input += digit

        return self.current_input

    def input_decimal(self):
        if self.last_error:
            self.reset()

        if self.waiting_for_new_input:
            self.current_input = "0."
            self.waiting_for_new_input = False
        elif "." not in self.current_input:
            self.current_input += "."

        return self.current_input

    def set_operator(self, operator):
        if self.last_error:
            return self.current_input

        if self.pending_operator and not self.waiting_for_new_input:
            result = self.equal()
            if self.last_error:
                return result

        self.left_operand = self._parse_decimal(self.current_input)
        self.pending_operator = operator
        self.waiting_for_new_input = True
        return self.current_input

    def add(self, left, right):
        return left + right

    def subtract(self, left, right):
        return left - right

    def multiply(self, left, right):
        return left * right

    def divide(self, left, right):
        if right == 0:
            raise ZeroDivisionError
        return left / right

    def negative_positive(self):
        if self.last_error:
            return self.current_input

        if self.current_input == "0":
            return self.current_input

        if self.current_input.startswith("-"):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = f"-{self.current_input}"

        return self.current_input

    def percent(self):
        if self.last_error:
            return self.current_input

        try:
            value = self._parse_decimal(self.current_input) / Decimal("100")
            self.current_input = self._prepare_display(value)
        except OverflowError:
            self._set_error("Overflow")
        except InvalidOperation:
            self._set_error("Error")

        return self.current_input

    def equal(self):
        if self.last_error:
            return self.current_input

        if self.pending_operator is None or self.left_operand is None:
            return self.current_input

        right_operand = self._parse_decimal(self.current_input)

        try:
            if self.pending_operator == "+":
                result = self.add(self.left_operand, right_operand)
            elif self.pending_operator == "-":
                result = self.subtract(self.left_operand, right_operand)
            elif self.pending_operator == "x":
                result = self.multiply(self.left_operand, right_operand)
            else:
                result = self.divide(self.left_operand, right_operand)

            self.current_input = self._prepare_display(result)
            self.left_operand = self._parse_decimal(self.current_input)
            self.pending_operator = None
            self.waiting_for_new_input = True
        except ZeroDivisionError:
            self._set_error("Cannot divide by 0")
        except OverflowError:
            self._set_error("Overflow")
        except InvalidOperation:
            self._set_error("Error")

        return self.current_input

    def _parse_decimal(self, value):
        return Decimal(value)

    def _prepare_display(self, value):
        if value.copy_abs() > self.MAX_ABS_VALUE:
            raise OverflowError

        rounded = value.quantize(self.ROUNDING_PRECISION, rounding=ROUND_HALF_UP)
        if rounded == rounded.to_integral():
            display = str(rounded.quantize(Decimal("1")))
        else:
            display = format(rounded.normalize(), "f").rstrip("0").rstrip(".")

        if display in {"-0", ""}:
            display = "0"

        if len(display.replace("-", "")) > 1 and len(display) > self.MAX_DISPLAY_LENGTH:
            raise OverflowError

        return display

    def _set_error(self, message):
        self.current_input = message
        self.left_operand = None
        self.pending_operator = None
        self.waiting_for_new_input = True
        self.last_error = message


class CalculatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.calculator = Calculator()
        self.operator_buttons = {}

        self.setWindowTitle("Calculator")
        self.setFixedSize(360, 640)
        self._build_ui()
        self._update_display(self.calculator.current_input)

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
        self.display.setWordWrap(False)
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

        for row_index, row in enumerate(button_rows):
            column_index = 0
            for text, class_type in row:
                button = QPushButton(text)
                button.setProperty("classType", class_type)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.clicked.connect(self._create_click_handler(text))

                if text in {"+", "-", "×", "÷"}:
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
                display_value = self.calculator.input_digit(value)
            elif value == ".":
                display_value = self.calculator.input_decimal()
            elif value in {"+", "-", "×", "÷"}:
                operator_map = {"×": "x", "÷": "/"}
                display_value = self.calculator.set_operator(operator_map.get(value, value))
            elif value == "=":
                display_value = self.calculator.equal()
            elif value == "AC":
                display_value = self.calculator.reset()
            elif value == "+/-":
                display_value = self.calculator.negative_positive()
            else:
                display_value = self.calculator.percent()

            self._update_display(display_value)
            self._refresh_operator_styles(value)

        return handler

    def _update_display(self, value):
        self.display.setText(value)

        font_size = 64
        length = len(value)
        if length > 12:
            font_size = 28
        elif length > 10:
            font_size = 34
        elif length > 8:
            font_size = 42
        elif length > 6:
            font_size = 50

        self.display.setFont(QFont("Arial", font_size, QFont.Light))

    def _refresh_operator_styles(self, clicked_value=None):
        active_symbol = None
        if self.calculator.pending_operator == "x":
            active_symbol = "×"
        elif self.calculator.pending_operator == "/":
            active_symbol = "÷"
        else:
            active_symbol = self.calculator.pending_operator

        if clicked_value in {"=", "AC"} or self.calculator.last_error:
            active_symbol = None

        for operator, button in self.operator_buttons.items():
            class_type = "operator_active" if operator == active_symbol else "operator"
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
