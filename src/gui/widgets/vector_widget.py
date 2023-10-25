import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit


class VectorWidget(QWidget):
    class VectorCell(QLineEdit):

        value_changed = QtCore.pyqtSignal(int, float)

        def __init__(self, value, cell_id):
            super().__init__()

            self.id = cell_id

            self.setFixedWidth(60)
            self.setAlignment(Qt.AlignLeft)
            self.value = value
            self.setText(str(self.value))
            self.textChanged.connect(self.update_cell_value)

        def update_cell_value(self, text):
            try:
                self.value = float(text)
                self.value_changed.emit(self.id, self.value)
            except ValueError:
                pass

    def __init__(self, label_text="", cell_count=3, initial_values=None):
        super().__init__()

        if len(initial_values) is not cell_count:
            initial_values = [0] * cell_count
            assert True

        self.vector_length = cell_count
        self.cells = []
        self.values = np.zeros(cell_count, dtype=float)

        layout = QHBoxLayout()
        self.setLayout(layout)

        label = QLabel(label_text)
        label.setFixedWidth(50)

        layout.addWidget(label)

        for i in range(cell_count):
            line_edit = self.VectorCell(initial_values[i], i)
            self.values[i] = initial_values[i]
            self.cells.append(line_edit)
            line_edit.value_changed.connect(self.cell_value_changed)
            layout.addWidget(line_edit)

        layout.addStretch()

    def cell_value_changed(self, cell_id, value):
        self.values[cell_id] = value

    def set_values(self, values):
        for i in range(self.vector_length):
            self.cells[i].setText(str(values[i]))
            self.values[i] = values[i]
            self.cells[i].setCursorPosition(0)

