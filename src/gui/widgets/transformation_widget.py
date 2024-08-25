import numpy as np
from PySide6 import QtCore
from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QDoubleValidator, QGuiApplication
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, \
    QTableWidget, QGridLayout, QLineEdit, QPushButton, QSizePolicy
import src.utils.graphics_utils as graphic_util
from src.gui.widgets.custom_push_button import CustomPushButton


class Transformation3DPicker(QWidget):
    class MatrixCell(QLineEdit):
        cell_number = 0

        value_changed = QtCore.Signal(int, int, float)
        matrix_copied = QtCore.Signal(np.ndarray)

        def __init__(self, value=0.0):
            super().__init__()

            locale = QLocale(QLocale.Language.C)
            double_validator = QDoubleValidator()
            double_validator.setLocale(locale)
            double_validator.setRange(-9999.0, 9999.0)
            double_validator.setDecimals(10)

            self.row = int(Transformation3DPicker.MatrixCell.cell_number / 4)
            self.col = self.cell_number % 4
            Transformation3DPicker.MatrixCell.cell_number += 1

            self.setFixedSize(50, 50)
            self.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.value = value
            self.setText(str(self.value))
            self.setValidator(double_validator)
            self.textEdited.connect(self.update_cell_value)

        def update_cell_value(self, text):
            try:
                self.value = float(text)
                self.value_changed.emit(self.row, self.col, self.value)
            except ValueError:
                pass

        def keyPressEvent(self, event):
            if event.key() == Qt.Key.Key_V and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                clipboard = QGuiApplication.clipboard()
                text_original = clipboard.text()
                try:
                    text = text_original.replace("\n", "").replace("[", "").replace("]", "")
                    new_matrix = np.fromstring(text, dtype=np.float32, sep=',')
                    self.matrix_copied.emit(new_matrix.reshape(4, 4))
                except ValueError:
                    pass

            super().keyPressEvent(event)

    transformation_matrix_changed = QtCore.Signal(object)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        label = QLabel("Transformation matrix")
        label.setStyleSheet(
            """QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding-bottom: 0.5em;
            }"""
        )

        self.matrix_table = QTableWidget(4, 4)

        self.matrix_widget = QWidget()
        grid_layout = QGridLayout(self.matrix_widget)

        self.cells = []
        self.transformation_matrix = np.array([[1, 0, 0, 0],
                                               [0, 1, 0, 0],
                                               [0, 0, 1, 0],
                                               [0, 0, 0, 1]], dtype=float)

        for iRow in range(4):
            for iCol in range(4):
                cell = self.MatrixCell(self.transformation_matrix[iRow, iCol])
                cell.value_changed.connect(self.cell_value_changed)
                cell.matrix_copied.connect(self.set_transformation)
                grid_layout.addWidget(cell, iRow, iCol)
                self.cells.append(cell)

        button_reset = CustomPushButton("Reset transformation matrix", 90)
        button_reset.connect_to_clicked(lambda: self.set_transformation(np.eye(4)))

        button_copy = CustomPushButton("Copy to clipboard", 90)
        button_copy.connect_to_clicked(self.copy_to_clipboard)

        layout.addWidget(label)
        layout.addWidget(self.matrix_widget)
        layout.addWidget(button_reset)
        layout.addWidget(button_copy)
        layout.addStretch()

    def cell_value_changed(self, row, col, value):
        self.transformation_matrix[row, col] = value
        self.transformation_matrix_changed.emit(self.transformation_matrix)

    def set_transformation(self, transformation_matrix):
        for cell in self.cells:
            self.transformation_matrix[cell.row][cell.col] = transformation_matrix[cell.row][cell.col]
            value = transformation_matrix[cell.row][cell.col]
            cell.setText(str(value))
            cell.setCursorPosition(0)

        self.transformation_matrix_changed.emit(self.transformation_matrix)

    def copy_to_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(str(self.transformation_matrix.tolist()))
