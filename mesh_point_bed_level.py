from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer


class MeshPointBedLevel(QtWidgets.QFrame):
    valueChanged = pyqtSignal(int, int, float)  # Define the signal
    moveHeadToPosition = pyqtSignal(int, int, float)  # Define the signal

    def __init__(self, row, col, parent=None):
        super(MeshPointBedLevel, self).__init__(parent)

        self.current_value = 0.0

        self.row = row
        self.col = col

        self.setGeometry(0, 0, 129, 96)
        self.setWindowTitle("Frame")

        # Setze den grauen Rahmen
        self.setObjectName("MeshPointBedLevelFrame")
        self.setStyleSheet("#MeshPointBedLevelFrame { border: 4px solid gray; }")

        gridLayout = QtWidgets.QGridLayout(self)
        gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setSpacing(0)

        self.position_label = QtWidgets.QLabel(f"I{col} J{row}", self)
        font = self.position_label.font()
        font.setPointSize(15)
        font.setBold(True)
        self.position_label.setFont(font)
        gridLayout.addWidget(self.position_label, 0, 0, 1, 2)

        self.head_position_indicator_label = QtWidgets.QLabel("", self)
        gridLayout.addWidget(self.head_position_indicator_label, 0, 2)

        self.move_head_to_position_toolButton = QtWidgets.QToolButton(self)
        self.move_head_to_position_toolButton.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        gridLayout.addWidget(self.move_head_to_position_toolButton, 0, 3)
        self.move_head_to_position_toolButton.clicked.connect(self.on_move_head_to_position)

        self.raise_label = QtWidgets.QLabel("raise", self)
        gridLayout.addWidget(self.raise_label, 1, 0)

        self.raise_1_00_toolButton = QtWidgets.QToolButton(self)
        self.raise_1_00_toolButton.setText("1.0")
        self.raise_1_00_toolButton.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        font.setPointSize(8)
        self.raise_1_00_toolButton.setFont(font)
        gridLayout.addWidget(self.raise_1_00_toolButton, 1, 1)

        self.raise_0_10_toolButton = QtWidgets.QToolButton(self)
        self.raise_0_10_toolButton.setText("0.1")
        self.raise_0_10_toolButton.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        self.raise_0_10_toolButton.setFont(font)
        gridLayout.addWidget(self.raise_0_10_toolButton, 1, 2)

        self.raise_0_01_toolButton = QtWidgets.QToolButton(self)
        self.raise_0_01_toolButton.setText("0.01")
        self.raise_0_01_toolButton.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        self.raise_0_01_toolButton.setFont(font)
        gridLayout.addWidget(self.raise_0_01_toolButton, 1, 3)

        self.reset_toolButton = QtWidgets.QToolButton(self)
        self.reset_toolButton.setText("rst")
        self.reset_toolButton.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        gridLayout.addWidget(self.reset_toolButton, 2, 0)

        self.value_doubleSpinBox = QtWidgets.QDoubleSpinBox(self)
        self.value_doubleSpinBox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.value_doubleSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.value_doubleSpinBox.setDecimals(2)
        self.value_doubleSpinBox.setMaximum(10.0)
        self.value_doubleSpinBox.setMinimum(-10.0)
        gridLayout.addWidget(self.value_doubleSpinBox, 2, 1, 1, 3)

        self.lower_label = QtWidgets.QLabel("lower", self)
        gridLayout.addWidget(self.lower_label, 3, 0)

        self.lower_1_00_toolButton = QtWidgets.QToolButton(self)
        self.lower_1_00_toolButton.setText("1.0")
        self.lower_1_00_toolButton.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        self.lower_1_00_toolButton.setFont(font)
        gridLayout.addWidget(self.lower_1_00_toolButton, 3, 1)

        self.lower_0_10_toolButton = QtWidgets.QToolButton(self)
        self.lower_0_10_toolButton.setText("0.1")
        self.lower_0_10_toolButton.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        self.lower_0_10_toolButton.setFont(font)
        gridLayout.addWidget(self.lower_0_10_toolButton, 3, 2)

        self.lower_0_01_toolButton = QtWidgets.QToolButton(self)
        self.lower_0_01_toolButton.setText("0.01")
        self.lower_0_01_toolButton.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        self.lower_0_01_toolButton.setFont(font)
        gridLayout.addWidget(self.lower_0_01_toolButton, 3, 3)

        # Verbinde die Buttons mit den entsprechenden Funktionen
        self.raise_1_00_toolButton.clicked.connect(lambda: self.change_value(1.0))
        self.raise_0_10_toolButton.clicked.connect(lambda: self.change_value(0.1))
        self.raise_0_01_toolButton.clicked.connect(lambda: self.change_value(0.01))
        self.reset_toolButton.clicked.connect(self.on_reset_value)
        self.lower_1_00_toolButton.clicked.connect(lambda: self.change_value(-1.0))
        self.lower_0_10_toolButton.clicked.connect(lambda: self.change_value(-0.1))
        self.lower_0_01_toolButton.clicked.connect(lambda: self.change_value(-0.01))

        self.value_doubleSpinBox.valueChanged.connect(self.on_spinbox_value_changed)

        self.head_is_positioned_here = False

    def update_ui(self):
        spinbox_value = self.value_doubleSpinBox.value()

        if self.head_is_positioned_here:
            if self.current_value > spinbox_value:
                self.setStyleSheet("#MeshPointBedLevelFrame { border: 4px solid red; }")
            elif self.current_value < spinbox_value:
                self.setStyleSheet("#MeshPointBedLevelFrame { border: 4px solid green; }")
            else:
                self.setStyleSheet("#MeshPointBedLevelFrame { border: 4px solid gray; }")

            svg_code = '<svg xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewbox="0 0 474 474"><path d="M138 40h198v118h39v99c-24.437-.125-24.437-.125-32.1-.243-11.236-.526-11.236-.526-21.354 3.358-2.28 2.519-3.924 4.911-5.546 7.885l-2.426 2.926-1.887 2.387c-3.943 4.884-8.137 9.463-12.434 14.033-2.83 3.033-5.444 6.098-7.878 9.466L289 300h-2l-.707 1.672c-1.633 2.94-3.686 5.119-5.98 7.578l-2.735 2.96L275 315a464 464 0 0 0-3.437 3.875l-1.603 1.76c-2.087 2.421-2.087 2.421-4.009 5.559-3.558 5.297-6.913 9.739-13.434 11.04-4.303.504-8.562.504-12.887.351-2.698-.085-5.372-.041-8.07.017-13.136-.008-13.136-.008-17.878-3.968-2.532-2.758-4.612-5.52-6.682-8.634a395 395 0 0 0-4.375-5.375l-2.21-2.742c-3.192-3.811-6.576-7.42-9.973-11.047-3.902-4.19-7.515-8.558-11.098-13.024-2.676-3.21-5.488-6.262-8.344-9.312a244 244 0 0 1-12.77-14.77L156 266l-1.34-1.981c-2.392-3.234-4.268-5.615-8.218-6.762-3.045-.277-6.006-.314-9.063-.257l-2.957-.035c-3.62-.032-7.24.006-10.86.035H99v-99h39zm79 315h40l.188 12.75.082 3.94c.077 10.936-1.867 20.694-6.895 30.435l-1.045 2.048c-7.938 14.925-20.74 23.615-36.518 28.894-6.892 1.664-14.096 1.194-21.142 1.16h-4.97c-4.478.002-8.956-.01-13.435-.024-4.687-.013-9.375-.014-14.062-.016-8.868-.006-17.736-.023-26.603-.043-10.1-.022-20.199-.033-30.298-.043-20.767-.021-41.535-.058-62.302-.101v-39l14.836-.012c16.17-.018 32.338-.062 48.507-.12 9.804-.035 19.608-.06 29.412-.064a5713 5713 0 0 0 25.64-.065c4.524-.02 9.048-.033 13.572-.025q6.393.01 12.785-.042 2.34-.012 4.682.001c11.715.112 11.715.112 21.566-5.673 4.222-4.547 5.108-7.88 5.316-13.98l.116-3.177.13-4.03z" fill="#3b4f7b"/></svg>'

            renderer = QSvgRenderer(bytearray(svg_code, encoding='utf-8'))

            # QPixmap erstellen, in dem das SVG gerendert wird
            pixmap = QPixmap(16, 16)
            pixmap.fill(QtCore.Qt.transparent)  # Transparenter Hintergrund

            # Das SVG auf die Pixmap malen
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            self.head_position_indicator_label.setPixmap(pixmap)

            self.position_label.setStyleSheet("color: black;")

            self.value_doubleSpinBox.setEnabled(True)
            self.reset_toolButton.setEnabled(True)
            self.lower_0_01_toolButton.setEnabled(True)
            self.lower_0_10_toolButton.setEnabled(True)
            self.lower_1_00_toolButton.setEnabled(True)
            self.raise_0_01_toolButton.setEnabled(True)
            self.raise_0_10_toolButton.setEnabled(True)
            self.raise_1_00_toolButton.setEnabled(True)

        else:
            if self.current_value > spinbox_value:
                self.setStyleSheet("#MeshPointBedLevelFrame { border: 4px solid salmon; }")
            elif self.current_value < spinbox_value:
                self.setStyleSheet("#MeshPointBedLevelFrame { border: 4px solid lightgreen; }")
            else:
                self.setStyleSheet("#MeshPointBedLevelFrame { border: 4px solid lightgray; }")

            empty_pixmap = QPixmap(16, 16)
            empty_pixmap.fill(QtCore.Qt.transparent)
            self.head_position_indicator_label.setPixmap(empty_pixmap)

            self.position_label.setStyleSheet("color: darkgrey;")

            self.value_doubleSpinBox.setEnabled(False)
            self.reset_toolButton.setEnabled(False)
            self.lower_0_01_toolButton.setEnabled(False)
            self.lower_0_10_toolButton.setEnabled(False)
            self.lower_1_00_toolButton.setEnabled(False)
            self.raise_0_01_toolButton.setEnabled(False)
            self.raise_0_10_toolButton.setEnabled(False)
            self.raise_1_00_toolButton.setEnabled(False)


    def set_value(self, value):
        """Setzt den Wert der QDoubleSpinBox auf value."""
        self.current_value = round(value, 2)
        self.value_doubleSpinBox.setValue(self.current_value)

    def get_value(self):
        return self.value_doubleSpinBox.value

    def change_value(self, delta):
        """Ändert den Wert der QDoubleSpinBox um delta."""
        spinbox_value = self.value_doubleSpinBox.value()
        new_value = spinbox_value + delta
        self.value_doubleSpinBox.setValue(new_value)

    def on_reset_value(self):
        """Setzt den Wert der QDoubleSpinBox auf 0."""
        self.value_doubleSpinBox.setValue(self.current_value)

    def on_spinbox_value_changed(self, new_value):
        """Slot, der aufgerufen wird, wenn sich der Wert der QDoubleSpinBox ändert."""
        self.update_ui()
        self.valueChanged.emit(self.row, self.col,round(new_value-self.current_value,2))  # Emit the signal

    def on_move_head_to_position(self):
        self.moveHeadToPosition.emit(self.row, self.col, round(self.value_doubleSpinBox.value()-self.current_value,2))

    def set_head_is_positioned_here(self, is_positioned_here):
        """Setzt den Text des Head Position Indicator Labels."""

        self.head_is_positioned_here = is_positioned_here
        self.update_ui()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MeshPointBedLevel()
    window.show()
    sys.exit(app.exec_())