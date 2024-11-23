from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.uic.Compiler.qtproxies import QtCore

from mesh_point_bed_level import MeshPointBedLevel
from PyQt5.QtCore import pyqtSignal

class MeshPointGrid(QWidget):
    """
    Widget-Klasse für ein 5x5-Gitter von MeshPointBedLevel-Widgets.
    """
    moveHeadToPosition = pyqtSignal(int, int, float)  # Signal für "Move Head" Button
    valueChanged = pyqtSignal(int, int, float)  # Signal für Wertänderungen

    def __init__(self, parent=None):
        super().__init__(parent)

        # Gitterlayout
        self.grid_layout = QGridLayout(self)

        self.mesh_point = [[None for _ in range(5)] for _ in range(5)]

        # Füllen des Gitters mit MeshPointBedLevel-Widgets
        for row in range(5):  # 5 Zeilen
            for col in range(5):  # 5 Spalten
                # Beispiel: Erstelle ein MeshPointBedLevel mit einer Beschriftung
                self.mesh_point[row][col] = MeshPointBedLevel(4-row, col, parent)
                self.mesh_point[row][col].set_head_is_positioned_here(False)

                # Füge das Widget ins Gitter ein
                self.grid_layout.addWidget(self.mesh_point[row][col], row, col)

                self.mesh_point[row][col].moveHeadToPosition.connect(self.on_move_head_to_position)
                self.mesh_point[row][col].valueChanged.connect(self.on_mesh_point_bed_level_value_changed)

        # Optional: Abstände setzen
        self.grid_layout.setSpacing(10)  # Abstand zwischen Widgets
        self.grid_layout.setContentsMargins(10, 10, 10, 10)  # Abstand zum Rand

        self.head_is_at_row = None
        self.head_is_at_col = None

    def set_value(self, row, col, value):
        """
        Setzt den Wert eines MeshPointBedLevel-Widgets im Gitter.
        :param row: Zeilenindex (0-4)
        :param col: Spaltenindex (0-4)
        :param value: Neuer Wert
        """
        widget = self.grid_layout.itemAtPosition(4-row, col).widget()
        widget.set_value(value)

    def get_value(self, row, col):
        widget = self.grid_layout.itemAtPosition(4-row, col).widget()
        return widget.get_value()

    def on_move_head_to_position(self, row, col, z):
        if self.head_is_at_row is None or self.head_is_at_col is None or self.head_is_at_row != row or self.head_is_at_col != col:
            if self.head_is_at_row is not None and self.head_is_at_col is not None:
                self.mesh_point[4-self.head_is_at_row][self.head_is_at_col].set_head_is_positioned_here(False)
            self.moveHeadToPosition.emit(row, col, z)

    def set_head_is_positioned_at(self, row, col):
        if self.head_is_at_row is not None and self.head_is_at_col is not None:
            self.mesh_point[4-self.head_is_at_row][self.head_is_at_col].set_head_is_positioned_here(False)
        self.head_is_at_row = row
        self.head_is_at_col = col
        self.mesh_point[4-row][col].set_head_is_positioned_here(True)

    def on_mesh_point_bed_level_value_changed(self, row, col, value):
        self.valueChanged.emit(row, col, value)
